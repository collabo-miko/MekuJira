use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

use crate::jira::types::NormalizedIssue;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FilterCache {
    pub last_fetched: Option<String>,
    pub issues: Vec<NormalizedIssue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MultiFilterCache {
    pub filters: HashMap<String, FilterCache>,
}

// Keep the old struct for backward compatibility with existing get_cached_issues command
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

impl Default for MultiFilterCache {
    fn default() -> Self {
        Self {
            filters: HashMap::new(),
        }
    }
}

fn cache_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("cache.json")
}

fn multi_cache_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("multi_cache.json")
}

// Legacy single-filter cache (kept for backward compatibility)
pub fn load(app_data_dir: &PathBuf) -> Result<IssueCache, String> {
    let path = cache_path(app_data_dir);
    if !path.exists() {
        return Ok(IssueCache::default());
    }
    let content =
        fs::read_to_string(&path).map_err(|e| format!("Failed to read cache: {}", e))?;
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

// Multi-filter cache
pub fn load_multi(app_data_dir: &PathBuf) -> Result<MultiFilterCache, String> {
    let path = multi_cache_path(app_data_dir);
    if !path.exists() {
        return Ok(MultiFilterCache::default());
    }
    let content =
        fs::read_to_string(&path).map_err(|e| format!("Failed to read multi cache: {}", e))?;
    serde_json::from_str(&content).map_err(|e| format!("Failed to parse multi cache: {}", e))
}

pub fn save_multi(app_data_dir: &PathBuf, cache: &MultiFilterCache) -> Result<(), String> {
    fs::create_dir_all(app_data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    let path = multi_cache_path(app_data_dir);
    let content = serde_json::to_string_pretty(cache)
        .map_err(|e| format!("Failed to serialize multi cache: {}", e))?;
    fs::write(&path, content).map_err(|e| format!("Failed to write multi cache: {}", e))
}

pub fn save_filter_cache(
    app_data_dir: &PathBuf,
    filter_id: &str,
    issues: Vec<NormalizedIssue>,
) -> Result<(), String> {
    let mut multi = load_multi(app_data_dir)?;
    multi.filters.insert(
        filter_id.to_string(),
        FilterCache {
            last_fetched: Some(chrono::Utc::now().to_rfc3339()),
            issues,
        },
    );
    save_multi(app_data_dir, &multi)
}
