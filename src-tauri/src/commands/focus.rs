use tauri::AppHandle;
use tauri::Manager;

use crate::store::focus_state::{self, FocusState, WidgetPosition};

#[tauri::command]
pub async fn get_focus_state(app: AppHandle) -> Result<FocusState, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    focus_state::load(&app_data_dir)
}

#[tauri::command]
pub async fn toggle_focus_issue(app: AppHandle, issue_key: String) -> Result<FocusState, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let mut state = focus_state::load(&app_data_dir)?;

    if let Some(pos) = state.focused_issues.iter().position(|k| k == &issue_key) {
        state.focused_issues.remove(pos);
        if state.focused_issues.is_empty() {
            state.widget_visible = false;
        }
    } else {
        state.focused_issues.push(issue_key);
        state.widget_visible = true;
    }

    focus_state::save(&app_data_dir, &state)?;

    // Notify widget
    let _ = app.emit("focus-state-updated", &state);

    Ok(state)
}

#[tauri::command]
pub async fn update_widget_position(
    app: AppHandle,
    x: f64,
    y: f64,
) -> Result<(), String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let mut state = focus_state::load(&app_data_dir)?;
    state.widget_position = Some(WidgetPosition { x, y });
    focus_state::save(&app_data_dir, &state)
}

#[tauri::command]
pub async fn set_widget_minimized(
    app: AppHandle,
    minimized: bool,
) -> Result<(), String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let mut state = focus_state::load(&app_data_dir)?;
    state.widget_minimized = minimized;
    focus_state::save(&app_data_dir, &state)?;

    let _ = app.emit("focus-state-updated", &state);
    Ok(())
}
