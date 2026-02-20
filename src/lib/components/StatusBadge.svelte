<script lang="ts">
  interface Props {
    status: string;
    category: string;
  }
  let { status, category }: Props = $props();

  const categoryStyles: Record<string, { bg: string; text: string; dot: string }> = {
    new: { bg: "#f0f4ff", text: "#3b5998", dot: "#4a90d9" },
    indeterminate: { bg: "#fff8f0", text: "#b45309", dot: "#f59e0b" },
    done: { bg: "#f0fdf4", text: "#15803d", dot: "#22c55e" },
  };

  let style = $derived(categoryStyles[category] ?? { bg: "#f5f5f5", text: "#6e6e73", dot: "#aeaeb2" });
</script>

<span
  class="badge"
  style="background: {style.bg}; color: {style.text};"
>
  <span class="dot" style="background: {style.dot};"></span>
  {status}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px 2px 6px;
    border-radius: 100px;
    font-size: 11px;
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
