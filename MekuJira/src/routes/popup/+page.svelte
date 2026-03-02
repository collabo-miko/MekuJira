<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import { check } from "@tauri-apps/plugin-updater";
  import AppHeader from "$lib/components/AppHeader.svelte";
  import TrackingView from "$lib/components/TrackingView.svelte";
  import { getBookmarks } from "$lib/api/bookmarks";
  import { getSettings } from "$lib/api/settings";
  import type {
    BookmarkedIssue,
    AppSettings,
  } from "$lib/types";
  import { getCurrentWindow } from "@tauri-apps/api/window";

  let appSettings = $state<AppSettings | null>(null);
  let bookmarks = $state<BookmarkedIssue[]>([]);
  let collapsed = $state(false);

  async function checkForUpdates() {
    try {
      const update = await check();
      if (update) {
        console.log(`Update available: ${update.version}`);
        await update.downloadAndInstall();
      }
    } catch (e) {
      console.warn("Update check failed:", e);
    }
  }

  onMount(async () => {
    checkForUpdates();

    try {
      bookmarks = await getBookmarks();
    } catch {}

    try {
      appSettings = await getSettings();
    } catch {}

    listen("bookmarks-updated", async () => {
      try {
        bookmarks = await getBookmarks();
      } catch {}
    });

    // フォーカスを得たときにデータを更新
    // フォーカス外の自動非表示はNSPanel側で処理
    const currentWindow = getCurrentWindow();
    currentWindow.onFocusChanged(async ({ payload: focused }) => {
      if (focused) {
        try {
          appSettings = await getSettings();
          bookmarks = await getBookmarks();
        } catch {}
      }
    });
  });
</script>

<div class="popup">
  <AppHeader bind:collapsed />
  {#if !collapsed}
    <TrackingView {bookmarks} />
  {/if}
</div>

<style>
  .popup {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--color-bg);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
</style>
