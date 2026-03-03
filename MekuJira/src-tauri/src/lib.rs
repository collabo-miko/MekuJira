mod commands;
mod jira;
mod keychain;
mod scheduler;
mod store;
mod tray;

use objc2::MainThreadMarker;
use objc2_app_kit::{NSApplication, NSApplicationActivationPolicy};
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(tauri_nspanel::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
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
            commands::bookmarks::refresh_bookmarks,
            commands::settings::get_settings,
            commands::settings::save_settings,
            commands::settings::save_api_token,
            commands::settings::has_api_token,
            commands::window::open_settings_window,
            commands::window::open_dashboard_window,
            commands::window::set_pinned,
            commands::window::get_pinned,
        ])
        .setup(|app| {
            // Dockにアイコンを表示しない（メニューバーアプリ）
            let mtm = MainThreadMarker::new().expect("must be on the main thread");
            let ns_app = NSApplication::sharedApplication(mtm);
            ns_app.setActivationPolicy(NSApplicationActivationPolicy::Accessory);

            // 暗号化トークンストレージを初期化
            let app_data_dir = app
                .path()
                .app_data_dir()
                .expect("Failed to get app data dir");
            keychain::init(app_data_dir);

            // トレイアイコンをセットアップ
            tray::setup_tray(app.handle())?;

            // バックグラウンドポーリングを開始
            scheduler::start(app.handle().clone());

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
