<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import { invoke } from "@tauri-apps/api/core";
  import DashboardView from "$lib/components/DashboardView.svelte";
  import { refreshAllFilters } from "$lib/api/jira";
  import { getBookmarks, toggleBookmark } from "$lib/api/bookmarks";
  import { getSettings } from "$lib/api/settings";
  import type {
    NormalizedIssue,
    BookmarkedIssue,
    AppSettings,
    FilterIssuesMap,
  } from "$lib/types";

  let isLoading = $state(false);
  let appSettings = $state<AppSettings | null>(null);
  let errorMsg = $state<string | null>(null);

  let bookmarks = $state<BookmarkedIssue[]>([]);
  let filterIssues = $state<FilterIssuesMap>({});
  let bookmarkedKeys = $derived(new Set(bookmarks.map((b) => b.key)));
  let filters = $derived(appSettings?.filters ?? []);

  onMount(async () => {
    try {
      appSettings = await getSettings();
    } catch {}

    try {
      bookmarks = await getBookmarks();
    } catch {}

    // Initial load
    await handleRefresh();

    listen<FilterIssuesMap>("filter-issues-updated", (event) => {
      filterIssues = event.payload;
    });

    listen("bookmarks-updated", async () => {
      try {
        bookmarks = await getBookmarks();
      } catch {}
    });
  });

  async function handleRefresh() {
    if (!appSettings?.jira.domain || !appSettings?.jira.email) {
      errorMsg = "JIRA接続情報が設定されていません。設定画面から設定してください。";
      return;
    }
    isLoading = true;
    errorMsg = null;
    try {
      filterIssues = await refreshAllFilters();
    } catch (e) {
      errorMsg = String(e);
    } finally {
      isLoading = false;
    }
  }

  async function handleToggleBookmark(issue: NormalizedIssue, filterId: string) {
    try {
      await toggleBookmark(issue, filterId);
      bookmarks = await getBookmarks();
    } catch (e) {
      console.error("Failed to toggle bookmark:", e);
    }
  }

  function openSettings() {
    invoke("open_settings_window");
  }
</script>

<div class="dashboard-page">
  <header class="page-header">
    <h1>対象課題一覧</h1>
    <button class="settings-btn" onclick={openSettings} title="設定">
      <svg
        width="18"
        height="18"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.4"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M6.86 2.07a1 1 0 0 1 2.28 0l.12.56a1 1 0 0 0 1.33.6l.52-.22a1 1 0 0 1 1.14 1.62l-.4.4a1 1 0 0 0 0 1.33l.4.4a1 1 0 0 1-1.14 1.62l-.52-.22a1 1 0 0 0-1.33.6l-.12.56a1 1 0 0 1-2.28 0l-.12-.56a1 1 0 0 0-1.33-.6l-.52.22a1 1 0 0 1-1.14-1.62l.4-.4a1 1 0 0 0 0-1.33l-.4-.4A1 1 0 0 1 4.89 2.4l.52.22a1 1 0 0 0 1.33-.6l.12-.56z"
        />
        <circle cx="8" cy="6" r="1.5" />
      </svg>
    </button>
  </header>

  {#if errorMsg}
    <div class="error">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="7"/>
        <path d="M8 5v3.5M8 10.5v.5"/>
      </svg>
      <p>{errorMsg}</p>
    </div>
  {/if}

  <DashboardView
    {filters}
    {filterIssues}
    {bookmarkedKeys}
    {isLoading}
    onRefresh={handleRefresh}
    onToggleBookmark={handleToggleBookmark}
  />
</div>

<style>
  .dashboard-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--color-bg);
    overflow: hidden;
  }
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px 12px;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }
  .page-header h1 {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-primary);
  }
  .settings-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: none;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    color: var(--color-text-tertiary);
    transition: all 0.12s ease;
  }
  .settings-btn:hover {
    background: var(--color-surface);
    color: var(--color-text-primary);
  }
  .error {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 14px;
    background: var(--color-error-bg);
    color: var(--color-error);
    font-size: 14px;
    line-height: 1.4;
    border-bottom: 1px solid var(--color-error-border);
    flex-shrink: 0;
  }
  .error svg {
    flex-shrink: 0;
    margin-top: 1px;
  }
  .error p {
    word-break: break-all;
  }
</style>
