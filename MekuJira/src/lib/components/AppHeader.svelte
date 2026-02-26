<script lang="ts">
  import { getCurrentWindow } from "@tauri-apps/api/window";
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";

  function openDashboard() {
    invoke("open_dashboard_window");
  }

  function openSettings() {
    invoke("open_settings_window");
  }

  let pinned = $state(false);

  onMount(async () => {
    pinned = await invoke<boolean>("get_pinned");
  });

  function togglePin() {
    pinned = !pinned;
    invoke("set_pinned", { pinned });
  }

  function startDrag() {
    getCurrentWindow().startDragging();
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="header" onmousedown={startDrag}>
  <span class="app-title">MekuJira</span>
  <div class="actions" onmousedown={(e) => e.stopPropagation()}>
    <button
      class="icon-btn"
      class:pin-active={pinned}
      onclick={togglePin}
      title={pinned ? "固定解除" : "固定表示"}
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill={pinned ? "currentColor" : "none"}
        stroke="currentColor"
        stroke-width="1.4"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M9.5 2.5L13.5 6.5L10 10L9.5 12.5L3.5 6.5L6 6L9.5 2.5Z" />
        <path d="M3.5 12.5L6 10" />
      </svg>
    </button>
    <button
      class="icon-btn"
      onclick={openDashboard}
      title="対象課題一覧"
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
        <rect x="2" y="2" width="12" height="12" rx="2" />
        <path d="M5 6h6M5 8.5h6M5 11h4" />
      </svg>
    </button>
    <button
      class="icon-btn"
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
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-secondary);
    letter-spacing: -0.01em;
    flex-shrink: 0;
  }
  .actions {
    display: flex;
    gap: 2px;
    -webkit-app-region: no-drag;
  }
  .icon-btn {
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
  .icon-btn:hover {
    background: var(--color-surface);
    color: var(--color-text-primary);
  }
  .icon-btn.pin-active {
    color: var(--color-accent);
  }
</style>
