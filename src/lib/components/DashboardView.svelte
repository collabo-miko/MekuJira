<script lang="ts">
  import type { JqlFilter, NormalizedIssue, FilterIssuesMap } from "$lib/types";
  import DashboardSection from "./DashboardSection.svelte";
  import { refreshAllFilters } from "$lib/api/jira";

  interface Props {
    filters: JqlFilter[];
    filterIssues: FilterIssuesMap;
    bookmarkedKeys: Set<string>;
    isLoading: boolean;
    onRefresh: () => void;
    onToggleBookmark: (issue: NormalizedIssue, filterId: string) => void;
  }
  let { filters, filterIssues, bookmarkedKeys, isLoading, onRefresh, onToggleBookmark }: Props = $props();

  let enabledFilters = $derived(filters.filter((f) => f.enabled));
</script>

<div class="dashboard-view">
  <div class="toolbar">
    <span class="toolbar-label">{enabledFilters.length} フィルター</span>
    <button class="refresh-btn" onclick={onRefresh} disabled={isLoading} title="全フィルター更新">
      <svg class="icon" class:spinning={isLoading} width="14" height="14" viewBox="0 0 16 16" fill="none">
        <path d="M13.65 2.35A8 8 0 1 0 16 8h-2a6 6 0 1 1-1.76-4.24L10 6h6V0l-2.35 2.35z" fill="currentColor"/>
      </svg>
    </button>
  </div>

  {#if enabledFilters.length === 0}
    <div class="empty">
      <p class="empty-title">有効なフィルターがありません</p>
      <p class="empty-hint">設定画面でフィルターを有効にしてください</p>
    </div>
  {:else}
    <div class="sections">
      {#each enabledFilters as filter (filter.id)}
        <DashboardSection
          {filter}
          issues={filterIssues[filter.id] ?? []}
          {bookmarkedKeys}
          {onToggleBookmark}
        />
      {/each}
    </div>
  {/if}
</div>

<style>
  .dashboard-view {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 14px;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }
  .toolbar-label {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
  .refresh-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    cursor: pointer;
    color: var(--color-text-secondary);
    transition: all 0.15s ease;
  }
  .refresh-btn:hover:not(:disabled) {
    background: var(--color-surface);
    color: var(--color-text-primary);
  }
  .refresh-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .icon {
    transition: transform 0.3s ease;
  }
  .spinning {
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .sections {
    flex: 1;
    overflow-y: auto;
  }
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    gap: 8px;
  }
  .empty-title {
    font-size: 15px;
    font-weight: 500;
    color: var(--color-text-secondary);
  }
  .empty-hint {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
</style>
