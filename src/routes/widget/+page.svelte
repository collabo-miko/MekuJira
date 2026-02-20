<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import FocusWidget from "$lib/components/FocusWidget.svelte";
  import { getFocusState, setWidgetMinimized } from "$lib/api/focus";
  import { getCachedIssues } from "$lib/api/jira";
  import type { NormalizedIssue, FocusState } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";

  let focusStateData = $state<FocusState>({
    focused_issues: [],
    widget_visible: false,
    widget_minimized: false,
    widget_position: null,
  });
  let issues = $state<NormalizedIssue[]>([]);

  onMount(async () => {
    try {
      focusStateData = await getFocusState();
      const cached = await getCachedIssues();
      issues = cached.issues;
    } catch {}

    listen<FocusState>("focus-state-updated", (event) => {
      focusStateData = event.payload;
      const win = getCurrentWindow();
      if (event.payload.widget_visible) {
        win.show();
      } else {
        win.hide();
      }
    });

    listen<NormalizedIssue[]>("issues-updated", (event) => {
      issues = event.payload;
    });

    // Show/hide based on initial state
    const win = getCurrentWindow();
    if (focusStateData.widget_visible) {
      await win.show();
    }
  });

  async function handleMinimize() {
    await setWidgetMinimized(!focusStateData.widget_minimized);
  }

  async function handleClose() {
    const win = getCurrentWindow();
    await win.hide();
  }
</script>

<div class="widget-container">
  <FocusWidget
    focusState={focusStateData}
    {issues}
    onMinimize={handleMinimize}
    onClose={handleClose}
  />
</div>

<style>
  .widget-container {
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    min-height: 100vh;
    padding: 8px;
  }
</style>
