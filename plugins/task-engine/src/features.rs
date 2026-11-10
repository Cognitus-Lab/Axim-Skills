#![allow(dead_code)]

use serde::{Deserialize, Serialize};
use crate::session::Session;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct MlSample {
    pub features: Features,
    pub labels: Labels,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Features {
    pub hour_of_day: u8,
    pub day_of_week: u8,
    pub time_since_last_switch: f32,
    pub session_duration: f32,
    pub typing_speed: f32,
    pub apps_in_rotation: u8,
    pub focus_entropy: f32,
    pub idle_ratio: f32,
    pub app_categories: [f32; 7],
    pub time_of_day_bin: u8,
    pub is_work_hours: u8,
    pub switch_frequency: f32,
    pub click_rate: f32,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Labels {
    pub next_action: String,
    pub productivity_score: f32,
    pub task_completion_probability: f32,
}

pub fn extract_features_from_session(session: &Session) -> MlSample {
    let current_time = std::time::SystemTime::now();
    let epoch_secs = current_time
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    let hour = ((epoch_secs / 3600) % 24) as u8;
    let day = (((epoch_secs / 86400) + 4) % 7) as u8; // 0 = Sunday

    let duration_minutes = (session.task_patterns.session_duration / 60.0).max(0.1);
    let switch_freq = (session.productivity_metrics.switch_count as f32) / duration_minutes;
    let click_rate = (session.user_profile.total_clicks as f32) / duration_minutes;

    let focused_time = session.productivity_metrics.focused_time;
    let idle_ratio = (1.0 - focused_time).clamp(0.0, 1.0);

    let features = Features {
        hour_of_day: hour,
        day_of_week: day,
        time_since_last_switch: 0.0,
        session_duration: session.task_patterns.session_duration,
        typing_speed: session.user_profile.typing_speed,
        apps_in_rotation: session.task_patterns.app_durations.len() as u8,
        focus_entropy: calculate_entropy(focused_time),
        idle_ratio,
        app_categories: one_hot_encode_apps(&session.task_patterns.app_sequences),
        time_of_day_bin: bin_time_of_day(hour),
        is_work_hours: if (9..=18).contains(&hour) { 1 } else { 0 },
        switch_frequency: switch_freq,
        click_rate,
    };

    let labels = Labels {
        next_action: predict_next_action(session),
        productivity_score: focused_time,
        task_completion_probability: estimate_completion_prob(session),
    };

    MlSample { features, labels }
}

fn calculate_entropy(focused_time: f32) -> f32 {
    if focused_time <= 0.001 || focused_time >= 0.999 {
        return 0.0;
    }
    let p = focused_time;
    let q = 1.0 - p;
    -(p * p.ln() + q * q.ln())
}

pub fn one_hot_encode_apps(sequences: &[(String, String)]) -> [f32; 7] {
    let mut encoded = [0.0; 7];
    for (from_app, to_app) in sequences {
        let idx1 = categorize_app(from_app) as usize;
        let idx2 = categorize_app(to_app) as usize;
        if idx1 < 7 {
            encoded[idx1] += 1.0;
        }
        if idx2 < 7 {
            encoded[idx2] += 1.0;
        }
    }
    // Normalize if any apps present
    let sum: f32 = encoded.iter().sum();
    if sum > 0.0 {
        for val in &mut encoded {
            *val /= sum;
        }
    }
    encoded
}

pub fn bin_time_of_day(hour: u8) -> u8 {
    match hour {
        5..=11 => 0,  // Morning
        12..=16 => 1, // Afternoon
        17..=21 => 2, // Evening
        _ => 3,       // Night
    }
}

pub fn predict_next_action(session: &Session) -> String {
    if let Some((_, to_app)) = session.task_patterns.app_sequences.last() {
        to_app.clone()
    } else if !session.task_patterns.current_app.is_empty() {
        session.task_patterns.current_app.clone()
    } else {
        "Idle".to_string()
    }
}

pub fn estimate_completion_prob(session: &Session) -> f32 {
    let duration_mins = session.task_patterns.session_duration / 60.0;
    let focused = session.productivity_metrics.focused_time;

    if duration_mins < 2.0 {
        0.15 * focused
    } else if duration_mins < 15.0 {
        0.50 * focused
    } else if duration_mins < 45.0 {
        0.80 * focused
    } else {
        0.95 * focused
    }
}

pub fn categorize_app(app: &str) -> u8 {
    let s = app.to_lowercase();
    if s.contains("code")
        || s.contains("visual studio")
        || s.contains("xcode")
        || s.contains("rust")
        || s.contains("intellij")
        || s.contains("pycharm")
        || s.contains("sublime")
        || s.contains("cursor")
        || s.contains("zed")
    {
        0 // CodeEditor
    } else if s.contains("chrome")
        || s.contains("firefox")
        || s.contains("safari")
        || s.contains("edge")
        || s.contains("arc")
        || s.contains("brave")
    {
        1 // Browser
    } else if s.contains("word")
        || s.contains("excel")
        || s.contains("powerpoint")
        || s.contains("notes")
        || s.contains("notion")
        || s.contains("obsidian")
        || s.contains("pages")
        || s.contains("keynote")
        || s.contains("numbers")
    {
        2 // OfficeSuite / Notes
    } else if s.contains("slack")
        || s.contains("discord")
        || s.contains("teams")
        || s.contains("zoom")
        || s.contains("telegram")
        || s.contains("signal")
        || s.contains("messages")
        || s.contains("mail")
    {
        3 // Communication
    } else if s.contains("figma")
        || s.contains("sketch")
        || s.contains("photoshop")
        || s.contains("illustrator")
        || s.contains("blender")
        || s.contains("canva")
    {
        4 // DesignTool
    } else if s.contains("terminal")
        || s.contains("iterm")
        || s.contains("alacritty")
        || s.contains("warp")
        || s.contains("kitty")
        || s.contains("zsh")
        || s.contains("bash")
        || s.contains("fish")
    {
        5 // Terminal
    } else {
        6 // Other
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_categorize_app() {
        assert_eq!(categorize_app("Visual Studio Code"), 0);
        assert_eq!(categorize_app("Google Chrome"), 1);
        assert_eq!(categorize_app("Microsoft Excel"), 2);
        assert_eq!(categorize_app("Slack"), 3);
        assert_eq!(categorize_app("Figma"), 4);
        assert_eq!(categorize_app("iTerm2"), 5);
        assert_eq!(categorize_app("Calculator"), 6);
    }

    #[test]
    fn test_feature_extraction() {
        let mut session = Session::new("test_sess".to_string());
        session.task_patterns.current_app = "Visual Studio Code".to_string();
        session.task_patterns.session_duration = 300.0;
        session.productivity_metrics.focused_time = 0.85;

        let sample = extract_features_from_session(&session);
        assert_eq!(sample.labels.productivity_score, 0.85);
        assert_eq!(sample.labels.next_action, "Visual Studio Code");
        assert!(sample.features.focus_entropy >= 0.0);
    }
}
