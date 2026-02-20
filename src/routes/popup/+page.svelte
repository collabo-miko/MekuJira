<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import FilterBar from "$lib/components/FilterBar.svelte";
  import IssueList from "$lib/components/IssueList.svelte";
  import { getCachedIssues, refreshIssues } from "$lib/api/jira";
  import { getSettings, saveSettings } from "$lib/api/settings";
  import { getFocusState, toggleFocusIssue } from "$lib/api/focus";
  import type { NormalizedIssue, AppSettings, FocusState } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";

  let issues = $state<NormalizedIssue[]>([]);
  let isLoading = $state(false);
  let lastFetched = $state<string | null>(null);
  let appSettings = $state<AppSettings | null>(null);
  let focusStateData = $state<FocusState>({
    focused_issues: [],
    widget_visible: false,
    widget_minimized: false,
    widget_position: null,
  });
  let errorMsg = $state<string | null>(null);

  let filters = $derived(appSettings?.filters ?? []);
  let focusedKeys = $derived(focusStateData.focused_issues);

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
      focusStateData = await getFocusState();
    } catch {}

    await handleRefresh();

    listen<NormalizedIssue[]>("issues-updated", (event) => {
      issues = event.payload;
      lastFetched = new Date().toISOString();
    });

    listen<FocusState>("focus-state-updated", (event) => {
      focusStateData = event.payload;
    });

    const currentWindow = getCurrentWindow();
    currentWindow.onFocusChanged(async ({ payload: focused }) => {
      if (focused) {
        focusStateData = await getFocusState();
      }
    });
  });

  async function handleRefresh() {
    if (!appSettings?.jira.domain || !appSettings?.jira.email) {
      errorMsg = "JIRA接続情報が設定されていません。右クリックメニューから設定画面を開いてください。";
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

  async function handleToggleFocus(key: string) {
    try {
      focusStateData = await toggleFocusIssue(key);
    } catch (e) {
      console.error("Failed to toggle focus:", e);
    }
  }
</script>

<div class="popup">
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

  <IssueList {issues} {focusedKeys} onToggleFocus={handleToggleFocus} />
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
