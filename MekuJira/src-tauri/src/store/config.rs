use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub jira: JiraConfig,
    pub filters: Vec<JqlFilter>,
    pub polling_interval_secs: u64,
    pub auto_start: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraConfig {
    pub domain: String,
    pub email: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JqlFilter {
    pub id: String,
    pub name: String,
    pub jql: String,
    pub enabled: bool,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            jira: JiraConfig {
                domain: String::new(),
                email: String::new(),
            },
            filters: vec![JqlFilter {
                id: "default".to_string(),
                name: "自分の未完了課題".to_string(),
                jql: "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC"
                    .to_string(),
                enabled: true,
            }],
            polling_interval_secs: 3600,
            auto_start: false,
        }
    }
}

fn config_path(app_data_dir: &PathBuf) -> PathBuf {
    app_data_dir.join("config.json")
}

pub fn load(app_data_dir: &PathBuf) -> Result<AppConfig, String> {
    let path = config_path(app_data_dir);
    if !path.exists() {
        let config = AppConfig::default();
        save(app_data_dir, &config)?;
        return Ok(config);
    }
    let content = fs::read_to_string(&path).map_err(|e| format!("Failed to read config: {}", e))?;
    serde_json::from_str(&content).map_err(|e| format!("Failed to parse config: {}", e))
}

pub fn save(app_data_dir: &PathBuf, config: &AppConfig) -> Result<(), String> {
    fs::create_dir_all(app_data_dir)
        .map_err(|e| format!("Failed to create data dir: {}", e))?;
    let path = config_path(app_data_dir);
    let content =
        serde_json::to_string_pretty(config).map_err(|e| format!("Failed to serialize: {}", e))?;
    fs::write(&path, content).map_err(|e| format!("Failed to write config: {}", e))
}
