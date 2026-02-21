use tauri::{AppHandle, Manager};

#[tauri::command]
pub async fn resize_popup(app: AppHandle, mode: String) -> Result<(), String> {
    let window = app
        .get_webview_window("popup")
        .ok_or("Popup window not found")?;

    let (width, height) = match mode.as_str() {
        "tracking" => (380.0, 520.0),
        "dashboard" => (900.0, 650.0),
        _ => return Err(format!("Unknown mode: {}", mode)),
    };

    let size = tauri::LogicalSize::new(width, height);
    window
        .set_size(size)
        .map_err(|e| format!("Failed to resize: {}", e))?;

    // Adjust position to keep window on screen
    if let Ok(monitor) = window.current_monitor() {
        if let Some(monitor) = monitor {
            let monitor_size = monitor.size();
            let monitor_pos = monitor.position();
            let scale = monitor.scale_factor();

            if let Ok(pos) = window.outer_position() {
                let logical_monitor_w = monitor_size.width as f64 / scale;
                let logical_monitor_h = monitor_size.height as f64 / scale;
                let logical_monitor_x = monitor_pos.x as f64 / scale;
                let logical_monitor_y = monitor_pos.y as f64 / scale;

                let mut x = pos.x as f64 / scale;
                let mut y = pos.y as f64 / scale;

                // Ensure window doesn't go off screen
                if x + width > logical_monitor_x + logical_monitor_w {
                    x = logical_monitor_x + logical_monitor_w - width;
                }
                if x < logical_monitor_x {
                    x = logical_monitor_x;
                }
                if y + height > logical_monitor_y + logical_monitor_h {
                    y = logical_monitor_y + logical_monitor_h - height;
                }
                if y < logical_monitor_y {
                    y = logical_monitor_y;
                }

                let _ = window.set_position(tauri::LogicalPosition::new(x, y));
            }
        }
    }

    Ok(())
}
