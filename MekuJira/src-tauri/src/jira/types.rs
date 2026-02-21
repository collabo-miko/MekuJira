use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraSearchResponse {
    #[serde(default)]
    pub total: Option<u32>,
    #[serde(default)]
    pub issues: Vec<JiraIssue>,
    #[serde(default, rename = "startAt")]
    pub start_at: Option<u32>,
    #[serde(default, rename = "maxResults")]
    pub max_results: Option<u32>,
    #[serde(default, rename = "isLast")]
    pub is_last: Option<bool>,
    #[serde(default, rename = "nextPageToken")]
    pub next_page_token: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraIssue {
    pub key: String,
    pub fields: JiraFields,
    #[serde(rename = "self")]
    pub self_url: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraFields {
    pub summary: String,
    pub status: Option<JiraStatus>,
    pub priority: Option<JiraPriority>,
    pub assignee: Option<JiraUser>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraStatus {
    pub name: String,
    #[serde(rename = "statusCategory")]
    pub status_category: Option<JiraStatusCategory>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraStatusCategory {
    pub key: String,
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraPriority {
    pub name: String,
    #[serde(rename = "iconUrl")]
    pub icon_url: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraUser {
    #[serde(rename = "displayName")]
    pub display_name: String,
    #[serde(rename = "avatarUrls")]
    pub avatar_urls: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JiraMyselfResponse {
    #[serde(rename = "displayName")]
    pub display_name: String,
    #[serde(rename = "emailAddress")]
    pub email_address: Option<String>,
}

/// Normalized issue for frontend consumption
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NormalizedIssue {
    pub key: String,
    pub summary: String,
    pub status: String,
    pub status_category: String,
    pub priority: String,
    pub assignee: String,
    pub url: String,
}

impl NormalizedIssue {
    pub fn from_jira_issue(issue: &JiraIssue, domain: &str) -> Self {
        Self {
            key: issue.key.clone(),
            summary: issue.fields.summary.clone(),
            status: issue
                .fields
                .status
                .as_ref()
                .map(|s| s.name.clone())
                .unwrap_or_default(),
            status_category: issue
                .fields
                .status
                .as_ref()
                .and_then(|s| s.status_category.as_ref())
                .map(|c| c.key.clone())
                .unwrap_or_default(),
            priority: issue
                .fields
                .priority
                .as_ref()
                .map(|p| p.name.clone())
                .unwrap_or_default(),
            assignee: issue
                .fields
                .assignee
                .as_ref()
                .map(|a| a.display_name.clone())
                .unwrap_or_default(),
            url: format!("https://{}/browse/{}", domain, issue.key),
        }
    }
}
