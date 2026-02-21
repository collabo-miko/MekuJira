import { invoke } from "@tauri-apps/api/core";
import type { NormalizedIssue, IssueCache, FilterIssuesMap, ViewMode } from "$lib/types";

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

export async function getAllFilterIssues(): Promise<FilterIssuesMap> {
  return invoke("get_all_filter_issues");
}

export async function refreshAllFilters(): Promise<FilterIssuesMap> {
  return invoke("refresh_all_filters");
}

export async function resizePopup(mode: ViewMode): Promise<void> {
  return invoke("resize_popup", { mode });
}
