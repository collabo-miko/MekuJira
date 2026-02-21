use tauri::{AppHandle, Manager};

/// Open settings window (or focus if already open)
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
    .title("Menubar Template - Settings")
    .inner_size(600.0, 500.0)
    .resizable(true)
    .build();
}
