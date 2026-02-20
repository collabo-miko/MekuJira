<script lang="ts">
  import type { NormalizedIssue, FocusState } from "$lib/types";
  import { openUrl } from "@tauri-apps/plugin-opener";
  import { getCurrentWindow } from "@tauri-apps/api/window";

  interface Props {
    focusState: FocusState;
    issues: NormalizedIssue[];
    onMinimize: () => void;
    onClose: () => void;
  }
  let { focusState, issues, onMinimize, onClose }: Props = $props();

  let focusedIssues = $derived(
    issues.filter((i) => focusState.focused_issues.includes(i.key))
  );

  let showTooltip = $state(false);

  function handleIssueClick(url: string) {
    openUrl(url);
  }

  function startDrag() {
    getCurrentWindow().startDragging();
  }
</script>

{#if focusState.widget_minimized}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="minimized"
    onclick={() => (showTooltip = !showTooltip)}
    onmouseenter={() => (showTooltip = true)}
    onmouseleave={() => (showTooltip = false)}
    onmousedown={startDrag}
  >
    📌
    {#if showTooltip}
      <div class="tooltip">
        {#each focusedIssues as issue}
          <div class="tooltip-item">{issue.key}: {issue.summary.slice(0, 20)}…</div>
        {/each}
      </div>
    {/if}
  </div>
{:else}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="widget" onmousedown={startDrag}>
    <div class="widget-content">
      {#each focusedIssues as issue (issue.key)}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="widget-issue" onclick={() => handleIssueClick(issue.url)}>
          <span class="pin">📌</span>
          <div class="widget-issue-text">
            <span class="widget-key">{issue.key}</span>
            <span class="widget-summary">{issue.summary}</span>
          </div>
        </div>
      {/each}
    </div>
    <div class="widget-actions">
      <button class="action-btn" onclick={onMinimize} title="最小化">−</button>
      <button class="action-btn" onclick={onClose} title="集中モード終了">×</button>
    </div>
  </div>
{/if}

<style>
  .widget {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    padding: 12px;
    cursor: move;
    min-width: 250px;
  }
  .widget-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .widget-issue {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: background 0.15s;
  }
  .widget-issue:hover {
    background: rgba(0, 0, 0, 0.05);
  }
  .pin {
    font-size: 14px;
    flex-shrink: 0;
  }
  .widget-issue-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .widget-key {
    font-size: 11px;
    font-weight: 600;
    color: #1a73e8;
  }
  .widget-summary {
    font-size: 12px;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .widget-actions {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    margin-top: 8px;
  }
  .action-btn {
    background: none;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 24px;
    height: 24px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .action-btn:hover {
    background: #f0f0f0;
  }
  .minimized {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    position: relative;
  }
  .tooltip {
    position: absolute;
    top: 44px;
    left: 0;
    background: white;
    border-radius: 6px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    padding: 8px;
    min-width: 200px;
    z-index: 100;
  }
  .tooltip-item {
    font-size: 12px;
    color: #333;
    padding: 4px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
