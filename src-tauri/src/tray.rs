use std::ptr::NonNull;

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};
use tauri_nspanel::{
    objc2, tauri_panel, CollectionBehavior, ManagerExt, NSPoint, NSRect, NSSize, PanelLevel,
    StyleMask, WebviewWindowExt,
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
    let dashboard_item =
        MenuItem::with_id(app, "dashboard", "対象課題一覧", true, None::<&str>)?;
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
                rect,
                ..
            } = event
            {
                let app = tray.app_handle();
                show_popup(app, rect);
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

    // window_did_resign_key: テキスト入力等でkey windowになった後のケースをカバー
    let handler = PopupEventHandler::new();
    let handle = app.clone();
    handler.window_did_resign_key(move |_notification| {
        if let Ok(p) = handle.get_webview_panel("popup") {
            p.hide();
        }
    });
    panel.set_event_handler(Some(handler.as_ref()));

    // NSEventグローバルモニタ: パネル外クリックでパネルを閉じる
    setup_global_mouse_monitor(app);

    // NSWorkspace通知: 他のアプリがアクティブになったらパネルを閉じる
    setup_workspace_listener(app);
}

fn show_popup(app: &AppHandle, icon_rect: tauri::Rect) {
    let panel = match app.get_webview_panel("popup") {
        Ok(p) => p,
        Err(_) => return,
    };
    let window = match app.get_webview_window("popup") {
        Some(w) => w,
        None => return,
    };

    // ウィンドウサイズ取得
    let win_size = window
        .outer_size()
        .unwrap_or(tauri::PhysicalSize::new(380, 520));

    // スケールファクター取得
    let scale_factor = window.scale_factor().unwrap_or(1.0);

    // Logical座標に変換
    let icon_x = icon_rect.position.x / scale_factor;
    let icon_y = icon_rect.position.y / scale_factor;
    let icon_w = icon_rect.size.width / scale_factor;
    let win_w = win_size.width as f64 / scale_factor;
    let win_h = win_size.height as f64 / scale_factor;

    // macOS座標系（左下原点）: アイコン中央の真下にポップアップを配置
    let x = icon_x + (icon_w / 2.0) - (win_w / 2.0);
    let y = icon_y - win_h;

    // NSWindowのsetFrame:display:で直接位置設定（macOS座標系）
    unsafe {
        let ns_window: *mut tauri_nspanel::NSObject = window.ns_window().unwrap() as _;
        let frame = NSRect::new(NSPoint::new(x, y), NSSize::new(win_w, win_h));
        let _: () = objc2::msg_send![ns_window, setFrame: frame display: false];
    }

    panel.show();
}

/// NSEventグローバルモニタ: アプリ外のマウスクリックでパネルを閉じる
fn setup_global_mouse_monitor(app: &AppHandle) {
    use objc2_app_kit::{NSEvent, NSEventMask};

    let handle = app.clone();

    let mask = NSEventMask::LeftMouseDown.union(NSEventMask::RightMouseDown);

    let block =
        block2::RcBlock::new(move |_event: NonNull<NSEvent>| {
            if let Ok(panel) = handle.get_webview_panel("popup") {
                if panel.is_visible() {
                    panel.hide();
                }
            }
        });

    unsafe {
        let _monitor =
            NSEvent::addGlobalMonitorForEventsMatchingMask_handler(mask, &block);
        // モニタの所有権を維持するためリーク（アプリ全体のライフタイム）
        if let Some(monitor) = _monitor {
            std::mem::forget(monitor);
        }
    }

    // blockの所有権も維持
    std::mem::forget(block);
}

/// NSWorkspace通知: 他のアプリがアクティブになったらパネルを閉じる
fn setup_workspace_listener(app: &AppHandle) {
    use objc2_app_kit::NSWorkspace;
    use objc2_foundation::{NSNotification, NSString};

    let handle = app.clone();

    let block =
        block2::RcBlock::new(move |_notif: NonNull<NSNotification>| {
            if let Ok(panel) = handle.get_webview_panel("popup") {
                if panel.is_visible() {
                    panel.hide();
                }
            }
        });

    unsafe {
        let workspace = NSWorkspace::sharedWorkspace();
        let notification_center = workspace.notificationCenter();
        let name = NSString::from_str("NSWorkspaceDidActivateApplicationNotification");

        let observer = notification_center
            .addObserverForName_object_queue_usingBlock(Some(&name), None, None, &block);

        // observerの所有権を維持するためリーク
        std::mem::forget(observer);
    }

    // blockの所有権も維持
    std::mem::forget(block);
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
