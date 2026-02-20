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
    <span class="label">🔍</span>
    <select class="filter-select" onchange={handleSelect} value={activeFilter?.id ?? ""}>
      {#each filters as filter}
        <option value={filter.id}>{filter.name}</option>
      {/each}
    </select>
  </div>
  <div class="status-row">
    <button class="refresh-btn" onclick={onRefresh} disabled={isLoading}>
      {isLoading ? "⏳" : "↻"}
    </button>
    <span class="last-updated">最終更新: {formatTime(lastFetched)}</span>
  </div>
</div>

<style>
  .filter-bar {
    padding: 10px 12px;
    border-bottom: 1px solid #e0e0e0;
    background: #fafafa;
  }
  .filter-row {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .label {
    font-size: 14px;
  }
  .filter-select {
    flex: 1;
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    background: white;
    cursor: pointer;
  }
  .status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
  }
  .refresh-btn {
    background: none;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 8px;
    cursor: pointer;
    font-size: 14px;
  }
  .refresh-btn:hover:not(:disabled) {
    background: #e8e8e8;
  }
  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .last-updated {
    font-size: 11px;
    color: #888;
  }
</style>
