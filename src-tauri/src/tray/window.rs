use tauri::{AppHandle, Manager};

/// ダッシュボードウィンドウを開く（既存なら前面に表示）
pub fn open_dashboard(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("dashboard") {
        let _ = window.show();
        let _ = window.set_focus();
        return;
    }

    let _window = tauri::WebviewWindowBuilder::new(
        app,
        "dashboard",
        tauri::WebviewUrl::App("/dashboard".into()),
    )
    .title("JIRA Focus - 対象課題一覧")
    .inner_size(900.0, 650.0)
    .resizable(true)
    .build();
}

/// 設定ウィンドウを開く（既存なら前面に表示）
pub fn open_settings(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("settings") {
        let _ = window.show();
        let _ = window.set_focus();
        return;
    }

    let _window = tauri::WebviewWindowBuilder::new(
        app,
        "settings",
        tauri::WebviewUrl::App("/settings".into()),
    )
    .title("JIRA Focus - 設定")
    .inner_size(600.0, 700.0)
    .resizable(true)
    .build();
}
