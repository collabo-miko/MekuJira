use std::sync::atomic::{AtomicBool, Ordering};

use tauri::{AppHandle, Manager, WindowEvent};

static PINNED: AtomicBool = AtomicBool::new(false);

pub fn set_pinned(pinned: bool) {
    PINNED.store(pinned, Ordering::Relaxed);
}

pub fn is_pinned() -> bool {
    PINNED.load(Ordering::Relaxed)
}

/// Windows版: ポップアップウィンドウの初期化
pub fn init_popup_panel(app: &AppHandle) {
    let window = match app.get_webview_window("popup") {
        Some(w) => w,
        None => return,
    };

    let _ = window.set_always_on_top(true);

    // フォーカスロストで自動非表示（ピン留め中はスキップ）
    // WindowsのFocused(false)は同アプリ内のウィンドウ間遷移でも発火するため、
    // 遅延後にアプリ内の他ウィンドウがフォーカスを持つか確認し、
    // アプリ外にフォーカスが移った場合のみ非表示にする。
    let handle = app.clone();
    window.on_window_event(move |event| {
        if let WindowEvent::Focused(false) = event {
            if !is_pinned() {
                let h = handle.clone();
                tauri::async_runtime::spawn(async move {
                    tokio::time::sleep(std::time::Duration::from_millis(150)).await;

                    let app_has_focus = h.webview_windows().values().any(|w| {
                        w.is_focused().unwrap_or(false)
                    });

                    if !app_has_focus {
                        if let Some(w) = h.get_webview_window("popup") {
                            let _ = w.hide();
                        }
                    }
                });
            }
        }
    });
}

/// Windows版: ポップアップの表示/非表示トグル
pub fn toggle_popup(app: &AppHandle, icon_rect: tauri::Rect) {
    let window = match app.get_webview_window("popup") {
        Some(w) => w,
        None => return,
    };

    let is_visible = window.is_visible().unwrap_or(false);

    if is_visible {
        let _ = window.hide();
    } else {
        let icon_pos = icon_rect.position.to_physical::<i32>(1.0);
        let icon_size = icon_rect.size.to_physical::<u32>(1.0);
        let win_width: i32 = window
            .outer_size()
            .map(|s| s.width as i32)
            .unwrap_or(380);
        let win_height: i32 = window
            .outer_size()
            .map(|s| s.height as i32)
            .unwrap_or(520);

        // Windowsはタスクバーが下にあるため、アイコンの上に配置
        let x = icon_pos.x + (icon_size.width as i32 / 2) - (win_width / 2);
        let y = icon_pos.y - win_height;

        let _ = window.set_position(tauri::PhysicalPosition::new(x, y));
        let _ = window.show();
        let _ = window.set_focus();
    }
}
