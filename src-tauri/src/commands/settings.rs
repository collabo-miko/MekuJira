use tauri::AppHandle;
use tauri::Manager;

use crate::keychain;
use crate::store::config::{self, AppConfig};

#[tauri::command]
pub async fn get_settings(app: AppHandle) -> Result<AppConfig, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    config::load(&app_data_dir)
}

#[tauri::command]
pub async fn save_settings(app: AppHandle, settings: AppConfig) -> Result<(), String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    config::save(&app_data_dir, &settings)
}

#[tauri::command]
pub async fn save_api_token(token: String) -> Result<(), String> {
    keychain::save_api_token(&token)
}

#[tauri::command]
pub async fn has_api_token() -> Result<bool, String> {
    match keychain::get_api_token() {
        Ok(_) => Ok(true),
        Err(_) => Ok(false),
    }
}
