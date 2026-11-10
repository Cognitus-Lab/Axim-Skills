#![allow(dead_code)]

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::Mutex;
use serde::{Deserialize, Serialize};

use crate::events::current_timestamp;
use crate::features::MlSample;
use crate::session::Session;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Metadata {
    pub version: u8,
    pub timestamp: u64,
    pub platform: String,
    pub engine_version: String,
    pub arch: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SessionSummary {
    pub session_id: String,
    pub duration_secs: f32,
    pub current_app: String,
    pub focused_time: f32,
    pub idle_time: f32,
    pub switches: u32,
    pub typing_speed: f32,
    pub total_clicks: u64,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct UnifiedTaskRecord {
    pub metadata: Metadata,
    pub session: SessionSummary,
    pub ml_sample: MlSample,
}

pub struct OutputWriter {
    jsonl_path: String,
    csv_path: Option<String>,
    jsonl_writer: Mutex<Option<BufWriter<std::fs::File>>>,
}

impl OutputWriter {
    pub fn new(jsonl_path: &str) -> Self {
        Self::with_csv(jsonl_path, None)
    }

    pub fn with_csv(jsonl_path: &str, csv_path: Option<&str>) -> Self {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(jsonl_path)
            .ok()
            .map(BufWriter::new);

        // If CSV is requested, initialize headers if file is empty
        if let Some(csv_p) = csv_path {
            if let Ok(file_meta) = std::fs::metadata(csv_p) {
                if file_meta.len() == 0 {
                    let _ = Self::write_csv_header(csv_p);
                }
            } else {
                let _ = Self::write_csv_header(csv_p);
            }
        }

        Self {
            jsonl_path: jsonl_path.to_string(),
            csv_path: csv_path.map(|s| s.to_string()),
            jsonl_writer: Mutex::new(file),
        }
    }

    fn write_csv_header(csv_path: &str) -> std::io::Result<()> {
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(csv_path)?;
        writeln!(
            file,
            "timestamp,session_id,app,duration,focus_ratio,entropy,hour,day,typing_wpm,clicks,next_action,productivity_score,completion_prob"
        )?;
        file.flush()
    }

    pub fn write_record(&self, record: &UnifiedTaskRecord) {
        // 1. Write JSON Lines
        if let Ok(json_line) = serde_json::to_string(record) {
            if let Ok(mut guard) = self.jsonl_writer.lock() {
                if let Some(writer) = guard.as_mut() {
                    let _ = writeln!(writer, "{}", json_line);
                    let _ = writer.flush();
                } else if let Ok(mut f) = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&self.jsonl_path)
                {
                    let _ = writeln!(f, "{}", json_line);
                    let _ = f.flush();
                }
            }
        }

        // 2. Write CSV if configured
        if let Some(csv_p) = &self.csv_path {
            if let Ok(mut f) = OpenOptions::new().append(true).open(csv_p) {
                let s = &record.session;
                let m = &record.ml_sample;
                let _ = writeln!(
                    f,
                    "{},{},{},{:.2},{:.4},{:.4},{},{},{:.2},{},{},{:.4},{:.4}",
                    record.metadata.timestamp,
                    s.session_id,
                    s.current_app.replace(',', " "),
                    s.duration_secs,
                    s.focused_time,
                    m.features.focus_entropy,
                    m.features.hour_of_day,
                    m.features.day_of_week,
                    s.typing_speed,
                    s.total_clicks,
                    m.labels.next_action.replace(',', " "),
                    m.labels.productivity_score,
                    m.labels.task_completion_probability
                );
                let _ = f.flush();
            }
        }
    }

    pub fn write_batch(&self, records: &[UnifiedTaskRecord]) {
        for record in records {
            self.write_record(record);
        }
    }
}

pub fn create_unified_record(session: &Session, ml_sample: &MlSample) -> UnifiedTaskRecord {
    let metadata = Metadata {
        version: 1,
        timestamp: current_timestamp(),
        platform: std::env::consts::OS.to_string(),
        engine_version: env!("CARGO_PKG_VERSION").to_string(),
        arch: std::env::consts::ARCH.to_string(),
    };

    let summary = SessionSummary {
        session_id: session.session_id.clone(),
        duration_secs: session.task_patterns.session_duration,
        current_app: session.task_patterns.current_app.clone(),
        focused_time: session.productivity_metrics.focused_time,
        idle_time: session.productivity_metrics.idle_time,
        switches: session.productivity_metrics.switch_count,
        typing_speed: session.user_profile.typing_speed,
        total_clicks: session.user_profile.total_clicks,
    };

    UnifiedTaskRecord {
        metadata,
        session: summary,
        ml_sample: ml_sample.clone(),
    }
}
