use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};
use tauri_nspanel::{
    tauri_panel, CollectionBehavior, ManagerExt, PanelLevel, StyleMask, WebviewWindowExt,
};

tauri_panel! {
    panel!(PopupPanel {
        config: {
            can_become_key_window: true,
            is_floating_panel: true
        }
    })

    panel_event!(PopupEventHandler {
        window_did_resign_key(notification: &NSNotification) -> ()
    })
}

pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let dashboard_item = MenuItem::with_id(app, "dashboard", "対象課題一覧", true, None::<&str>)?;
    let settings_item = MenuItem::with_id(app, "settings", "設定", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "quit", "終了", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&dashboard_item, &settings_item, &quit_item])?;

    // ポップアップウィンドウをNSPanel化
    init_popup_panel(app);

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .icon_as_template(true)
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
            "dashboard" => {
                open_dashboard(app);
            }
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

fn init_popup_panel(app: &AppHandle) {
    let window = match app.get_webview_window("popup") {
        Some(w) => w,
        None => return,
    };

    let panel = match window.to_panel::<PopupPanel>() {
        Ok(p) => p,
        Err(_) => return,
    };

    // フルスクリーンでも表示される設定
    panel.set_level(PanelLevel::PopUpMenu.value());
    panel.set_style_mask(StyleMask::empty().nonactivating_panel().into());
    panel.set_collection_behavior(
        CollectionBehavior::new()
            .full_screen_auxiliary()
            .can_join_all_spaces()
            .into(),
    );

    // フォーカス外で自動クローズ
    let handler = PopupEventHandler::new();
    let handle = app.clone();
    handler.window_did_resign_key(move |_notification| {
        if let Ok(p) = handle.get_webview_panel("popup") {
            p.hide();
        }
    });
    panel.set_event_handler(Some(handler.as_ref()));
}

fn show_popup(app: &AppHandle, tray_position: tauri::PhysicalPosition<f64>) {
    if let Ok(panel) = app.get_webview_panel("popup") {
        // Get window size for centering
        if let Some(window) = app.get_webview_window("popup") {
            let window_width = window
                .outer_size()
                .map(|s| s.width as f64)
                .unwrap_or(380.0);
            let x = tray_position.x - (window_width / 2.0);
            let y = tray_position.y;
            let _ = window.set_position(tauri::PhysicalPosition::new(x as i32, y as i32));
        }
        panel.show();
    }
}

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
