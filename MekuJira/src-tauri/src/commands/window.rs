use crate::tray::window;

#[tauri::command]
pub fn open_settings_window(app: tauri::AppHandle) {
    window::open_settings(&app);
}

#[tauri::command]
pub fn open_dashboard_window(app: tauri::AppHandle) {
    window::open_dashboard(&app);
}
