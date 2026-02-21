mod commands;
mod jira;
mod keychain;
mod store;
mod tray;

use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tauri::{Emitter, Manager};

#[tauri::command]
fn open_settings_window(app: tauri::AppHandle) {
    tray::open_settings(&app);
}

#[tauri::command]
fn open_dashboard_window(app: tauri::AppHandle) {
    tray::open_dashboard(&app);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(tauri_nspanel::init())
        .invoke_handler(tauri::generate_handler![
            commands::jira::get_issues,
            commands::jira::refresh_issues,
            commands::jira::get_cached_issues,
            commands::jira::test_connection,
            commands::jira::get_all_filter_issues,
            commands::jira::refresh_all_filters,
            commands::bookmarks::get_bookmarks,
            commands::bookmarks::add_bookmark,
            commands::bookmarks::remove_bookmark,
            commands::bookmarks::toggle_bookmark,
            commands::settings::get_settings,
            commands::settings::save_settings,
            commands::settings::save_api_token,
            commands::settings::has_api_token,
            open_settings_window,
            open_dashboard_window,
        ])
        .setup(|app| {
            // Initialize encrypted token storage
            let app_data_dir = app
                .path()
                .app_data_dir()
                .expect("Failed to get app data dir");
            keychain::init(app_data_dir);

            // Setup tray icon
            tray::setup_tray(app.handle())?;

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

        // Fetch issues for all enabled filters
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

        let enabled_filters: Vec<_> = config.filters.iter().filter(|f| f.enabled).cloned().collect();
        if enabled_filters.is_empty() {
            continue;
        }

        // Fetch all enabled filters in parallel
        let mut handles = Vec::new();
        for filter in &enabled_filters {
            let domain = config.jira.domain.clone();
            let email = config.jira.email.clone();
            let jql = filter.jql.clone();
            let filter_id = filter.id.clone();
            handles.push(tokio::spawn(async move {
                let result = jira::client::search_issues(&domain, &email, &jql).await;
                (filter_id, result)
            }));
        }

        let mut filter_results: HashMap<String, Vec<jira::types::NormalizedIssue>> = HashMap::new();
        for handle in handles {
            match handle.await {
                Ok((filter_id, Ok(issues))) => {
                    let _ =
                        store::cache::save_filter_cache(&app_data_dir, &filter_id, issues.clone());
                    filter_results.insert(filter_id, issues);
                }
                Ok((filter_id, Err(e))) => {
                    log::warn!("Polling failed for filter {}: {}", filter_id, e);
                }
                Err(e) => {
                    log::warn!("Task join error: {}", e);
                }
            }
        }

        if !filter_results.is_empty() {
            let _ = app.emit("filter-issues-updated", &filter_results);

            // Also emit issues-updated with first filter's issues for backward compat
            if let Some(first_filter) = enabled_filters.first() {
                if let Some(issues) = filter_results.get(&first_filter.id) {
                    let issue_cache = store::cache::IssueCache {
                        last_fetched: Some(chrono::Utc::now().to_rfc3339()),
                        filter_id: first_filter.id.clone(),
                        issues: issues.clone(),
                    };
                    let _ = store::cache::save(&app_data_dir, &issue_cache);
                    let _ = app.emit("issues-updated", issues);
                }
            }
        }

        // Update bookmarks with fresh issue data
        if let Ok(mut bookmark_store) = store::bookmarks::load(&app_data_dir) {
            let mut changed = false;
            for bookmark in &mut bookmark_store.bookmarked_issues {
                for issues in filter_results.values() {
                    if let Some(fresh) = issues.iter().find(|i| i.key == bookmark.issue.key) {
                        bookmark.issue = fresh.clone();
                        changed = true;
                        break;
                    }
                }
            }
            if changed {
                let _ = store::bookmarks::save(&app_data_dir, &bookmark_store);
                let _ = app.emit("bookmarks-updated", ());
            }
        }
    }
}
