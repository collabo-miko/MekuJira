<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import AppHeader from "$lib/components/AppHeader.svelte";
  import TrackingView from "$lib/components/TrackingView.svelte";
  import DashboardView from "$lib/components/DashboardView.svelte";
  import { getAllFilterIssues, refreshAllFilters, resizePopup } from "$lib/api/jira";
  import { getBookmarks, toggleBookmark } from "$lib/api/bookmarks";
  import { getSettings } from "$lib/api/settings";
  import type {
    NormalizedIssue,
    BookmarkedIssue,
    AppSettings,
    ViewMode,
    FilterIssuesMap,
  } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";

  let viewMode = $state<ViewMode>("tracking");
  let isLoading = $state(false);
  let appSettings = $state<AppSettings | null>(null);
  let errorMsg = $state<string | null>(null);

  // Tracking mode state
  let bookmarks = $state<BookmarkedIssue[]>([]);

  // Dashboard mode state
  let filterIssues = $state<FilterIssuesMap>({});
  let bookmarkedKeys = $derived(new Set(bookmarks.map((b) => b.key)));

  let filters = $derived(appSettings?.filters ?? []);

  onMount(async () => {
    // Load bookmarks
    try {
      bookmarks = await getBookmarks();
    } catch {}

    // Load settings
    try {
      appSettings = await getSettings();
    } catch {}

    // Listen for events
    listen<FilterIssuesMap>("filter-issues-updated", (event) => {
      filterIssues = event.payload;
    });

    listen("bookmarks-updated", async () => {
      try {
        bookmarks = await getBookmarks();
      } catch {}
    });

    const currentWindow = getCurrentWindow();
    currentWindow.onFocusChanged(async ({ payload: focused }) => {
      if (focused) {
        try {
          appSettings = await getSettings();
          bookmarks = await getBookmarks();
        } catch {}
      }
    });
  });

  async function handleModeChange(mode: ViewMode) {
    viewMode = mode;
    try {
      await resizePopup(mode);
    } catch (e) {
      console.error("Failed to resize:", e);
    }

    if (mode === "dashboard" && Object.keys(filterIssues).length === 0) {
      await handleDashboardRefresh();
    }
  }

  async function handleDashboardRefresh() {
    if (!appSettings?.jira.domain || !appSettings?.jira.email) {
      errorMsg = "JIRA接続情報が設定されていません。歯車アイコンから設定してください。";
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
</script>

<div class="popup">
  <AppHeader {viewMode} onModeChange={handleModeChange} />

  {#if errorMsg}
    <div class="error">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="7"/>
        <path d="M8 5v3.5M8 10.5v.5"/>
      </svg>
      <p>{errorMsg}</p>
    </div>
  {/if}

  {#if viewMode === "tracking"}
    <TrackingView {bookmarks} />
  {:else}
    <DashboardView
      {filters}
      {filterIssues}
      {bookmarkedKeys}
      {isLoading}
      onRefresh={handleDashboardRefresh}
      onToggleBookmark={handleToggleBookmark}
    />
  {/if}
</div>

<style>
  .popup {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--color-bg);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  .error {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 14px;
    background: var(--color-error-bg);
    color: var(--color-error);
    font-size: 13px;
    line-height: 1.4;
    border-bottom: 1px solid var(--color-error-border);
    max-height: 100px;
    overflow-y: auto;
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
