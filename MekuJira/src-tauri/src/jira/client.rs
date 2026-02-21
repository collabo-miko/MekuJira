use super::auth;
use super::types::{JiraMyselfResponse, JiraSearchResponse, NormalizedIssue};

pub async fn search_issues(
    domain: &str,
    email: &str,
    jql: &str,
) -> Result<Vec<NormalizedIssue>, String> {
    let auth_header = auth::get_auth_header(email)?;

    // Try new endpoint first (POST /rest/api/3/search/jql), fall back to legacy (GET /rest/api/3/search)
    let result = search_issues_new(domain, &auth_header, jql).await;
    match result {
        Ok(issues) => Ok(issues),
        Err(_) => search_issues_legacy(domain, &auth_header, jql).await,
    }
}

async fn search_issues_new(
    domain: &str,
    auth_header: &str,
    jql: &str,
) -> Result<Vec<NormalizedIssue>, String> {
    let url = format!("https://{}/rest/api/3/search/jql", domain);
    let client = reqwest::Client::new();
    let response = client
        .post(&url)
        .header("Authorization", auth_header)
        .header("Content-Type", "application/json")
        .json(&serde_json::json!({
            "jql": jql,
            "maxResults": 50,
            "fields": ["key", "summary", "status", "priority", "assignee"]
        }))
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    parse_search_response(response, domain).await
}

async fn search_issues_legacy(
    domain: &str,
    auth_header: &str,
    jql: &str,
) -> Result<Vec<NormalizedIssue>, String> {
    let url = format!(
        "https://{}/rest/api/3/search?jql={}&maxResults=50&fields=key,summary,status,priority,assignee",
        domain,
        urlencoding::encode(jql)
    );
    let client = reqwest::Client::new();
    let response = client
        .get(&url)
        .header("Authorization", auth_header)
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    parse_search_response(response, domain).await
}

async fn parse_search_response(
    response: reqwest::Response,
    domain: &str,
) -> Result<Vec<NormalizedIssue>, String> {
    let status = response.status();
    if status == 401 {
        return Err("Authentication failed. Please check your credentials.".to_string());
    }
    if status == 429 {
        return Err("Rate limited by JIRA. Please try again later.".to_string());
    }

    let body = response
        .text()
        .await
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if !status.is_success() {
        return Err(format!("JIRA API error ({}): {}", status, body));
    }

    let search_response: JiraSearchResponse = serde_json::from_str(&body)
        .map_err(|e| {
            let preview = if body.len() > 500 { &body[..500] } else { &body };
            format!("Failed to parse response: {} | Body: {}", e, preview)
        })?;

    let issues = search_response
        .issues
        .iter()
        .map(|issue| NormalizedIssue::from_jira_issue(issue, domain))
        .collect();

    Ok(issues)
}

pub async fn test_connection(domain: &str, email: &str) -> Result<String, String> {
    let auth_header = auth::get_auth_header(email)?;
    let url = format!("https://{}/rest/api/3/myself", domain);

    let client = reqwest::Client::new();
    let response = client
        .get(&url)
        .header("Authorization", &auth_header)
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    let status = response.status();
    let body = response
        .text()
        .await
        .map_err(|e| format!("Failed to read response: {}", e))?;

    if !status.is_success() {
        return Err(format!("Connection failed (HTTP {}): {}", status, body));
    }

    let myself: JiraMyselfResponse = serde_json::from_str(&body)
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(myself.display_name)
}
