use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

use crate::jira::types::NormalizedIssue;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BookmarkedIssue {
    #[serde(flatten)]
    pub issue: NormalizedIssue,
    pub bookmarked_at: String,
    pub source_filter_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BookmarkStore {
    pub bookmarked_issues: Vec<BookmarkedIssue>,
}

impl Default for BookmarkStore {
    fn default() -> Self {
        Self {
            bookmarked_issues: Vec::new(),
        }
    }
}

fn bookmarks_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("bookmarks.json")
}

pub fn load(app_data_dir: &PathBuf) -> Result<BookmarkStore, String> {
    let path = bookmarks_path(app_data_dir);
    if !path.exists() {
        return Ok(BookmarkStore::default());
    }
    let content =
        fs::read_to_string(&path).map_err(|e| format!("Failed to read bookmarks: {}", e))?;
    serde_json::from_str(&content).map_err(|e| format!("Failed to parse bookmarks: {}", e))
}

pub fn save(app_data_dir: &PathBuf, store: &BookmarkStore) -> Result<(), String> {
    fs::create_dir_all(app_data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    let path = bookmarks_path(app_data_dir);
    let content = serde_json::to_string_pretty(store)
        .map_err(|e| format!("Failed to serialize bookmarks: {}", e))?;
    fs::write(&path, content).map_err(|e| format!("Failed to write bookmarks: {}", e))
}

pub fn add(
    app_data_dir: &PathBuf,
    issue: &NormalizedIssue,
    filter_id: &str,
) -> Result<(), String> {
    let mut store = load(app_data_dir)?;
    if store.bookmarked_issues.iter().any(|b| b.issue.key == issue.key) {
        return Ok(());
    }
    store.bookmarked_issues.push(BookmarkedIssue {
        issue: issue.clone(),
        bookmarked_at: chrono::Utc::now().to_rfc3339(),
        source_filter_id: filter_id.to_string(),
    });
    save(app_data_dir, &store)
}

pub fn remove(app_data_dir: &PathBuf, issue_key: &str) -> Result<(), String> {
    let mut store = load(app_data_dir)?;
    store.bookmarked_issues.retain(|b| b.issue.key != issue_key);
    save(app_data_dir, &store)
}

pub fn toggle(
    app_data_dir: &PathBuf,
    issue: &NormalizedIssue,
    filter_id: &str,
) -> Result<bool, String> {
    let store = load(app_data_dir)?;
    let is_bookmarked = store.bookmarked_issues.iter().any(|b| b.issue.key == issue.key);
    if is_bookmarked {
        remove(app_data_dir, &issue.key)?;
        Ok(false)
    } else {
        add(app_data_dir, issue, filter_id)?;
        Ok(true)
    }
}

pub fn is_bookmarked(app_data_dir: &PathBuf, issue_key: &str) -> Result<bool, String> {
    let store = load(app_data_dir)?;
    Ok(store.bookmarked_issues.iter().any(|b| b.issue.key == issue_key))
}
