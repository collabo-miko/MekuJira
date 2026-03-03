use std::ptr::NonNull;
use std::sync::atomic::{AtomicBool, Ordering};

use tauri::{AppHandle, Manager};
use tauri_nspanel::{
    tauri_panel, CollectionBehavior, ManagerExt, PanelLevel, StyleMask, WebviewWindowExt,
};

static PINNED: AtomicBool = AtomicBool::new(false);

pub fn set_pinned(pinned: bool) {
    PINNED.store(pinned, Ordering::Relaxed);
}

pub fn is_pinned() -> bool {
    PINNED.load(Ordering::Relaxed)
}

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

/// ポップアップウィンドウをNSPanelに変換し、フルスクリーン表示と自動クローズを設定
pub fn init_popup_panel(app: &AppHandle) {
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
        if !is_pinned() {
            if let Ok(p) = handle.get_webview_panel("popup") {
                p.hide();
                set_tray_icon_template(&handle, true);
            }
        }
    });
    panel.set_event_handler(Some(handler.as_ref()));

    // NSEventグローバルモニタ: パネル外クリックでパネルを閉じる
    setup_global_mouse_monitor(app);

    // NSWorkspace通知: 他のアプリがアクティブになったらパネルを閉じる
    setup_workspace_listener(app);
}

/// トレイアイコンのrect情報に基づいてポップアップを表示/非表示をトグル
pub fn toggle_popup(app: &AppHandle, icon_rect: tauri::Rect) {
    let panel = match app.get_webview_panel("popup") {
        Ok(p) => p,
        Err(_) => return,
    };

    if panel.is_visible() {
        // 表示中 → 非表示 + アイコンをモノクロに
        panel.hide();
        set_tray_icon_template(app, true);
    } else {
        // 非表示 → 表示 + アイコンをカラーに
        let window = match app.get_webview_window("popup") {
            Some(w) => w,
            None => return,
        };

        // Physical座標を取得（TrayIconEventのrectはPhysical座標）
        let icon_pos = icon_rect.position.to_physical::<i32>(1.0);
        let icon_size = icon_rect.size.to_physical::<u32>(1.0);
        let win_width: i32 = window
            .outer_size()
            .map(|s| s.width as i32)
            .unwrap_or(380);

        // アイコン中央の真下に配置（Physical座標）
        let x = icon_pos.x + (icon_size.width as i32 / 2) - (win_width / 2);
        let y = icon_pos.y + icon_size.height as i32;

        let _ = window.set_position(tauri::PhysicalPosition::new(x, y));
        panel.show();
        panel.make_key_and_order_front();
        set_tray_icon_template(app, false);
    }
}

/// トレイアイコンのtemplate表示を切り替え
fn set_tray_icon_template(app: &AppHandle, is_template: bool) {
    if let Some(tray) = app.tray_by_id("main") {
        let _ = tray.set_icon_as_template(is_template);
    }
}

/// NSEventグローバルモニタ: アプリ外のマウスクリックでパネルを閉じる
fn setup_global_mouse_monitor(app: &AppHandle) {
    use objc2_app_kit::{NSEvent, NSEventMask};

    let handle = app.clone();

    let mask = NSEventMask::LeftMouseDown.union(NSEventMask::RightMouseDown);

    let block = block2::RcBlock::new(move |_event: NonNull<NSEvent>| {
        if let Ok(panel) = handle.get_webview_panel("popup") {
            if panel.is_visible() && !is_pinned() {
                panel.hide();
                set_tray_icon_template(&handle, true);
            }
        }
    });

    let _monitor =
        unsafe { NSEvent::addGlobalMonitorForEventsMatchingMask_handler(mask, &block) };
    // モニタの所有権を維持するためリーク（アプリ全体のライフタイム）
    if let Some(monitor) = _monitor {
        std::mem::forget(monitor);
    }

    // blockの所有権も維持
    std::mem::forget(block);
}

/// NSWorkspace通知: 他のアプリがアクティブになったらパネルを閉じる
fn setup_workspace_listener(app: &AppHandle) {
    use objc2_app_kit::NSWorkspace;
    use objc2_foundation::{NSNotification, NSString};

    let handle = app.clone();

    let block = block2::RcBlock::new(move |_notif: NonNull<NSNotification>| {
        if let Ok(panel) = handle.get_webview_panel("popup") {
            if panel.is_visible() && !is_pinned() {
                panel.hide();
                set_tray_icon_template(&handle, true);
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
