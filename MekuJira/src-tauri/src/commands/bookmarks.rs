use tauri::{AppHandle, Emitter, Manager};

use crate::jira::types::NormalizedIssue;
use crate::store::bookmarks;

#[tauri::command]
pub async fn get_bookmarks(app: AppHandle) -> Result<Vec<bookmarks::BookmarkedIssue>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    let store = bookmarks::load(&app_data_dir)?;
    Ok(store.bookmarked_issues)
}

#[tauri::command]
pub async fn add_bookmark(
    app: AppHandle,
    issue: NormalizedIssue,
    filter_id: String,
) -> Result<(), String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    bookmarks::add(&app_data_dir, &issue, &filter_id)?;
    let _ = app.emit("bookmarks-updated", ());
    Ok(())
}

#[tauri::command]
pub async fn remove_bookmark(app: AppHandle, issue_key: String) -> Result<(), String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    bookmarks::remove(&app_data_dir, &issue_key)?;
    let _ = app.emit("bookmarks-updated", ());
    Ok(())
}

#[tauri::command]
pub async fn toggle_bookmark(
    app: AppHandle,
    issue: NormalizedIssue,
    filter_id: String,
) -> Result<bool, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    let result = bookmarks::toggle(&app_data_dir, &issue, &filter_id)?;
    let _ = app.emit("bookmarks-updated", ());
    Ok(result)
}
