mod commands;
mod jira;
mod keychain;
mod store;
mod tray;

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tauri::{Emitter, Manager};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_positioner::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .invoke_handler(tauri::generate_handler![
            commands::jira::get_issues,
            commands::jira::refresh_issues,
            commands::jira::get_cached_issues,
            commands::jira::test_connection,
            commands::settings::get_settings,
            commands::settings::save_settings,
            commands::settings::save_api_token,
            commands::settings::has_api_token,
            commands::focus::get_focus_state,
            commands::focus::toggle_focus_issue,
            commands::focus::update_widget_position,
            commands::focus::set_widget_minimized,
        ])
        .setup(|app| {
            // Setup tray icon
            tray::setup_tray(app.handle())?;

            // Setup popup window: hide on focus lost
            if let Some(popup) = app.get_webview_window("popup") {
                let popup_clone = popup.clone();
                popup.on_window_event(move |event| {
                    if let tauri::WindowEvent::Focused(false) = event {
                        let _ = popup_clone.hide();
                    }
                });
            }

            // Start polling scheduler
            let app_handle = app.handle().clone();
            let stop_flag = Arc::new(AtomicBool::new(false));
            let stop_flag_clone = stop_flag.clone();

            tauri::async_runtime::spawn(async move {
                polling_loop(app_handle, stop_flag_clone).await;
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

async fn polling_loop(app: tauri::AppHandle, stop_flag: Arc<AtomicBool>) {
    loop {
        // Read polling interval from config
        let interval_secs = {
            let app_data_dir = match app.path().app_data_dir() {
                Ok(dir) => dir,
                Err(_) => {
                    tokio::time::sleep(std::time::Duration::from_secs(60)).await;
                    continue;
                }
            };
            let config = store::config::load(&app_data_dir).unwrap_or_default();
            config.polling_interval_secs.max(30)
        };

        tokio::time::sleep(std::time::Duration::from_secs(interval_secs)).await;

        if stop_flag.load(Ordering::Relaxed) {
            break;
        }

        // Fetch issues
        let app_data_dir = match app.path().app_data_dir() {
            Ok(dir) => dir,
            Err(_) => continue,
        };

        let config = match store::config::load(&app_data_dir) {
            Ok(c) => c,
            Err(_) => continue,
        };

        if config.jira.domain.is_empty() || config.jira.email.is_empty() {
            continue;
        }

        let active_filter = match config.filters.iter().find(|f| f.is_active) {
            Some(f) => f.clone(),
            None => continue,
        };

        match jira::client::search_issues(
            &config.jira.domain,
            &config.jira.email,
            &active_filter.jql,
        )
        .await
        {
            Ok(issues) => {
                let issue_cache = store::cache::IssueCache {
                    last_fetched: Some(chrono::Utc::now().to_rfc3339()),
                    filter_id: active_filter.id.clone(),
                    issues: issues.clone(),
                };
                let _ = store::cache::save(&app_data_dir, &issue_cache);
                let _ = app.emit("issues-updated", &issues);
            }
            Err(e) => {
                log::warn!("Polling failed: {}", e);
            }
        }
    }
}
