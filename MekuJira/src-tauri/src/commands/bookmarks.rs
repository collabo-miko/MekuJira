use tauri::{AppHandle, Emitter, Manager};

use crate::jira::client;
use crate::jira::types::NormalizedIssue;
use crate::store::{bookmarks, config};

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

#[tauri::command]
pub async fn refresh_bookmarks(
    app: AppHandle,
) -> Result<Vec<bookmarks::BookmarkedIssue>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    let store = bookmarks::load(&app_data_dir)?;

    if store.bookmarked_issues.is_empty() {
        return Ok(store.bookmarked_issues);
    }

    let cfg = config::load(&app_data_dir)?;
    if cfg.jira.domain.is_empty() || cfg.jira.email.is_empty() {
        return Err("JIRA接続情報が設定されていません。".to_string());
    }

    let keys: Vec<String> = store
        .bookmarked_issues
        .iter()
        .map(|b| b.issue.key.clone())
        .collect();
    let jql = format!("key in ({})", keys.join(", "));

    let fresh_issues = client::search_issues(&cfg.jira.domain, &cfg.jira.email, &jql).await?;

    let mut updated_store = store;
    for bookmark in &mut updated_store.bookmarked_issues {
        if let Some(fresh) = fresh_issues.iter().find(|i| i.key == bookmark.issue.key) {
            bookmark.issue = fresh.clone();
        }
    }

    bookmarks::save(&app_data_dir, &updated_store)?;
    let _ = app.emit("bookmarks-updated", ());
    Ok(updated_store.bookmarked_issues)
}
