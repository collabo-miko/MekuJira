import { invoke } from "@tauri-apps/api/core";
import type { AppSettings } from "$lib/types";

export async function getSettings(): Promise<AppSettings> {
  return invoke("get_settings");
}

export async function saveSettings(settings: AppSettings): Promise<void> {
  return invoke("save_settings", { settings });
}

export async function saveApiToken(token: string): Promise<void> {
  return invoke("save_api_token", { token });
}

export async function hasApiToken(): Promise<boolean> {
  return invoke("has_api_token");
}

export async function testNotification(): Promise<void> {
  return invoke("test_notification");
}
