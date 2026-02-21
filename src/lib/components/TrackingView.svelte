<script lang="ts">
  import type { BookmarkedIssue } from "$lib/types";
  import IssueCard from "./IssueCard.svelte";
  import { removeBookmark } from "$lib/api/bookmarks";

  interface Props {
    bookmarks: BookmarkedIssue[];
  }
  let { bookmarks }: Props = $props();

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
          <svg width="12" height="12" viewBox="0 0 12 12" stroke="currentColor" stroke-width="1.5" fill="none">
            <path d="M3 3l6 6M9 3l-6 6"/>
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
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
  }
  .empty-hint {
    font-size: 12px;
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
    width: 28px;
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
