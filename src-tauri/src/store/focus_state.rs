use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FocusState {
    pub focused_issues: Vec<String>,
    pub widget_visible: bool,
    pub widget_minimized: bool,
    pub widget_position: Option<WidgetPosition>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WidgetPosition {
    pub x: f64,
    pub y: f64,
}

impl Default for FocusState {
    fn default() -> Self {
        Self {
            focused_issues: Vec::new(),
            widget_visible: false,
            widget_minimized: false,
            widget_position: None,
        }
    }
}

fn state_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("focus_state.json")
}

pub fn load(app_data_dir: &PathBuf) -> Result<FocusState, String> {
    let path = state_path(app_data_dir);
    if !path.exists() {
        return Ok(FocusState::default());
    }
    let content =
        fs::read_to_string(&path).map_err(|e| format!("Failed to read focus state: {}", e))?;
    serde_json::from_str(&content).map_err(|e| format!("Failed to parse focus state: {}", e))
}

pub fn save(app_data_dir: &PathBuf, state: &FocusState) -> Result<(), String> {
    fs::create_dir_all(app_data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    let path = state_path(app_data_dir);
    let content =
        serde_json::to_string_pretty(state).map_err(|e| format!("Failed to serialize: {}", e))?;
    fs::write(&path, content).map_err(|e| format!("Failed to write focus state: {}", e))
}
