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
    // Load cached data first for instant display
    try {
      const cached = await getCachedIssues();
      if (cached.issues.length > 0) {
        issues = cached.issues;
        lastFetched = cached.last_fetched;
      }
    } catch {}

    // Load settings and focus state
    try {
      appSettings = await getSettings();
      focusStateData = await getFocusState();
    } catch {}

    // Then fetch fresh data
    await handleRefresh();

    // Listen for updates from polling
    listen<NormalizedIssue[]>("issues-updated", (event) => {
      issues = event.payload;
      lastFetched = new Date().toISOString();
    });

    listen<FocusState>("focus-state-updated", (event) => {
      focusStateData = event.payload;
    });

    // Refresh focus state when window gains focus
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
      <p>{errorMsg}</p>
    </div>
  {/if}

  <IssueList {issues} {focusedKeys} onToggleFocus={handleToggleFocus} />

  <div class="footer">
    <span class="app-name">JIRA Focus</span>
  </div>
</div>

<style>
  .popup {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
  .error {
    padding: 8px 12px;
    background: #fff3e0;
    color: #e65100;
    font-size: 12px;
    border-bottom: 1px solid #ffe0b2;
  }
  .footer {
    display: flex;
    justify-content: center;
    padding: 6px 12px;
    border-top: 1px solid #eee;
    background: #fafafa;
  }
  .app-name {
    font-size: 11px;
    color: #aaa;
  }
</style>
