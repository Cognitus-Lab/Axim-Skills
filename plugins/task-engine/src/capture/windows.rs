use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use crate::events::{EventType, RawEvent};
use crate::funnel::Funnel;

#[cfg(target_os = "windows")]
use windows::Win32::UI::WindowsAndMessaging::{
    GetForegroundWindow, GetWindowTextW, GetWindowThreadProcessId,
};

#[cfg(target_os = "windows")]
pub fn start_capture(funnel: Arc<Funnel>, running: Arc<AtomicBool>, poll_interval_ms: u64) {
    let mut last_hwnd: isize = 0;

    while running.load(Ordering::Relaxed) {
        unsafe {
            let hwnd = GetForegroundWindow();
            let hwnd_val = hwnd.0 as isize;

            if hwnd_val != 0 && hwnd_val != last_hwnd {
                let mut title_buf: [u16; 512] = [0; 512];
                let len = GetWindowTextW(hwnd, &mut title_buf);

                let title = if len > 0 {
                    String::from_utf16_lossy(&title_buf[..len as usize])
                } else {
                    String::new()
                };

                let mut pid: u32 = 0;
                GetWindowThreadProcessId(hwnd, Some(&mut pid));

                let app_name = extract_app_from_title(&title);

                funnel.ingest_event(RawEvent::new(
                    EventType::WindowFocus,
                    app_name,
                    title,
                    Some(serde_json::json!({
                        "hwnd": hwnd_val,
                        "pid": pid,
                    })),
                ));

                last_hwnd = hwnd_val;
            }
        }

        thread::sleep(Duration::from_millis(poll_interval_ms));
    }
}

#[cfg(not(target_os = "windows"))]
pub fn start_capture(_funnel: Arc<Funnel>, _running: Arc<AtomicBool>, _poll_interval_ms: u64) {
    // Stub for non-Windows platforms
}

fn extract_app_from_title(title: &str) -> String {
    if let Some(pos) = title.rfind(" — ") {
        title[pos + 4..].trim().to_string()
    } else if let Some(pos) = title.rfind(" - ") {
        title[pos + 3..].trim().to_string()
    } else if !title.is_empty() {
        title.to_string()
    } else {
        "Unknown".to_string()
    }
}

