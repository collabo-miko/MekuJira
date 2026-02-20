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

  const priorityIcons: Record<string, string> = {
    Highest: "🔴",
    High: "🟠",
    Medium: "🟡",
    Low: "🟢",
    Lowest: "⚪",
  };

  let priorityIcon = $derived(priorityIcons[issue.priority] ?? "⚪");

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
<div class="card" onclick={handleClick}>
  <button class="star" onclick={handleToggle} title={isFocused ? "集中モードから外す" : "集中モードに追加"}>
    {isFocused ? "⭐" : "☆"}
  </button>
  <div class="content">
    <div class="header">
      <span class="key">{issue.key}</span>
      <span class="priority">{priorityIcon} {issue.priority}</span>
    </div>
    <div class="summary">{issue.summary}</div>
    <div class="footer">
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
    padding: 10px 12px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.15s;
  }
  .card:hover {
    background-color: #f8f9fa;
  }
  .star {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    padding: 2px;
    line-height: 1;
    flex-shrink: 0;
  }
  .content {
    flex: 1;
    min-width: 0;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
  }
  .key {
    font-size: 12px;
    font-weight: 600;
    color: #1a73e8;
  }
  .priority {
    font-size: 11px;
    color: #666;
  }
  .summary {
    font-size: 13px;
    color: #333;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .footer {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
  }
  .assignee {
    font-size: 11px;
    color: #888;
  }
</style>
