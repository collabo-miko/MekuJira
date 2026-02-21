<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";

  // Root page redirects to popup
  onMount(() => {
    goto("/popup");
  });
</script>

<p>Loading...</p>
