use keyring::Entry;
use std::sync::Mutex;

const SERVICE_NAME: &str = "jira-focus";
const USERNAME: &str = "api_token";

static CACHED_TOKEN: Mutex<Option<String>> = Mutex::new(None);

pub fn save_api_token(token: &str) -> Result<(), String> {
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    entry
        .set_password(token)
        .map_err(|e| format!("Failed to save token: {}", e))?;

    // Update cache
    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = Some(token.to_string());
    }

    Ok(())
}

pub fn get_api_token() -> Result<String, String> {
    // Return cached token if available
    if let Ok(cache) = CACHED_TOKEN.lock() {
        if let Some(ref token) = *cache {
            return Ok(token.clone());
        }
    }

    // Read from keychain and cache it
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    let token = entry
        .get_password()
        .map_err(|e| format!("Failed to get token: {}", e))?;

    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = Some(token.clone());
    }

    Ok(token)
}

pub fn has_api_token() -> bool {
    // Check cache first
    if let Ok(cache) = CACHED_TOKEN.lock() {
        if cache.is_some() {
            return true;
        }
    }

    // Try reading from keychain
    get_api_token().is_ok()
}

pub fn delete_api_token() -> Result<(), String> {
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    entry
        .delete_credential()
        .map_err(|e| format!("Failed to delete token: {}", e))?;

    // Clear cache
    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = None;
    }

    Ok(())
}
