<script lang="ts">
  import type { JqlFilter } from "$lib/types";

  interface Props {
    filters: JqlFilter[];
    lastFetched: string | null;
    isLoading: boolean;
    onRefresh: () => void;
    onFilterChange: (filterId: string) => void;
  }
  let { filters, lastFetched, isLoading, onRefresh, onFilterChange }: Props = $props();

  let activeFilter = $derived(filters.find((f) => f.is_active));

  function formatTime(isoString: string | null): string {
    if (!isoString) return "--:--";
    const date = new Date(isoString);
    return date.toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" });
  }

  function handleSelect(e: Event) {
    const target = e.target as HTMLSelectElement;
    onFilterChange(target.value);
  }
</script>

<div class="filter-bar">
  <div class="filter-row">
    <select class="filter-select" onchange={handleSelect} value={activeFilter?.id ?? ""}>
      {#each filters as filter}
        <option value={filter.id}>{filter.name}</option>
      {/each}
    </select>
    <button class="refresh-btn" onclick={onRefresh} disabled={isLoading} title="更新">
      <svg class="icon" class:spinning={isLoading} width="14" height="14" viewBox="0 0 16 16" fill="none">
        <path d="M13.65 2.35A8 8 0 1 0 16 8h-2a6 6 0 1 1-1.76-4.24L10 6h6V0l-2.35 2.35z" fill="currentColor"/>
      </svg>
    </button>
  </div>
  <span class="last-updated">{formatTime(lastFetched)}</span>
</div>

<style>
  .filter-bar {
    padding: 10px 14px 8px;
    background: var(--color-bg);
    border-bottom: 1px solid var(--color-border);
  }
  .filter-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .filter-select {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-family: inherit;
    background: var(--color-surface);
    color: var(--color-text-primary);
    cursor: pointer;
    outline: none;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%236e6e73' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 28px;
  }
  .filter-select:focus {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
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
    flex-shrink: 0;
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
  .last-updated {
    display: block;
    font-size: 11px;
    color: var(--color-text-tertiary);
    margin-top: 4px;
  }
</style>
