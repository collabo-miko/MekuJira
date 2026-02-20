use keyring::Entry;

const SERVICE_NAME: &str = "jira-focus";
const USERNAME: &str = "api_token";

pub fn save_api_token(token: &str) -> Result<(), String> {
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    entry
        .set_password(token)
        .map_err(|e| format!("Failed to save token: {}", e))
}

pub fn get_api_token() -> Result<String, String> {
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    entry
        .get_password()
        .map_err(|e| format!("Failed to get token: {}", e))
}

pub fn delete_api_token() -> Result<(), String> {
    let entry =
        Entry::new(SERVICE_NAME, USERNAME).map_err(|e| format!("Keychain error: {}", e))?;
    entry
        .delete_credential()
        .map_err(|e| format!("Failed to delete token: {}", e))
}
