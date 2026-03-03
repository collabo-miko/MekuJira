import { invoke } from "@tauri-apps/api/core";
import type { BookmarkedIssue, NormalizedIssue } from "$lib/types";

export async function getBookmarks(): Promise<BookmarkedIssue[]> {
  return invoke("get_bookmarks");
}

export async function addBookmark(issue: NormalizedIssue, filterId: string): Promise<void> {
  return invoke("add_bookmark", { issue, filterId });
}

export async function removeBookmark(issueKey: string): Promise<void> {
  return invoke("remove_bookmark", { issueKey });
}

export async function toggleBookmark(issue: NormalizedIssue, filterId: string): Promise<boolean> {
  return invoke("toggle_bookmark", { issue, filterId });
}

export async function refreshBookmarks(): Promise<BookmarkedIssue[]> {
  return invoke("refresh_bookmarks");
}
