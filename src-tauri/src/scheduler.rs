use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use tauri::{AppHandle, Emitter};

use crate::{jira, store};

/// バックグラウンドポーリングを開始する
pub fn start(app: AppHandle) {
    let stop_flag = Arc::new(AtomicBool::new(false));
    let stop_flag_clone = stop_flag.clone();

    tauri::async_runtime::spawn(async move {
        polling_loop(app, stop_flag_clone).await;
    });
}

async fn polling_loop(app: AppHandle, stop_flag: Arc<AtomicBool>) {
    loop {
        // ポーリング間隔を設定から読み取り
        let interval_secs = {
            let app_data_dir = match app.path().app_data_dir() {
                Ok(dir) => dir,
                Err(_) => {
                    tokio::time::sleep(std::time::Duration::from_secs(60)).await;
                    continue;
                }
            };
            let config = store::config::load(&app_data_dir).unwrap_or_default();
            config.polling_interval_secs.max(30)
        };

        tokio::time::sleep(std::time::Duration::from_secs(interval_secs)).await;

        if stop_flag.load(Ordering::Relaxed) {
            break;
        }

        let app_data_dir = match app.path().app_data_dir() {
            Ok(dir) => dir,
            Err(_) => continue,
        };

        let config = match store::config::load(&app_data_dir) {
            Ok(c) => c,
            Err(_) => continue,
        };

        if config.jira.domain.is_empty() || config.jira.email.is_empty() {
            continue;
        }

        let enabled_filters: Vec<_> = config
            .filters
            .iter()
            .filter(|f| f.enabled)
            .cloned()
            .collect();
        if enabled_filters.is_empty() {
            continue;
        }

        // 有効なフィルタを並列に取得
        let mut handles = Vec::new();
        for filter in &enabled_filters {
            let domain = config.jira.domain.clone();
            let email = config.jira.email.clone();
            let jql = filter.jql.clone();
            let filter_id = filter.id.clone();
            handles.push(tokio::spawn(async move {
                let result = jira::client::search_issues(&domain, &email, &jql).await;
                (filter_id, result)
            }));
        }

        let mut filter_results: HashMap<String, Vec<jira::types::NormalizedIssue>> =
            HashMap::new();
        for handle in handles {
            match handle.await {
                Ok((filter_id, Ok(issues))) => {
                    let _ =
                        store::cache::save_filter_cache(&app_data_dir, &filter_id, issues.clone());
                    filter_results.insert(filter_id, issues);
                }
                Ok((filter_id, Err(e))) => {
                    log::warn!("Polling failed for filter {}: {}", filter_id, e);
                }
                Err(e) => {
                    log::warn!("Task join error: {}", e);
                }
            }
        }

        if !filter_results.is_empty() {
            let _ = app.emit("filter-issues-updated", &filter_results);

            // 後方互換: 最初のフィルタの課題を issues-updated イベントでも発行
            if let Some(first_filter) = enabled_filters.first() {
                if let Some(issues) = filter_results.get(&first_filter.id) {
                    let issue_cache = store::cache::IssueCache {
                        last_fetched: Some(chrono::Utc::now().to_rfc3339()),
                        filter_id: first_filter.id.clone(),
                        issues: issues.clone(),
                    };
                    let _ = store::cache::save(&app_data_dir, &issue_cache);
                    let _ = app.emit("issues-updated", issues);
                }
            }
        }

        // ブックマークを最新の課題データで更新
        if let Ok(mut bookmark_store) = store::bookmarks::load(&app_data_dir) {
            let mut changed = false;
            for bookmark in &mut bookmark_store.bookmarked_issues {
                for issues in filter_results.values() {
                    if let Some(fresh) = issues.iter().find(|i| i.key == bookmark.issue.key) {
                        bookmark.issue = fresh.clone();
                        changed = true;
                        break;
                    }
                }
            }
            if changed {
                let _ = store::bookmarks::save(&app_data_dir, &bookmark_store);
                let _ = app.emit("bookmarks-updated", ());
            }
        }
    }
}
