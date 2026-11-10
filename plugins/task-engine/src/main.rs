mod capture;
mod events;
mod features;
mod funnel;
mod output;
mod session;

use std::env;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use funnel::Funnel;

const BANNER: &str = r#"
================================================================================
⚡ TASK_ENGINE: Portable Workstation Task & Activity ML Funnel
================================================================================
  Target Architecture : Low-Overhead Native OS Activity Telemetry
  Dataset Target      : Streamable JSONL / CSV for Neural Network Training
  Active Platform     : Native Cross-Platform OS Hooks
================================================================================
"#;

struct Config {
    output_jsonl: String,
    output_csv: Option<String>,
    poll_interval_ms: u64,
}

fn parse_args() -> Config {
    let args: Vec<String> = env::args().collect();
    let mut output_jsonl = "tasks_ml_dataset.jsonl".to_string();
    let mut output_csv = None;
    let mut poll_interval_ms = 500u64;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--output" | "-o" => {
                if i + 1 < args.len() {
                    output_jsonl = args[i + 1].clone();
                    i += 1;
                }
            }
            "--csv" => {
                if i + 1 < args.len() {
                    output_csv = Some(args[i + 1].clone());
                    i += 1;
                }
            }
            "--interval" | "-i" => {
                if i + 1 < args.len() {
                    if let Ok(val) = args[i + 1].parse::<u64>() {
                        poll_interval_ms = val;
                    }
                    i += 1;
                }
            }
            "--help" | "-h" => {
                println!("{}", BANNER);
                println!("USAGE:");
                println!("  task_engine [OPTIONS]");
                println!();
                println!("OPTIONS:");
                println!("  -o, --output <FILE>   Path to output JSONL dataset (default: tasks_ml_dataset.jsonl)");
                println!("      --csv <FILE>      Enable dual CSV dataset stream (default: disabled)");
                println!("  -i, --interval <MS>   Hook polling interval in milliseconds (default: 500)");
                println!("  -h, --help            Show this help dialog");
                std::process::exit(0);
            }
            _ => {}
        }
        i += 1;
    }

    Config {
        output_jsonl,
        output_csv,
        poll_interval_ms,
    }
}

fn main() {
    println!("{}", BANNER);
    let config = parse_args();

    println!("  [+] Output Dataset (JSONL) : {}", config.output_jsonl);
    if let Some(csv_p) = &config.output_csv {
        println!("  [+] Output Dataset (CSV)   : {}", csv_p);
    }
    println!("  [+] Polling Interval       : {} ms", config.poll_interval_ms);
    println!("  [+] Platform               : {}", env::consts::OS);
    println!("--------------------------------------------------------------------------------");

    let funnel = Arc::new(Funnel::with_csv(
        &config.output_jsonl,
        config.output_csv.as_deref(),
    ));
    let running = Arc::new(AtomicBool::new(true));

    // Handle Ctrl+C for clean shutdown
    let r_sig = running.clone();
    let f_sig = funnel.clone();
    ctrlc_handler(r_sig, f_sig);

    // 1. Launch Platform Capture Thread
    let f_cap = funnel.clone();
    let r_cap = running.clone();
    let poll_interval = config.poll_interval_ms;
    let cap_handle = thread::spawn(move || {
        #[cfg(target_os = "macos")]
        capture::macos::start_capture(f_cap, r_cap, poll_interval);

        #[cfg(target_os = "windows")]
        capture::windows::start_capture(f_cap, r_cap, poll_interval);

        #[cfg(target_os = "linux")]
        capture::linux::start_capture(f_cap, r_cap, poll_interval);
    });

    // 2. Launch Background ML Dataset Funnel Processor
    let f_proc = funnel.clone();
    let r_proc = running.clone();
    let proc_handle = thread::spawn(move || {
        while r_proc.load(Ordering::Relaxed) {
            f_proc.process_events();
            thread::sleep(Duration::from_millis(200));
        }
        // Final flush on exit
        f_proc.process_events();
    });

    // 3. Telemetry Monitor Loop
    let mut tick = 0u64;
    while running.load(Ordering::Relaxed) {
        thread::sleep(Duration::from_secs(3));
        tick += 1;
        let (total_evts, total_samples) = funnel.stats();
        let active_sessions = funnel
            .session_manager
            .lock()
            .map(|sm| sm.active_session_count())
            .unwrap_or(0);

        let current_app = funnel
            .session_manager
            .lock()
            .ok()
            .and_then(|sm| sm.get_current_session())
            .map(|s| s.task_patterns.current_app)
            .unwrap_or_else(|| "Idle".to_string());

        println!(
            "[Tick #{:04}] App: {:<16} | Raw Events: {:>5} | ML Samples: {:>5} | Active Sessions: {}",
            tick, current_app, total_evts, total_samples, active_sessions
        );
    }

    let _ = cap_handle.join();
    let _ = proc_handle.join();

    let (final_evts, final_samples) = funnel.stats();
    println!("--------------------------------------------------------------------------------");
    println!("✅ TASK_ENGINE Gracefully Stopped.");
    println!("   Total Raw OS Events Processed: {}", final_evts);
    println!("   Total ML Samples Streamed    : {}", final_samples);
    println!("   Dataset Path                 : {}", config.output_jsonl);
    println!("================================================================================");
}

fn ctrlc_handler(running: Arc<AtomicBool>, funnel: Arc<Funnel>) {
    // Standard signal handler without external crate dependencies
    #[cfg(unix)]
    {
        extern "C" fn handle_sigint(_: i32) {
            // Signal received
            SHUTDOWN_SIGNAL.store(true, Ordering::Relaxed);
        }
        static SHUTDOWN_SIGNAL: AtomicBool = AtomicBool::new(false);

        unsafe {
            libc::signal(libc::SIGINT, handle_sigint as *const () as usize);
            libc::signal(libc::SIGTERM, handle_sigint as *const () as usize);
        }

        let r_clone = running.clone();
        let f_clone = funnel.clone();
        thread::spawn(move || loop {
            if SHUTDOWN_SIGNAL.load(Ordering::Relaxed) {
                println!("\n[*] Intercepted termination signal. Flushing buffers...");
                r_clone.store(false, Ordering::Relaxed);
                f_clone.process_events();
                break;
            }
            thread::sleep(Duration::from_millis(100));
        });
    }

    #[cfg(not(unix))]
    {
        // On non-Unix, main loop runs until external flag or process kill
        let _ = (running, funnel);
    }
}
