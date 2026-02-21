<script lang="ts">
  import type { JqlFilter, NormalizedIssue } from "$lib/types";
  import BookmarkableIssueCard from "./BookmarkableIssueCard.svelte";

  interface Props {
    filter: JqlFilter;
    issues: NormalizedIssue[];
    bookmarkedKeys: Set<string>;
    onToggleBookmark: (issue: NormalizedIssue, filterId: string) => void;
  }
  let { filter, issues, bookmarkedKeys, onToggleBookmark }: Props = $props();

  let isOpen = $state(true);

  function toggle() {
    isOpen = !isOpen;
  }
</script>

<div class="section">
  <button class="section-header" onclick={toggle}>
    <span class="chevron" class:open={isOpen}>
      <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
        <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </span>
    <span class="section-name">{filter.name}</span>
    <span class="issue-count">({issues.length})</span>
  </button>
  {#if isOpen}
    <div class="section-body">
      {#if issues.length === 0}
        <div class="empty-section">課題なし</div>
      {:else}
        {#each issues as issue (issue.key)}
          <BookmarkableIssueCard
            {issue}
            isBookmarked={bookmarkedKeys.has(issue.key)}
            onToggle={() => onToggleBookmark(issue, filter.id)}
          />
        {/each}
      {/if}
    </div>
  {/if}
</div>

<style>
  .section {
    border-bottom: 1px solid var(--color-border);
  }
  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding: 10px 14px;
    border: none;
    background: var(--color-surface);
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-primary);
    cursor: pointer;
    text-align: left;
    transition: background 0.12s ease;
  }
  .section-header:hover {
    background: var(--color-surface-hover);
  }
  .chevron {
    display: flex;
    align-items: center;
    color: var(--color-text-tertiary);
    transition: transform 0.2s ease;
    transform: rotate(-90deg);
  }
  .chevron.open {
    transform: rotate(0deg);
  }
  .section-name {
    flex: 1;
  }
  .issue-count {
    font-size: 13px;
    font-weight: 400;
    color: var(--color-text-tertiary);
  }
  .section-body {
    overflow: hidden;
  }
  .empty-section {
    padding: 16px 14px;
    font-size: 13px;
    color: var(--color-text-tertiary);
    text-align: center;
  }
</style>
