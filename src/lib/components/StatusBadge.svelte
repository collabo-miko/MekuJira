<script lang="ts">
  interface Props {
    status: string;
    category: string;
  }
  let { status, category }: Props = $props();

  const categoryVarMap: Record<string, string> = {
    new: "new",
    indeterminate: "progress",
    done: "done",
  };

  let varPrefix = $derived(categoryVarMap[category] ?? "default");
</script>

<span
  class="badge"
  style="background: var(--badge-{varPrefix}-bg); color: var(--badge-{varPrefix}-text);"
>
  <span class="dot" style="background: var(--badge-{varPrefix}-dot);"></span>
  {status}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px 2px 6px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    letter-spacing: 0;
  }
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }
</style>
