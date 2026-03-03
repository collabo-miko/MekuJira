<script lang="ts">
  import type { BookmarkedIssue } from "$lib/types";
  import IssueCard from "./IssueCard.svelte";
  import { removeBookmark } from "$lib/api/bookmarks";

  interface Props {
    bookmarks: BookmarkedIssue[];
    onRefresh: () => void;
    isRefreshing: boolean;
  }
  let { bookmarks, onRefresh, isRefreshing }: Props = $props();

  async function handleRemoveBookmark(e: MouseEvent, issueKey: string) {
    e.stopPropagation();
    try {
      await removeBookmark(issueKey);
    } catch (err) {
      console.error("Failed to remove bookmark:", err);
    }
  }
</script>

<div class="tracking-view">
  {#if bookmarks.length === 0}
    <div class="empty">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-icon-muted)" stroke-width="1.5">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
      </svg>
      <p class="empty-title">追跡中の課題はありません</p>
      <p class="empty-hint">「対象」タブで課題をブックマークしてください</p>
    </div>
  {:else}
    <div class="toolbar">
      <span class="toolbar-label">{bookmarks.length} 件</span>
      <button class="refresh-btn" onclick={onRefresh} disabled={isRefreshing} title="ステータスを更新">
        <svg class="icon" class:spinning={isRefreshing} width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M13.65 2.35A8 8 0 1 0 16 8h-2a6 6 0 1 1-1.76-4.24L10 6h6V0l-2.35 2.35z" fill="currentColor"/>
        </svg>
      </button>
    </div>
    {#each bookmarks as bookmark (bookmark.key)}
      <div class="bookmark-row">
        <div class="card-wrapper">
          <IssueCard issue={bookmark} />
        </div>
        <button
          class="unbookmark-btn"
          onclick={(e) => handleRemoveBookmark(e, bookmark.key)}
          title="ブックマーク解除"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M4 4l8 8M12 4l-8 8"/>
          </svg>
        </button>
      </div>
    {/each}
  {/if}
</div>

<style>
  .tracking-view {
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
  .refresh-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
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
  .bookmark-row {
    display: flex;
    align-items: stretch;
    position: relative;
  }
  .card-wrapper {
    flex: 1;
    min-width: 0;
  }
  .unbookmark-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    padding: 0;
    border: none;
    background: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    opacity: 0;
    transition: all 0.12s ease;
    flex-shrink: 0;
  }
  .bookmark-row:hover .unbookmark-btn {
    opacity: 1;
  }
  .unbookmark-btn:hover {
    color: var(--color-error);
  }
</style>
