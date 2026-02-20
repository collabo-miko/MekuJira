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
    <svg width="16" height="16" viewBox="0 0 16 16" fill="#f59e0b" stroke="#f59e0b" stroke-width="1">
      <path d="M8 1.5l1.85 3.75 4.15.6-3 2.93.71 4.12L8 10.88 4.29 12.9l.71-4.12-3-2.93 4.15-.6z"/>
    </svg>
    {#if showTooltip}
      <div class="tooltip">
        {#each focusedIssues as issue}
          <div class="tooltip-item">
            <span class="tooltip-key">{issue.key}</span>
            <span class="tooltip-summary">{issue.summary.slice(0, 30)}</span>
          </div>
        {/each}
      </div>
    {/if}
  </div>
{:else}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="widget" onmousedown={startDrag}>
    <div class="widget-header">
      <span class="widget-title">Focus</span>
      <div class="widget-actions">
        <button class="action-btn" onclick={onMinimize} title="最小化">
          <svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M2 5h6"/>
          </svg>
        </button>
        <button class="action-btn close" onclick={onClose} title="閉じる">
          <svg width="10" height="10" viewBox="0 0 10 10" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M2 2l6 6M8 2l-6 6"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="widget-content">
      {#each focusedIssues as issue (issue.key)}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="widget-issue" onclick={() => handleIssueClick(issue.url)}>
          <div class="widget-issue-text">
            <span class="widget-key">{issue.key}</span>
            <span class="widget-summary">{issue.summary}</span>
          </div>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .widget {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
    cursor: move;
    min-width: 240px;
    overflow: hidden;
  }
  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  }
  .widget-title {
    font-size: 11px;
    font-weight: 600;
    color: #6e6e73;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .widget-actions {
    display: flex;
    gap: 4px;
  }
  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background: none;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    color: #aeaeb2;
    transition: all 0.12s ease;
  }
  .action-btn:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #6e6e73;
  }
  .action-btn.close:hover {
    background: rgba(255, 59, 48, 0.1);
    color: #ff3b30;
  }
  .widget-content {
    padding: 4px 0;
  }
  .widget-issue {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    cursor: pointer;
    padding: 6px 12px;
    transition: background 0.12s ease;
  }
  .widget-issue:hover {
    background: rgba(0, 0, 0, 0.03);
  }
  .widget-issue-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
    gap: 1px;
  }
  .widget-key {
    font-size: 11px;
    font-weight: 600;
    color: #0071e3;
  }
  .widget-summary {
    font-size: 12px;
    color: #1d1d1f;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .minimized {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: relative;
    transition: transform 0.12s ease;
  }
  .minimized:hover {
    transform: scale(1.05);
  }
  .tooltip {
    position: absolute;
    top: 40px;
    left: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
    padding: 8px;
    min-width: 200px;
    z-index: 100;
  }
  .tooltip-item {
    display: flex;
    gap: 6px;
    padding: 3px 0;
    overflow: hidden;
  }
  .tooltip-key {
    font-size: 11px;
    font-weight: 600;
    color: #0071e3;
    flex-shrink: 0;
  }
  .tooltip-summary {
    font-size: 11px;
    color: #6e6e73;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
