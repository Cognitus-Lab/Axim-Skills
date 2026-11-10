#![allow(dead_code)]

use serde::{Deserialize, Serialize};
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

/// High-level categorization of events captured from the OS
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub enum EventType {
    WindowFocus,
    TextInput,
    KeyPress,
    MouseClick,
    FileSave,
    Commit,
    Idle,
    AppSwitch,
}

impl fmt::Display for EventType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EventType::WindowFocus => write!(f, "WindowFocus"),
            EventType::TextInput => write!(f, "TextInput"),
            EventType::KeyPress => write!(f, "KeyPress"),
            EventType::MouseClick => write!(f, "MouseClick"),
            EventType::FileSave => write!(f, "FileSave"),
            EventType::Commit => write!(f, "Commit"),
            EventType::Idle => write!(f, "Idle"),
            EventType::AppSwitch => write!(f, "AppSwitch"),
        }
    }
}

/// Raw event emitted by platform-specific hooks
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct RawEvent {
    pub timestamp: u64,
    pub event_type: EventType,
    pub app_name: String,
    pub window_title: String,
    pub data: Option<serde_json::Value>,
}

impl RawEvent {
    pub fn new(
        event_type: EventType,
        app_name: impl Into<String>,
        window_title: impl Into<String>,
        data: Option<serde_json::Value>,
    ) -> Self {
        Self {
            timestamp: current_timestamp(),
            event_type,
            app_name: app_name.into(),
            window_title: window_title.into(),
            data,
        }
    }
}

/// Helper function to retrieve the current Unix timestamp in seconds
pub fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

/// Helper function to retrieve high-resolution millisecond timestamp
pub fn current_timestamp_millis() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_raw_event_serialization() {
        let evt = RawEvent::new(
            EventType::WindowFocus,
            "Code",
            "task_engine - main.rs",
            Some(serde_json::json!({"test": true})),
        );
        let serialized = serde_json::to_string(&evt).expect("Failed to serialize event");
        assert!(serialized.contains("WindowFocus"));
        assert!(serialized.contains("Code"));

        let deserialized: RawEvent =
            serde_json::from_str(&serialized).expect("Failed to deserialize event");
        assert_eq!(deserialized.event_type, EventType::WindowFocus);
        assert_eq!(deserialized.app_name, "Code");
    }
}
