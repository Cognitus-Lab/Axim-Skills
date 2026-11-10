use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use crate::events::{EventType, RawEvent};
use crate::funnel::Funnel;

#[cfg(target_os = "linux")]
use x11::xlib;

#[cfg(target_os = "linux")]
pub fn start_capture(funnel: Arc<Funnel>, running: Arc<AtomicBool>, poll_interval_ms: u64) {
    unsafe {
        let display = xlib::XOpenDisplay(std::ptr::null_mut());
        if display.is_null() {
            eprintln!("[Linux] Failed to open X11 Display. Wayland or headless mode active.");
            return;
        }

        let mut last_window: xlib::Window = 0;

        while running.load(Ordering::Relaxed) {
            let mut focused_window: xlib::Window = 0;
            let mut revert_to: i32 = 0;

            xlib::XGetInputFocus(display, &mut focused_window, &mut revert_to);

            if focused_window != 0 && focused_window != last_window {
                let window_title = get_x11_window_title(display, focused_window);
                let (app_name, title) = parse_x11_title(&window_title);

                funnel.ingest_event(RawEvent::new(
                    EventType::WindowFocus,
                    app_name,
                    title,
                    Some(serde_json::json!({
                        "x11_window_id": focused_window,
                    })),
                ));

                last_window = focused_window;
            }

            thread::sleep(Duration::from_millis(poll_interval_ms));
        }

        xlib::XCloseDisplay(display);
    }
}

#[cfg(not(target_os = "linux"))]
pub fn start_capture(_funnel: Arc<Funnel>, _running: Arc<AtomicBool>, _poll_interval_ms: u64) {
    // Stub for non-Linux platforms
}

#[cfg(target_os = "linux")]
unsafe fn get_x11_window_title(display: *mut xlib::Display, window: xlib::Window) -> String {
    let mut name: xlib::XTextProperty = std::mem::zeroed();
    let status = xlib::XGetTextProperty(display, window, &mut name, xlib::XA_WM_NAME);

    if status != 0 && !name.value.is_null() {
        let mut text_list: *mut *mut std::os::raw::c_char = std::ptr::null_mut();
        let mut count: i32 = 0;
        let conv_status = xlib::XTextPropertyToStringList(&mut name, &mut text_list, &mut count);

        if conv_status != 0 && count > 0 && !text_list.is_null() {
            let first_str = *text_list;
            if !first_str.is_null() {
                let title = std::ffi::CStr::from_ptr(first_str)
                    .to_string_lossy()
                    .into_owned();
                xlib::XFreeStringList(text_list);
                xlib::XFree(name.value as *mut _);
                return title;
            }
        }
        xlib::XFree(name.value as *mut _);
    }

    "Desktop".to_string()
}

#[cfg(target_os = "linux")]
fn parse_x11_title(title: &str) -> (String, String) {
    if let Some(pos) = title.rfind(" — ") {
        (title[pos + 4..].trim().to_string(), title.to_string())
    } else if let Some(pos) = title.rfind(" - ") {
        (title[pos + 3..].trim().to_string(), title.to_string())
    } else {
        (title.to_string(), title.to_string())
    }
}
