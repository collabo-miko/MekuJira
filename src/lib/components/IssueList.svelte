<script lang="ts">
  import type { NormalizedIssue } from "$lib/types";
  import IssueCard from "./IssueCard.svelte";

  interface Props {
    issues: NormalizedIssue[];
  }
  let { issues }: Props = $props();
</script>

<div class="issue-list">
  {#if issues.length === 0}
    <div class="empty">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-icon-muted)" stroke-width="1.5">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="1"/>
      </svg>
      <p class="empty-title">課題が見つかりません</p>
      <p class="empty-hint">フィルターを変更するか、JQL設定を確認してください</p>
    </div>
  {:else}
    {#each issues as issue (issue.key)}
      <IssueCard {issue} />
    {/each}
  {/if}
</div>

<style>
  .issue-list {
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
