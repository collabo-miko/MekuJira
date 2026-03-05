use crate::tray::window;

// Windows: WebView2の制約により、WebviewWindowBuilder::build()はsyncコマンドから
// 呼ぶとデッドロックする。asyncコマンドにすることで回避。
// https://github.com/tauri-apps/wry/issues/583

#[tauri::command]
pub async fn open_settings_window(app: tauri::AppHandle) {
    window::open_settings(&app);
}

#[tauri::command]
pub async fn open_dashboard_window(app: tauri::AppHandle) {
    window::open_dashboard(&app);
}

#[tauri::command]
pub fn set_pinned(pinned: bool) {
    crate::tray::panel::set_pinned(pinned);
}

#[tauri::command]
pub fn get_pinned() -> bool {
    crate::tray::panel::is_pinned()
}
