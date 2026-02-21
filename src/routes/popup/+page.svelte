<script lang="ts">
  import { onMount } from "svelte";
  import { listen } from "@tauri-apps/api/event";
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

  onMount(async () => {
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
  <AppHeader />
  <TrackingView {bookmarks} />
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
