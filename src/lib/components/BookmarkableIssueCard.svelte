<script lang="ts">
  import type { NormalizedIssue } from "$lib/types";
  import StatusBadge from "./StatusBadge.svelte";
  import { openUrl } from "@tauri-apps/plugin-opener";

  interface Props {
    issue: NormalizedIssue;
    isBookmarked: boolean;
    onToggle: () => void;
  }
  let { issue, isBookmarked, onToggle }: Props = $props();

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

  function handleCheckbox(e: Event) {
    e.stopPropagation();
    onToggle();
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="card" onclick={handleClick}>
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <label class="checkbox-wrapper" onclick={(e) => e.stopPropagation()}>
    <input type="checkbox" checked={isBookmarked} onchange={handleCheckbox} />
  </label>
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
  .checkbox-wrapper {
    display: flex;
    align-items: center;
    padding-top: 2px;
    cursor: pointer;
    flex-shrink: 0;
  }
  .checkbox-wrapper input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--color-accent);
    cursor: pointer;
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
    font-size: 13px;
    font-weight: 600;
    color: var(--color-accent);
  }
  .priority {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--color-text-secondary);
  }
  .priority-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .summary {
    font-size: 14px;
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
    font-size: 12px;
    color: var(--color-text-tertiary);
  }
</style>
