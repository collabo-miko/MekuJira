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

  let searchQuery = $state("");
  let searchInput: HTMLInputElement | undefined = $state();

  function matchesQuery(issue: NormalizedIssue, query: string): boolean {
    const q = query.toLowerCase();
    return (
      issue.key.toLowerCase().includes(q) ||
      issue.summary.toLowerCase().includes(q) ||
      issue.assignee.toLowerCase().includes(q) ||
      issue.status.toLowerCase().includes(q)
    );
  }

  let filteredIssues: FilterIssuesMap = $derived.by(() => {
    if (!searchQuery.trim()) return filterIssues;
    const query = searchQuery.trim();
    const result: FilterIssuesMap = {};
    for (const [filterId, issues] of Object.entries(filterIssues)) {
      result[filterId] = issues.filter((issue) => matchesQuery(issue, query));
    }
    return result;
  });

  let visibleFilters = $derived(
    enabledFilters.filter((f) => (filteredIssues[f.id] ?? []).length > 0 || !searchQuery.trim())
  );

  let hasNoResults = $derived(
    searchQuery.trim() !== "" && enabledFilters.every((f) => (filteredIssues[f.id] ?? []).length === 0)
  );

  function clearSearch() {
    searchQuery = "";
    searchInput?.focus();
  }

  function handleSearchKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      clearSearch();
    }
  }
</script>

<div class="dashboard-view">
  <div class="toolbar">
    <span class="toolbar-label">{enabledFilters.length} フィルター</span>
    <div class="search-box">
      <svg class="search-icon" width="14" height="14" viewBox="0 0 16 16" fill="none">
        <path d="M11.5 7a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Zm-1.06 3.85a6 6 0 1 1 .71-.71l3.86 3.85-.71.71-3.86-3.85Z" fill="currentColor"/>
      </svg>
      <input
        bind:this={searchInput}
        bind:value={searchQuery}
        onkeydown={handleSearchKeydown}
        class="search-input"
        type="text"
        placeholder="課題を検索..."
      />
      {#if searchQuery}
        <button class="search-clear" onclick={clearSearch} title="検索をクリア">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M12.2 4.5 8.7 8l3.5 3.5-.7.7L8 8.7l-3.5 3.5-.7-.7L7.3 8 3.8 4.5l.7-.7L8 7.3l3.5-3.5.7.7Z" fill="currentColor"/>
          </svg>
        </button>
      {/if}
    </div>
    <button class="refresh-btn" onclick={onRefresh} disabled={isLoading} title="全フィルター更新">
      <svg class="icon" class:spinning={isLoading} width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M13.65 2.35A8 8 0 1 0 16 8h-2a6 6 0 1 1-1.76-4.24L10 6h6V0l-2.35 2.35z" fill="currentColor"/>
      </svg>
    </button>
  </div>

  {#if enabledFilters.length === 0}
    <div class="empty">
      <p class="empty-title">有効なフィルターがありません</p>
      <p class="empty-hint">設定画面でフィルターを有効にしてください</p>
    </div>
  {:else if hasNoResults}
    <div class="empty">
      <p class="empty-title">該当する課題が見つかりません</p>
      <p class="empty-hint">別のキーワードで検索してください</p>
    </div>
  {:else}
    <div class="sections">
      {#each visibleFilters as filter (filter.id)}
        <DashboardSection
          {filter}
          issues={filteredIssues[filter.id] ?? []}
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
    font-size: 14px;
    color: var(--color-text-tertiary);
    flex-shrink: 0;
  }
  .search-box {
    display: flex;
    align-items: center;
    flex: 1;
    max-width: 480px;
    margin: 0 8px;
    padding: 0 8px;
    height: 28px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    transition: border-color 0.15s ease;
  }
  .search-box:focus-within {
    border-color: var(--color-text-tertiary);
  }
  .search-icon {
    flex-shrink: 0;
    color: var(--color-text-tertiary);
  }
  .search-input {
    flex: 1;
    border: none;
    outline: none;
    background: none;
    font-size: 13px;
    color: var(--color-text-primary);
    padding: 0 6px;
    min-width: 0;
  }
  .search-input::placeholder {
    color: var(--color-text-tertiary);
  }
  .search-clear {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    padding: 0;
    background: none;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    color: var(--color-text-tertiary);
    flex-shrink: 0;
    transition: all 0.15s ease;
  }
  .search-clear:hover {
    color: var(--color-text-primary);
    background: var(--color-border);
  }
  .refresh-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
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
    font-size: 14px;
    color: var(--color-text-tertiary);
  }
</style>
