<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import IssueList from "$lib/components/IssueList.svelte";
  import { getCachedIssues, refreshIssues } from "$lib/api/jira";
  import { getSettings, saveSettings } from "$lib/api/settings";
  import type { NormalizedIssue, AppSettings } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";
  import { invoke } from "@tauri-apps/api/core";

  let issues = $state<NormalizedIssue[]>([]);
  let isLoading = $state(false);
  let lastFetched = $state<string | null>(null);
  let appSettings = $state<AppSettings | null>(null);
  let errorMsg = $state<string | null>(null);

  let filters = $derived(appSettings?.filters ?? []);

  onMount(async () => {
    try {
      const cached = await getCachedIssues();
      if (cached.issues.length > 0) {
        issues = cached.issues;
        lastFetched = cached.last_fetched;
      }
    } catch {}

    try {
      appSettings = await getSettings();
    } catch {}

    await handleRefresh();

    listen<NormalizedIssue[]>("issues-updated", (event) => {
      issues = event.payload;
      lastFetched = new Date().toISOString();
    });

    const currentWindow = getCurrentWindow();
    currentWindow.onFocusChanged(async ({ payload: focused }) => {
      if (focused) {
        try {
          appSettings = await getSettings();
        } catch {}
      }
    });
  });

  async function handleRefresh() {
    if (!appSettings?.jira.domain || !appSettings?.jira.email) {
      errorMsg = "JIRA接続情報が設定されていません。右上の歯車アイコンから設定してください。";
      return;
    }
    isLoading = true;
    errorMsg = null;
    try {
      issues = await refreshIssues();
      lastFetched = new Date().toISOString();
    } catch (e) {
      errorMsg = String(e);
    } finally {
      isLoading = false;
    }
  }

  async function handleFilterChange(filterId: string) {
    if (!appSettings) return;
    const updatedFilters = appSettings.filters.map((f) => ({
      ...f,
      is_active: f.id === filterId,
    }));
    appSettings = { ...appSettings, filters: updatedFilters };
    await saveSettings(appSettings);
    await handleRefresh();
  }

  function openSettings() {
    invoke("open_settings_window");
  }
</script>

<div class="popup">
  <div class="header">
    <span class="app-title">JIRA Focus</span>
    <button class="settings-btn" onclick={openSettings} title="設定">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
        <path d="M6.86 2.07a1 1 0 0 1 2.28 0l.12.56a1 1 0 0 0 1.33.6l.52-.22a1 1 0 0 1 1.14 1.62l-.4.4a1 1 0 0 0 0 1.33l.4.4a1 1 0 0 1-1.14 1.62l-.52-.22a1 1 0 0 0-1.33.6l-.12.56a1 1 0 0 1-2.28 0l-.12-.56a1 1 0 0 0-1.33-.6l-.52.22a1 1 0 0 1-1.14-1.62l.4-.4a1 1 0 0 0 0-1.33l-.4-.4A1 1 0 0 1 4.89 2.4l.52.22a1 1 0 0 0 1.33-.6l.12-.56z"/>
        <circle cx="8" cy="6" r="1.5"/>
      </svg>
    </button>
  </div>

  <FilterBar
    {filters}
    {lastFetched}
    {isLoading}
    onRefresh={handleRefresh}
    onFilterChange={handleFilterChange}
  />

  {#if errorMsg}
    <div class="error">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="7"/>
        <path d="M8 5v3.5M8 10.5v.5"/>
      </svg>
      <p>{errorMsg}</p>
    </div>
  {/if}

  <IssueList {issues} />
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
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px 0;
  }
  .app-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text-secondary);
    letter-spacing: -0.01em;
  }
  .settings-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
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
    background: #fff2f0;
    color: var(--color-error);
    font-size: 12px;
    line-height: 1.4;
    border-bottom: 1px solid #fecaca;
    max-height: 100px;
    overflow-y: auto;
  }
  .error svg {
    flex-shrink: 0;
    margin-top: 1px;
  }
  .error p {
    word-break: break-all;
  }
</style>
