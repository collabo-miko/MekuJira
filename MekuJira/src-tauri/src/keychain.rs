use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use argon2::Argon2;
use rand::RngCore;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::sync::Mutex;

static CACHED_TOKEN: Mutex<Option<String>> = Mutex::new(None);
static DATA_DIR: Mutex<Option<PathBuf>> = Mutex::new(None);

const TOKEN_FILENAME: &str = ".token.enc";
const SALT_FILENAME: &str = ".token.salt";

/// Encrypted token file format
#[derive(Serialize, Deserialize)]
struct EncryptedData {
    /// Format version for future migration
    version: u8,
    /// Hex-encoded nonce (12 bytes)
    nonce: String,
    /// Hex-encoded ciphertext
    ciphertext: String,
}

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

fn salt_path() -> Result<PathBuf, String> {
    Ok(get_data_dir()?.join(SALT_FILENAME))
}

/// Get or create a persistent random salt (32 bytes).
/// The salt is stored in a separate file and reused across token saves.
fn get_or_create_salt() -> Result<[u8; 32], String> {
    let path = salt_path()?;

    if path.exists() {
        let hex_salt = fs::read_to_string(&path)
            .map_err(|e| format!("Failed to read salt: {}", e))?;
        let salt_vec = hex::decode(hex_salt.trim())
            .map_err(|e| format!("Invalid salt data: {}", e))?;
        if salt_vec.len() == 32 {
            let mut salt = [0u8; 32];
            salt.copy_from_slice(&salt_vec);
            return Ok(salt);
        }
    }

    // Generate new salt
    let mut salt = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut salt);

    fs::create_dir_all(path.parent().unwrap())
        .map_err(|e| format!("Failed to create dir: {}", e))?;
    fs::write(&path, hex::encode(salt))
        .map_err(|e| format!("Failed to write salt: {}", e))?;

    // Restrict file permissions to owner only (macOS/Linux)
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = fs::set_permissions(&path, fs::Permissions::from_mode(0o600));
    }

    Ok(salt)
}

/// Collect machine-specific entropy for key derivation.
/// Uses macOS hardware UUID if available, falls back to hostname + username.
fn get_machine_identity() -> Vec<u8> {
    let mut identity = Vec::new();

    // Constant app identifier
    identity.extend_from_slice(b"mekujira-v2-");

    // Try macOS IOPlatformUUID (stable across reboots, unique per machine)
    #[cfg(target_os = "macos")]
    {
        if let Ok(output) = std::process::Command::new("ioreg")
            .args(["-rd1", "-c", "IOPlatformExpertDevice"])
            .output()
        {
            let stdout = String::from_utf8_lossy(&output.stdout);
            if let Some(line) = stdout.lines().find(|l| l.contains("IOPlatformUUID")) {
                identity.extend_from_slice(line.as_bytes());
                return identity;
            }
        }
    }

    // Fallback: hostname + username
    if let Ok(hostname) = hostname::get() {
        identity.extend_from_slice(hostname.as_encoded_bytes());
    }
    identity.extend_from_slice(whoami::username().as_bytes());

    identity
}

/// Derive a 256-bit encryption key using Argon2id.
///
/// Argon2id is resistant to:
/// - GPU/ASIC brute force (memory-hard)
/// - Side-channel attacks (hybrid mode)
/// - Rainbow table attacks (uses random salt)
fn derive_key(salt: &[u8; 32]) -> Result<[u8; 32], String> {
    let machine_id = get_machine_identity();

    let mut key = [0u8; 32];
    Argon2::default()
        .hash_password_into(&machine_id, salt, &mut key)
        .map_err(|e| format!("Key derivation error: {}", e))?;

    Ok(key)
}

pub fn save_api_token(token: &str) -> Result<(), String> {
    let salt = get_or_create_salt()?;
    let key = derive_key(&salt)?;

    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|e| format!("Cipher init error: {}", e))?;

    // Generate random 96-bit nonce
    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher
        .encrypt(nonce, token.as_bytes())
        .map_err(|e| format!("Encryption error: {}", e))?;

    let encrypted = EncryptedData {
        version: 2,
        nonce: hex::encode(nonce_bytes),
        ciphertext: hex::encode(ciphertext),
    };

    let path = token_path()?;
    fs::create_dir_all(path.parent().unwrap())
        .map_err(|e| format!("Failed to create dir: {}", e))?;

    let json = serde_json::to_string(&encrypted)
        .map_err(|e| format!("Failed to serialize: {}", e))?;
    fs::write(&path, &json)
        .map_err(|e| format!("Failed to write token: {}", e))?;

    // Restrict file permissions to owner only
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = fs::set_permissions(&path, fs::Permissions::from_mode(0o600));
    }

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

    let path = token_path()?;
    if !path.exists() {
        return Err("No API token saved".to_string());
    }

    let content = fs::read_to_string(&path)
        .map_err(|e| format!("Failed to read token file: {}", e))?;

    // Only accept v2 JSON format. Reject anything else.
    let encrypted: EncryptedData = serde_json::from_str(content.trim())
        .map_err(|_| "Invalid token file format. Please re-save your API token.".to_string())?;

    if encrypted.version != 2 {
        return Err("Unsupported token format version. Please re-save your API token.".to_string());
    }

    let nonce_bytes = hex::decode(&encrypted.nonce)
        .map_err(|_| "Corrupted token data".to_string())?;
    let ciphertext = hex::decode(&encrypted.ciphertext)
        .map_err(|_| "Corrupted token data".to_string())?;

    if nonce_bytes.len() != 12 {
        return Err("Corrupted token data".to_string());
    }

    let salt = get_or_create_salt()?;
    let key = derive_key(&salt)?;

    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|e| format!("Cipher init error: {}", e))?;

    let nonce = Nonce::from_slice(&nonce_bytes);
    let plaintext = cipher
        .decrypt(nonce, ciphertext.as_ref())
        .map_err(|_| "Failed to decrypt token. Please re-save your API token.".to_string())?;

    let token = String::from_utf8(plaintext)
        .map_err(|_| "Invalid token encoding".to_string())?;

    // Update cache
    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = Some(token.clone());
    }

    Ok(token)
}

pub fn has_api_token() -> bool {
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

    // Also clean up salt
    let salt = salt_path()?;
    if salt.exists() {
        let _ = fs::remove_file(&salt);
    }

    if let Ok(mut cache) = CACHED_TOKEN.lock() {
        *cache = None;
    }

    Ok(())
}
