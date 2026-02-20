use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use rand::RngCore;
use sha2::{Digest, Sha256};
use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;

static CACHED_TOKEN: Mutex<Option<String>> = Mutex::new(None);
static DATA_DIR: Mutex<Option<PathBuf>> = Mutex::new(None);

const TOKEN_FILENAME: &str = ".token.enc";

/// Initialize with the app data directory. Must be called once at startup.
pub fn init(app_data_dir: PathBuf) {
    if let Ok(mut dir) = DATA_DIR.lock() {
        *dir = Some(app_data_dir);
    }
}

fn get_data_dir() -> Result<PathBuf, String> {
    DATA_DIR
        .lock()
        .map_err(|_| "Failed to lock data dir".to_string())?
        .clone()
        .ok_or_else(|| "Data dir not initialized".to_string())
}

fn token_path() -> Result<PathBuf, String> {
    Ok(get_data_dir()?.join(TOKEN_FILENAME))
}

/// Derive a 256-bit encryption key from machine-specific data.
/// Uses the app identifier + hostname as seed material.
fn derive_key() -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(b"jira-focus-v1-");
    // Use hostname as machine-specific entropy
    if let Ok(hostname) = hostname::get() {
        hasher.update(hostname.as_encoded_bytes());
    }
    // Add username for extra entropy
    hasher.update(whoami::username().as_bytes());
    hasher.finalize().into()
}

pub fn save_api_token(token: &str) -> Result<(), String> {
    let key = derive_key();
    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|e| format!("Cipher init error: {}", e))?;

    // Generate random 96-bit nonce
    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, token.as_bytes())
        .map_err(|e| format!("Encryption error: {}", e))?;

    // Store as: nonce (12 bytes) || ciphertext
    let mut data = Vec::with_capacity(12 + ciphertext.len());
    data.extend_from_slice(&nonce_bytes);
    data.extend_from_slice(&ciphertext);

    let path = token_path()?;
    fs::create_dir_all(path.parent().unwrap())
        .map_err(|e| format!("Failed to create dir: {}", e))?;
    fs::write(&path, hex::encode(&data))
        .map_err(|e| format!("Failed to write token: {}", e))?;

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

    // Read from encrypted file
    let path = token_path()?;
    if !path.exists() {
        return Err("No API token saved".to_string());
    }

    let hex_data = fs::read_to_string(&path)
        .map_err(|e| format!("Failed to read token file: {}", e))?;
    let data = hex::decode(hex_data.trim())
        .map_err(|e| format!("Invalid token data: {}", e))?;

    if data.len() < 13 {
        return Err("Corrupted token data".to_string());
    }

    let key = derive_key();
    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|e| format!("Cipher init error: {}", e))?;

    let nonce = Nonce::from_slice(&data[..12]);
    let plaintext = cipher
        .decrypt(nonce, &data[12..])
        .map_err(|_| "Failed to decrypt token. Data may be corrupted.".to_string())?;

    let token = String::from_utf8(plaintext)
        .map_err(|_| "Invalid token encoding".to_string())?;

    // Update cache
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

    get_api_token().is_ok()
}

pub fn delete_api_token() -> Result<(), String> {
    let path = token_path()?;
    if path.exists() {
        fs::remove_file(&path)
            .map_err(|e| format!("Failed to delete token: {}", e))?;
    }

    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = None;
    }

    Ok(())
}
