import { invoke } from "@tauri-apps/api/core";
import type { NormalizedIssue, IssueCache } from "$lib/types";

export async function getIssues(): Promise<NormalizedIssue[]> {
  return invoke("get_issues");
}

export async function refreshIssues(): Promise<NormalizedIssue[]> {
  return invoke("refresh_issues");
}

export async function getCachedIssues(): Promise<IssueCache> {
  return invoke("get_cached_issues");
}

export async function testConnection(): Promise<string> {
  return invoke("test_connection");
}
