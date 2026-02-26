pub(crate) mod panel;
pub mod window;

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle,
};

/// トレイアイコンとメニューをセットアップ
pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let dashboard_item =
        MenuItem::with_id(app, "dashboard", "対象課題一覧", true, None::<&str>)?;
    let settings_item = MenuItem::with_id(app, "settings", "設定", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "quit", "終了", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&dashboard_item, &settings_item, &quit_item])?;

    // ポップアップウィンドウをNSPanel化
    panel::init_popup_panel(app);

    TrayIconBuilder::with_id("main")
        .icon(app.default_window_icon().unwrap().clone())
        .icon_as_template(true)
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                rect,
                ..
            } = event
            {
                let app = tray.app_handle();
                panel::toggle_popup(app, rect);
            }
        })
        .on_menu_event(|app, event| match event.id.as_ref() {
            "dashboard" => {
                window::open_dashboard(app);
            }
            "settings" => {
                window::open_settings(app);
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .build(app)?;

    Ok(())
}
