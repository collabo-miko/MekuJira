use base64::{engine::general_purpose::STANDARD, Engine};

use crate::keychain;

pub fn build_basic_auth_header(email: &str, api_token: &str) -> String {
    let credentials = format!("{}:{}", email, api_token);
    let encoded = STANDARD.encode(credentials.as_bytes());
    format!("Basic {}", encoded)
}

pub fn get_auth_header(email: &str) -> Result<String, String> {
    let token = keychain::get_api_token().map_err(|e| format!("Failed to get API token: {}", e))?;
    Ok(build_basic_auth_header(email, &token))
}
