use std::collections::HashMap;
use tauri::AppHandle;
use tauri::{Emitter, Manager};

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

    if cfg.jira.domain.is_empty() || cfg.jira.email.is_empty() {
        return Err("JIRA接続情報が設定されていません。設定画面で設定してください。".to_string());
    }

    // Use first enabled filter for backward compatibility
    let active_filter = cfg
        .filters
        .iter()
        .find(|f| f.enabled)
        .ok_or("No active filter found")?;

    let issues =
        client::search_issues(&cfg.jira.domain, &cfg.jira.email, &active_filter.jql).await?;

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

#[tauri::command]
pub async fn get_all_filter_issues(
    app: AppHandle,
) -> Result<HashMap<String, Vec<NormalizedIssue>>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let cfg = config::load(&app_data_dir)?;

    if cfg.jira.domain.is_empty() || cfg.jira.email.is_empty() {
        return Err("JIRA接続情報が設定されていません。設定画面で設定してください。".to_string());
    }

    let enabled_filters: Vec<_> = cfg.filters.iter().filter(|f| f.enabled).cloned().collect();
    if enabled_filters.is_empty() {
        return Ok(HashMap::new());
    }

    // Try loading from multi-cache first
    let cached = cache::load_multi(&app_data_dir).unwrap_or_default();
    if !cached.filters.is_empty() {
        let mut result = HashMap::new();
        for filter in &enabled_filters {
            if let Some(fc) = cached.filters.get(&filter.id) {
                result.insert(filter.id.clone(), fc.issues.clone());
            }
        }
        if result.len() == enabled_filters.len() {
            return Ok(result);
        }
    }

    // Fetch all filters in parallel
    fetch_all_filters(&app, &cfg, &enabled_filters).await
}

#[tauri::command]
pub async fn refresh_all_filters(
    app: AppHandle,
) -> Result<HashMap<String, Vec<NormalizedIssue>>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let cfg = config::load(&app_data_dir)?;

    if cfg.jira.domain.is_empty() || cfg.jira.email.is_empty() {
        return Err("JIRA接続情報が設定されていません。設定画面で設定してください。".to_string());
    }

    let enabled_filters: Vec<_> = cfg.filters.iter().filter(|f| f.enabled).cloned().collect();
    if enabled_filters.is_empty() {
        return Ok(HashMap::new());
    }

    fetch_all_filters(&app, &cfg, &enabled_filters).await
}

async fn fetch_all_filters(
    app: &AppHandle,
    cfg: &config::AppConfig,
    filters: &[config::JqlFilter],
) -> Result<HashMap<String, Vec<NormalizedIssue>>, String> {
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data dir: {}", e))?;

    let mut handles = Vec::new();
    for filter in filters {
        let domain = cfg.jira.domain.clone();
        let email = cfg.jira.email.clone();
        let jql = filter.jql.clone();
        let filter_id = filter.id.clone();
        handles.push(tokio::spawn(async move {
            let result = client::search_issues(&domain, &email, &jql).await;
            (filter_id, result)
        }));
    }

    let mut result = HashMap::new();
    for handle in handles {
        match handle.await {
            Ok((filter_id, Ok(issues))) => {
                let _ = cache::save_filter_cache(&app_data_dir, &filter_id, issues.clone());
                result.insert(filter_id, issues);
            }
            Ok((filter_id, Err(e))) => {
                log::warn!("Failed to fetch filter {}: {}", filter_id, e);
                // Use cached data if available
                if let Ok(cached) = cache::load_multi(&app_data_dir) {
                    if let Some(fc) = cached.filters.get(&filter_id) {
                        result.insert(filter_id, fc.issues.clone());
                    }
                }
            }
            Err(e) => {
                log::warn!("Task join error: {}", e);
            }
        }
    }

    let _ = app.emit("filter-issues-updated", &result);
    Ok(result)
}
