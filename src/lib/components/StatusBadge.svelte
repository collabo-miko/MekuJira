<script lang="ts">
  interface Props {
    status: string;
    category: string;
  }
  let { status, category }: Props = $props();

  const categoryColors: Record<string, { bg: string; text: string }> = {
    new: { bg: "#e3f2fd", text: "#1565c0" },
    indeterminate: { bg: "#fff3e0", text: "#e65100" },
    done: { bg: "#e8f5e9", text: "#2e7d32" },
  };

  let colors = $derived(categoryColors[category] ?? { bg: "#f5f5f5", text: "#616161" });
</script>

<span
  class="badge"
  style="background-color: {colors.bg}; color: {colors.text};"
>
  {status}
</span>

<style>
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
  }
</style>
