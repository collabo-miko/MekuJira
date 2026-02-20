<script lang="ts">
  import type { NormalizedIssue } from "$lib/types";
  import StatusBadge from "./StatusBadge.svelte";
  import { openUrl } from "@tauri-apps/plugin-opener";

  interface Props {
    issue: NormalizedIssue;
    isFocused: boolean;
    onToggleFocus: (key: string) => void;
  }
  let { issue, isFocused, onToggleFocus }: Props = $props();

  const priorityColors: Record<string, string> = {
    Highest: "#ff3b30",
    High: "#ff9f0a",
    Medium: "#ffcc00",
    Low: "#34c759",
    Lowest: "#aeaeb2",
  };

  let dotColor = $derived(priorityColors[issue.priority] ?? "#aeaeb2");

  function handleClick() {
    openUrl(issue.url);
  }

  function handleToggle(e: Event) {
    e.stopPropagation();
    onToggleFocus(issue.key);
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="card" class:focused={isFocused} onclick={handleClick}>
  <button class="focus-btn" class:active={isFocused} onclick={handleToggle} title={isFocused ? "集中モードから外す" : "集中モードに追加"}>
    <svg width="14" height="14" viewBox="0 0 16 16" fill={isFocused ? "currentColor" : "none"} stroke="currentColor" stroke-width="1.5">
      <path d="M8 1.5l1.85 3.75 4.15.6-3 2.93.71 4.12L8 10.88 4.29 12.9l.71-4.12-3-2.93 4.15-.6z"/>
    </svg>
  </button>
  <div class="content">
    <div class="header">
      <span class="key">{issue.key}</span>
      <span class="priority">
        <span class="priority-dot" style="background: {dotColor};"></span>
        {issue.priority}
      </span>
    </div>
    <div class="summary">{issue.summary}</div>
    <div class="meta">
      <StatusBadge status={issue.status} category={issue.status_category} />
      {#if issue.assignee}
        <span class="assignee">{issue.assignee}</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .card {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 14px;
    cursor: pointer;
    transition: background 0.12s ease;
    border-bottom: 1px solid var(--color-border);
  }
  .card:hover {
    background: var(--color-surface);
  }
  .card.focused {
    background: #fefce8;
  }
  .card.focused:hover {
    background: #fef9c3;
  }
  .focus-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--color-text-tertiary);
    flex-shrink: 0;
    border-radius: var(--radius-sm);
    transition: all 0.12s ease;
  }
  .focus-btn:hover {
    background: rgba(0, 0, 0, 0.04);
    color: var(--color-text-secondary);
  }
  .focus-btn.active {
    color: #f59e0b;
  }
  .content {
    flex: 1;
    min-width: 0;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }
  .key {
    font-size: 12px;
    font-weight: 600;
    color: var(--color-accent);
  }
  .priority {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--color-text-secondary);
  }
  .priority-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .summary {
    font-size: 13px;
    color: var(--color-text-primary);
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 5px;
  }
  .assignee {
    font-size: 11px;
    color: var(--color-text-tertiary);
  }
</style>
