use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

use crate::jira::types::NormalizedIssue;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IssueCache {
    pub last_fetched: Option<String>,
    pub filter_id: String,
    pub issues: Vec<NormalizedIssue>,
}

impl Default for IssueCache {
    fn default() -> Self {
        Self {
            last_fetched: None,
            filter_id: "default".to_string(),
            issues: Vec::new(),
        }
    }
}

fn cache_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("cache.json")
}

pub fn load(app_data_dir: &PathBuf) -> Result<IssueCache, String> {
    let path = cache_path(app_data_dir);
    if !path.exists() {
        return Ok(IssueCache::default());
    }
    let content = fs::read_to_string(&path).map_err(|e| format!("Failed to read cache: {}", e))?;
    serde_json::from_str(&content).map_err(|e| format!("Failed to parse cache: {}", e))
}

pub fn save(app_data_dir: &PathBuf, cache: &IssueCache) -> Result<(), String> {
    fs::create_dir_all(app_data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    let path = cache_path(app_data_dir);
    let content =
        serde_json::to_string_pretty(cache).map_err(|e| format!("Failed to serialize: {}", e))?;
    fs::write(&path, content).map_err(|e| format!("Failed to write cache: {}", e))
}
