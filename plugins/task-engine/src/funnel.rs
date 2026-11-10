#![allow(dead_code)]

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use crate::events::RawEvent;
use crate::features::extract_features_from_session;
use crate::output::{create_unified_record, OutputWriter};
use crate::session::SessionManager;

pub struct Funnel {
    pub events: Mutex<Vec<RawEvent>>,
    pub session_manager: Mutex<SessionManager>,
    pub output: OutputWriter,
    pub total_events: AtomicU64,
    pub total_samples: AtomicU64,
}

impl Funnel {
    pub fn new(output_jsonl: &str) -> Self {
        Self::with_csv(output_jsonl, None)
    }

    pub fn with_csv(output_jsonl: &str, output_csv: Option<&str>) -> Self {
        Self {
            events: Mutex::new(Vec::new()),
            session_manager: Mutex::new(SessionManager::new()),
            output: OutputWriter::with_csv(output_jsonl, output_csv),
            total_events: AtomicU64::new(0),
            total_samples: AtomicU64::new(0),
        }
    }

    /// Non-blocking ingestion of raw OS events
    pub fn ingest_event(&self, event: RawEvent) {
        if let Ok(mut evts) = self.events.lock() {
            evts.push(event);
            self.total_events.fetch_add(1, Ordering::Relaxed);
        }
    }

    /// Background worker function to normalize events, update active sessions,
    /// extract ML feature matrices, and stream unified training records.
    pub fn process_events(&self) {
        let events: Vec<RawEvent> = match self.events.lock() {
            Ok(mut evts) => evts.drain(..).collect(),
            Err(_) => return,
        };

        if events.is_empty() {
            return;
        }

        if let Ok(mut sm) = self.session_manager.lock() {
            for event in &events {
                sm.update_activity(event);
            }

            if let Some(session) = sm.get_current_session() {
                let ml_sample = extract_features_from_session(&session);
                let record = create_unified_record(&session, &ml_sample);
                self.output.write_record(&record);
                self.total_samples.fetch_add(1, Ordering::Relaxed);
            }
        }
    }

    pub fn stats(&self) -> (u64, u64) {
        (
            self.total_events.load(Ordering::Relaxed),
            self.total_samples.load(Ordering::Relaxed),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::events::EventType;

    #[test]
    fn test_funnel_pipeline() {
        let test_file = "/tmp/test_funnel_output.jsonl";
        let _ = std::fs::remove_file(test_file);

        let funnel = Funnel::new(test_file);
        funnel.ingest_event(RawEvent::new(
            EventType::WindowFocus,
            "Code",
            "funnel.rs",
            None,
        ));
        funnel.ingest_event(RawEvent::new(
            EventType::TextInput,
            "Code",
            "funnel.rs",
            Some(serde_json::json!({"words_per_min": 72.0})),
        ));

        let (evts, _) = funnel.stats();
        assert_eq!(evts, 2);

        funnel.process_events();
        let (_, samples) = funnel.stats();
        assert_eq!(samples, 1);

        assert!(std::path::Path::new(test_file).exists());
        let _ = std::fs::remove_file(test_file);
    }
}
