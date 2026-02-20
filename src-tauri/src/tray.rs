use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};

pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let settings_item = MenuItem::with_id(app, "settings", "設定", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "quit", "終了", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&settings_item, &quit_item])?;

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                position,
                ..
            } = event
            {
                let app = tray.app_handle();
                show_popup(app, position);
            }
        })
        .on_menu_event(|app, event| match event.id.as_ref() {
            "settings" => {
                open_settings(app);
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .build(app)?;

    Ok(())
}

fn show_popup(app: &AppHandle, tray_position: tauri::PhysicalPosition<f64>) {
    if let Some(window) = app.get_webview_window("popup") {
        let window_width = 380.0_f64;
        let x = tray_position.x - (window_width / 2.0);
        let y = tray_position.y;
        let _ = window.set_position(tauri::PhysicalPosition::new(x as i32, y as i32));
        let _ = window.show();
        let _ = window.set_focus();
    }
}

pub fn open_settings(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("settings") {
        let _ = window.show();
        let _ = window.set_focus();
        return;
    }

    let _window = tauri::WebviewWindowBuilder::new(app, "settings", tauri::WebviewUrl::App("/settings".into()))
        .title("JIRA Focus - 設定")
        .inner_size(600.0, 500.0)
        .resizable(true)
        .build();
}
