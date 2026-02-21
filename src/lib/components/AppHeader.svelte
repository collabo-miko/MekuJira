<script lang="ts">
  import type { ViewMode } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";
  import { invoke } from "@tauri-apps/api/core";

  interface Props {
    viewMode: ViewMode;
    onModeChange: (mode: ViewMode) => void;
  }
  let { viewMode, onModeChange }: Props = $props();

  function openSettings() {
    invoke("open_settings_window");
  }

  function startDrag() {
    getCurrentWindow().startDragging();
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="header" onmousedown={startDrag}>
  <span class="app-title">JIRA Focus</span>
  <div class="tabs" onmousedown={(e) => e.stopPropagation()}>
    <button
      class="tab"
      class:active={viewMode === "tracking"}
      onclick={() => onModeChange("tracking")}
    >
      追跡
    </button>
    <button
      class="tab"
      class:active={viewMode === "dashboard"}
      onclick={() => onModeChange("dashboard")}
    >
      対象
    </button>
  </div>
  <button
    class="settings-btn"
    onmousedown={(e) => e.stopPropagation()}
    onclick={openSettings}
    title="設定"
  >
    <svg
      width="16"
      height="16"
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
</div>

<style>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px 8px;
    cursor: grab;
    -webkit-app-region: drag;
    gap: 8px;
  }
  .header:active {
    cursor: grabbing;
  }
  .app-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text-secondary);
    letter-spacing: -0.01em;
    flex-shrink: 0;
  }
  .tabs {
    display: flex;
    gap: 2px;
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    padding: 2px;
    -webkit-app-region: no-drag;
  }
  .tab {
    padding: 4px 14px;
    border: none;
    border-radius: calc(var(--radius-sm) - 2px);
    background: none;
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    color: var(--color-text-tertiary);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }
  .tab:hover {
    color: var(--color-text-secondary);
  }
  .tab.active {
    background: #fff;
    color: var(--color-text-primary);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
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
    -webkit-app-region: no-drag;
    flex-shrink: 0;
  }
  .settings-btn:hover {
    background: var(--color-surface);
    color: var(--color-text-primary);
  }
</style>
