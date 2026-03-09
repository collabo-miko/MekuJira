<script lang="ts">
  import type { NormalizedIssue } from "$lib/types";
  import StatusBadge from "./StatusBadge.svelte";
  import { openUrl } from "@tauri-apps/plugin-opener";

  interface Props {
    issue: NormalizedIssue;
  }
  let { issue }: Props = $props();

  const priorityColors: Record<string, string> = {
    Highest: "#ff3b30",
    High: "#ff9f0a",
    Medium: "#ffcc00",
    Low: "#34c759",
    Lowest: "#aeaeb2",
  };

  let dotColor = $derived(priorityColors[issue.priority] ?? "#aeaeb2");

  let dueDateDisplay = $derived.by(() => {
    if (!issue.due_date) return null;
    const [, m, d] = issue.due_date.split("-");
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const due = new Date(issue.due_date + "T00:00:00");
    const overdue = due < today;
    return { label: `${parseInt(m)}/${parseInt(d)}`, overdue };
  });

  function handleClick() {
    openUrl(issue.url);
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="card" onclick={handleClick}>
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
      {#if dueDateDisplay}
        <span class="due-date" class:overdue={dueDateDisplay.overdue}>{dueDateDisplay.label}</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .card {
    display: flex;
    align-items: flex-start;
    padding: 10px 14px;
    cursor: pointer;
    transition: background 0.12s ease;
    border-bottom: 1px solid var(--color-border);
  }
  .card:hover {
    background: var(--color-surface);
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
    font-size: 14px;
    font-weight: 600;
    color: var(--color-accent);
  }
  .priority {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
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
    font-size: 14px;
    color: var(--color-text-tertiary);
  }
  .due-date {
    font-size: 12px;
    color: var(--color-text-tertiary);
  }
  .due-date.overdue {
    color: #ff3b30;
    font-weight: 600;
  }
</style>
