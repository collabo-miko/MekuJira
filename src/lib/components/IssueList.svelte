<script lang="ts">
  import type { NormalizedIssue } from "$lib/types";
  import IssueCard from "./IssueCard.svelte";

  interface Props {
    issues: NormalizedIssue[];
    focusedKeys: string[];
    onToggleFocus: (key: string) => void;
  }
  let { issues, focusedKeys, onToggleFocus }: Props = $props();
</script>

<div class="issue-list">
  {#if issues.length === 0}
    <div class="empty">
      <p>課題が見つかりません</p>
      <p class="hint">フィルターを変更するか、JQL設定を確認してください</p>
    </div>
  {:else}
    {#each issues as issue (issue.key)}
      <IssueCard
        {issue}
        isFocused={focusedKeys.includes(issue.key)}
        {onToggleFocus}
      />
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
    padding: 40px 20px;
    color: #888;
  }
  .empty p {
    margin: 4px 0;
    font-size: 14px;
  }
  .hint {
    font-size: 12px !important;
    color: #aaa;
  }
</style>
