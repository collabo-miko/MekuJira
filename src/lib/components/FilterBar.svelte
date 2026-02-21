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
  let isOpen = $state(false);
  let dropdownRef = $state<HTMLDivElement | null>(null);

  function formatTime(isoString: string | null): string {
    if (!isoString) return "--:--";
    const date = new Date(isoString);
    return date.toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" });
  }

  function toggleDropdown() {
    isOpen = !isOpen;
  }

  function selectFilter(id: string) {
    isOpen = false;
    onFilterChange(id);
  }

  function handleClickOutside(e: MouseEvent) {
    if (dropdownRef && !dropdownRef.contains(e.target as Node)) {
      isOpen = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      isOpen = false;
    }
  }
</script>

<svelte:document onclick={handleClickOutside} onkeydown={handleKeydown} />

<div class="filter-bar">
  <div class="filter-row">
    <div class="dropdown" bind:this={dropdownRef}>
      <button class="dropdown-trigger" onclick={toggleDropdown}>
        <span class="dropdown-label">{activeFilter?.name ?? "フィルター"}</span>
        <svg class="chevron" class:open={isOpen} width="10" height="6" viewBox="0 0 10 6" fill="none">
          <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      {#if isOpen}
        <div class="dropdown-menu">
          {#each filters as filter (filter.id)}
            <button
              class="dropdown-item"
              class:active={filter.is_active}
              onclick={() => selectFilter(filter.id)}
            >
              <span class="item-check">
                {#if filter.is_active}
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2.5 6l2.5 2.5 4.5-5"/>
                  </svg>
                {/if}
              </span>
              <span class="item-label">{filter.name}</span>
            </button>
          {/each}
        </div>
      {/if}
    </div>
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
  .dropdown {
    flex: 1;
    position: relative;
  }
  .dropdown-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 6px 10px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-family: inherit;
    background: var(--color-surface);
    color: var(--color-text-primary);
    cursor: pointer;
    outline: none;
    transition: all 0.15s ease;
    text-align: left;
  }
  .dropdown-trigger:hover {
    border-color: #c8c8cc;
  }
  .dropdown-trigger:focus {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
  }
  .dropdown-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chevron {
    flex-shrink: 0;
    color: var(--color-text-tertiary);
    transition: transform 0.2s ease;
  }
  .chevron.open {
    transform: rotate(180deg);
  }
  .dropdown-menu {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: var(--radius-sm);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.06);
    padding: 4px;
    z-index: 100;
    max-height: 200px;
    overflow-y: auto;
    animation: dropdown-in 0.12s ease-out;
  }
  @keyframes dropdown-in {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  .dropdown-item {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding: 7px 8px;
    border: none;
    border-radius: 4px;
    background: none;
    font-size: 13px;
    font-family: inherit;
    color: var(--color-text-primary);
    cursor: pointer;
    text-align: left;
    transition: background 0.1s ease;
  }
  .dropdown-item:hover {
    background: var(--color-surface);
  }
  .dropdown-item.active {
    color: var(--color-accent);
    font-weight: 500;
  }
  .item-check {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    flex-shrink: 0;
    color: var(--color-accent);
  }
  .item-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
