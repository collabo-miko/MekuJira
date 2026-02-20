use tauri::AppHandle;
use tauri::Manager;

use crate::jira::client;
use crate::jira::types::NormalizedIssue;
use crate::store::{cache, config};

#[tauri::command]
pub async fn get_issues(app: AppHandle) -> Result<Vec<NormalizedIssue>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let cfg = config::load(&app_data_dir)?;

    let active_filter = cfg
        .filters
        .iter()
        .find(|f| f.is_active)
        .ok_or("No active filter found")?;

    let issues = client::search_issues(&cfg.jira.domain, &cfg.jira.email, &active_filter.jql).await?;

    // Update cache
    let issue_cache = cache::IssueCache {
        last_fetched: Some(chrono::Utc::now().to_rfc3339()),
        filter_id: active_filter.id.clone(),
        issues: issues.clone(),
    };
    let _ = cache::save(&app_data_dir, &issue_cache);

    // Emit event to all windows
    let _ = app.emit("issues-updated", &issues);

    Ok(issues)
}

#[tauri::command]
pub async fn refresh_issues(app: AppHandle) -> Result<Vec<NormalizedIssue>, String> {
    get_issues(app).await
}

#[tauri::command]
pub async fn get_cached_issues(app: AppHandle) -> Result<cache::IssueCache, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    cache::load(&app_data_dir)
}

#[tauri::command]
pub async fn test_connection(app: AppHandle) -> Result<String, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;
    let cfg = config::load(&app_data_dir)?;

    if cfg.jira.domain.is_empty() || cfg.jira.email.is_empty() {
        return Err("Please configure JIRA domain and email first.".to_string());
    }

    client::test_connection(&cfg.jira.domain, &cfg.jira.email).await
}
