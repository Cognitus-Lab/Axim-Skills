#![allow(dead_code)]

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use serde::{Deserialize, Serialize};
use crate::events::{current_timestamp, EventType, RawEvent};

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct UserProfile {
    pub typing_speed: f32,
    pub total_keystrokes: u64,
    pub total_clicks: u64,
    pub avg_focus_duration: f32,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct TaskPatterns {
    pub session_duration: f32,
    pub current_app: String,
    pub app_sequences: Vec<(String, String)>,
    pub app_durations: HashMap<String, f32>,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct ProductivityMetrics {
    pub focused_time: f32,
    pub idle_time: f32,
    pub switch_count: u32,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Session {
    pub session_id: String,
    pub start_time: u64,
    pub last_update: u64,
    pub user_profile: UserProfile,
    pub task_patterns: TaskPatterns,
    pub productivity_metrics: ProductivityMetrics,
}

impl Session {
    pub fn new(session_id: String) -> Self {
        let now = current_timestamp();
        Self {
            session_id,
            start_time: now,
            last_update: now,
            user_profile: UserProfile::default(),
            task_patterns: TaskPatterns::default(),
            productivity_metrics: ProductivityMetrics {
                focused_time: 1.0,
                idle_time: 0.0,
                switch_count: 0,
            },
        }
    }

    pub fn update_activity(&mut self, event: &RawEvent) {
        let now = event.timestamp;
        let delta = (now.saturating_sub(self.last_update)) as f32;
        self.last_update = now;
        self.task_patterns.session_duration = (now.saturating_sub(self.start_time)) as f32;

        if !self.task_patterns.current_app.is_empty() && delta > 0.0 {
            let entry = self
                .task_patterns
                .app_durations
                .entry(self.task_patterns.current_app.clone())
                .or_insert(0.0);
            *entry += delta;
        }

        match event.event_type {
            EventType::TextInput | EventType::KeyPress => {
                self.update_typing_stats(event);
            }
            EventType::MouseClick => {
                self.user_profile.total_clicks += 1;
            }
            EventType::WindowFocus | EventType::AppSwitch => {
                self.update_task_switch(event);
            }
            EventType::Idle => {
                if let Some(data) = &event.data {
                    if let Some(idle_secs) = data.get("idle_seconds").and_then(|v| v.as_f64()) {
                        self.productivity_metrics.idle_time += idle_secs as f32;
                    }
                }
            }
            _ => {}
        }

        // Recalculate focus ratio
        let total_time = self.task_patterns.session_duration;
        if total_time > 0.0 {
            let focus = (total_time - self.productivity_metrics.idle_time).max(0.0);
            self.productivity_metrics.focused_time = (focus / total_time).clamp(0.0, 1.0);
        }
    }

    fn update_typing_stats(&mut self, event: &RawEvent) {
        self.user_profile.total_keystrokes += 1;
        if let Some(data) = &event.data {
            if let Some(wpm) = data.get("words_per_min").and_then(|v| v.as_f64()) {
                let current = self.user_profile.typing_speed;
                if current == 0.0 {
                    self.user_profile.typing_speed = wpm as f32;
                } else {
                    // Exponential moving average for typing speed
                    self.user_profile.typing_speed = current * 0.85 + (wpm as f32) * 0.15;
                }
            }
        }
    }

    fn update_task_switch(&mut self, event: &RawEvent) {
        let from_app = self.task_patterns.current_app.clone();
        let to_app = event.app_name.clone();

        if from_app != to_app && !to_app.is_empty() {
            if !from_app.is_empty() {
                self.task_patterns.app_sequences.push((from_app, to_app.clone()));
                self.productivity_metrics.switch_count += 1;
            }
            self.task_patterns.current_app = to_app;
        }
    }
}

pub struct SessionManager {
    sessions: HashMap<String, Session>,
    current_session_id: Option<String>,
    session_counter: AtomicU64,
    last_activity: HashMap<String, u64>,
    last_global_activity: u64,
    idle_threshold: u64, // Threshold in seconds to fork a new session
}

impl SessionManager {
    pub fn new() -> Self {
        Self::with_idle_threshold(300) // Default 5 minutes
    }

    pub fn with_idle_threshold(threshold_secs: u64) -> Self {
        let now = current_timestamp();
        Self {
            sessions: HashMap::new(),
            current_session_id: None,
            session_counter: AtomicU64::new(1),
            last_activity: HashMap::new(),
            last_global_activity: now,
            idle_threshold: threshold_secs,
        }
    }

    pub fn update_activity(&mut self, event: &RawEvent) {
        let timestamp = event.timestamp;
        let app = event.app_name.clone();

        // Check global idle threshold across the workstation
        let should_new_session = if self.last_global_activity > 0 {
            timestamp.saturating_sub(self.last_global_activity) > self.idle_threshold
        } else {
            true
        };

        if should_new_session || self.current_session_id.is_none() {
            let new_id = self.create_new_session();
            self.current_session_id = Some(new_id);
        }

        self.last_global_activity = timestamp;
        self.last_activity.insert(app, timestamp);

        if let Some(session_id) = &self.current_session_id {
            if let Some(session) = self.sessions.get_mut(session_id) {
                session.update_activity(event);
            }
        }
    }

    fn create_new_session(&mut self) -> String {
        let counter = self.session_counter.fetch_add(1, Ordering::Relaxed);
        let session_id = format!("sess_{:06}", counter);
        let session = Session::new(session_id.clone());
        self.sessions.insert(session_id.clone(), session);
        session_id
    }

    pub fn get_current_session(&self) -> Option<Session> {
        self.current_session_id
            .as_ref()
            .and_then(|id| self.sessions.get(id).cloned())
    }

    pub fn get_all_sessions(&self) -> Vec<Session> {
        self.sessions.values().cloned().collect()
    }

    pub fn active_session_count(&self) -> usize {
        self.sessions.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_lifecycle() {
        let mut sm = SessionManager::with_idle_threshold(10);
        let evt1 = RawEvent::new(EventType::WindowFocus, "Code", "main.rs", None);
        sm.update_activity(&evt1);

        assert_eq!(sm.active_session_count(), 1);
        let session = sm.get_current_session().expect("Expected active session");
        assert_eq!(session.task_patterns.current_app, "Code");

        // App switch
        let evt2 = RawEvent::new(EventType::AppSwitch, "Chrome", "GitHub", None);
        sm.update_activity(&evt2);
        let updated = sm.get_current_session().expect("Expected active session");
        assert_eq!(updated.task_patterns.current_app, "Chrome");
        assert_eq!(updated.task_patterns.app_sequences.len(), 1);
        assert_eq!(updated.productivity_metrics.switch_count, 1);
    }
}
