use tauri::AppHandle;
use tauri::Manager;
use tauri_plugin_notification::NotificationExt;

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
    Ok(keychain::has_api_token())
}

#[tauri::command]
pub async fn test_notification(app: AppHandle) -> Result<(), String> {
    app.notification()
        .builder()
        .title("MekuJira")
        .body("テスト通知です。この通知が表示されていれば正常です。")
        .sound("default")
        .show()
        .map_err(|e| format!("通知の送信に失敗しました: {}", e))
}
