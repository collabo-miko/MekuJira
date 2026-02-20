<script lang="ts">
  import { onMount } from "svelte";
  import { getSettings, saveSettings, saveApiToken, hasApiToken } from "$lib/api/settings";
  import { testConnection } from "$lib/api/jira";
  import type { AppSettings } from "$lib/types";

  let settings = $state<AppSettings>({
    jira: { domain: "", email: "" },
    filters: [],
    polling_interval_secs: 60,
    auto_start: false,
  });
  let apiToken = $state("");
  let hasTokenState = $state(false);
  let isTesting = $state(false);
  let isSaving = $state(false);
  let testResult = $state<{ success: boolean; message: string } | null>(null);
  let saveMessage = $state<string | null>(null);

  let newFilterName = $state("");
  let newFilterJql = $state("");

  onMount(async () => {
    try {
      settings = await getSettings();
      hasTokenState = await hasApiToken();
    } catch (e) {
      console.error("Failed to load settings:", e);
    }
  });

  async function handleSave() {
    isSaving = true;
    saveMessage = null;
    try {
      if (apiToken) {
        await saveApiToken(apiToken);
        hasTokenState = true;
        apiToken = "";
      }
      await saveSettings(settings);
      saveMessage = "設定を保存しました";
    } catch (e) {
      saveMessage = `保存に失敗しました: ${e}`;
    } finally {
      isSaving = false;
    }
  }

  async function handleTest() {
    isTesting = true;
    testResult = null;
    try {
      // Save current form values first so test_connection can read them
      if (apiToken) {
        await saveApiToken(apiToken);
        hasTokenState = true;
      }
      await saveSettings(settings);
      const name = await testConnection();
      testResult = { success: true, message: `接続成功: ${name}` };
    } catch (e) {
      testResult = { success: false, message: String(e) };
    } finally {
      isTesting = false;
    }
  }

  function addFilter() {
    if (!newFilterName || !newFilterJql) return;
    const id = `filter_${Date.now()}`;
    settings.filters = [
      ...settings.filters,
      { id, name: newFilterName, jql: newFilterJql, is_active: false },
    ];
    newFilterName = "";
    newFilterJql = "";
  }

  function removeFilter(id: string) {
    settings.filters = settings.filters.filter((f) => f.id !== id);
  }

  function setActiveFilter(id: string) {
    settings.filters = settings.filters.map((f) => ({
      ...f,
      is_active: f.id === id,
    }));
  }
</script>

<div class="settings">
  <h1>JIRA Focus 設定</h1>

  <section>
    <h2>JIRA接続設定</h2>
    <div class="form-group">
      <label for="domain">JIRAドメイン</label>
      <input
        id="domain"
        type="text"
        bind:value={settings.jira.domain}
        placeholder="mycompany.atlassian.net"
      />
    </div>
    <div class="form-group">
      <label for="email">メールアドレス</label>
      <input
        id="email"
        type="email"
        bind:value={settings.jira.email}
        placeholder="user@example.com"
      />
    </div>
    <div class="form-group">
      <label for="token">
        APIトークン
        {#if hasTokenState}
          <span class="token-saved">(保存済み)</span>
        {/if}
      </label>
      <input
        id="token"
        type="password"
        bind:value={apiToken}
        placeholder={hasTokenState ? "新しいトークンで上書き" : "APIトークンを入力"}
      />
    </div>
    <div class="button-row">
      <button onclick={handleTest} disabled={isTesting}>
        {isTesting ? "テスト中..." : "接続テスト"}
      </button>
      {#if testResult}
        <span class={testResult.success ? "success" : "error-text"}>
          {testResult.message}
        </span>
      {/if}
    </div>
  </section>

  <section>
    <h2>JQLフィルター</h2>
    <div class="filter-list">
      {#each settings.filters as filter (filter.id)}
        <div class="filter-item">
          <input
            type="radio"
            name="activeFilter"
            checked={filter.is_active}
            onchange={() => setActiveFilter(filter.id)}
          />
          <div class="filter-info">
            <span class="filter-name">{filter.name}</span>
            <code class="filter-jql">{filter.jql}</code>
          </div>
          {#if filter.id !== "default"}
            <button class="remove-btn" onclick={() => removeFilter(filter.id)}>×</button>
          {/if}
        </div>
      {/each}
    </div>
    <div class="add-filter">
      <input type="text" bind:value={newFilterName} placeholder="フィルター名" />
      <input type="text" bind:value={newFilterJql} placeholder="JQLクエリ" />
      <button onclick={addFilter}>追加</button>
    </div>
  </section>

  <section>
    <h2>一般設定</h2>
    <div class="form-group">
      <label for="interval">ポーリング間隔（秒）</label>
      <input
        id="interval"
        type="number"
        bind:value={settings.polling_interval_secs}
        min="30"
        max="600"
      />
    </div>
    <div class="form-group checkbox">
      <input id="autostart" type="checkbox" bind:checked={settings.auto_start} />
      <label for="autostart">macOS起動時に自動起動</label>
    </div>
  </section>

  <div class="save-row">
    <button class="save-btn" onclick={handleSave} disabled={isSaving}>
      {isSaving ? "保存中..." : "保存"}
    </button>
    {#if saveMessage}
      <span class="save-message">{saveMessage}</span>
    {/if}
  </div>
</div>

<style>
  .settings {
    padding: 24px;
    max-width: 600px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    overflow-y: auto;
    max-height: 100vh;
  }
  h1 {
    font-size: 20px;
    margin-bottom: 24px;
    color: #333;
  }
  h2 {
    font-size: 16px;
    margin-bottom: 12px;
    color: #555;
    border-bottom: 1px solid #eee;
    padding-bottom: 6px;
  }
  section {
    margin-bottom: 24px;
  }
  .form-group {
    margin-bottom: 12px;
  }
  .form-group label {
    display: block;
    margin-bottom: 4px;
    font-size: 13px;
    color: #666;
  }
  .form-group input[type="text"],
  .form-group input[type="email"],
  .form-group input[type="password"],
  .form-group input[type="number"] {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }
  .form-group.checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .form-group.checkbox label {
    margin-bottom: 0;
  }
  .token-saved {
    color: #2e7d32;
    font-size: 11px;
  }
  .button-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  button {
    padding: 6px 16px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 13px;
  }
  button:hover:not(:disabled) {
    background: #f5f5f5;
  }
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .success {
    color: #2e7d32;
    font-size: 13px;
  }
  .error-text {
    color: #c62828;
    font-size: 13px;
  }
  .filter-list {
    margin-bottom: 12px;
  }
  .filter-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px;
    border: 1px solid #eee;
    border-radius: 6px;
    margin-bottom: 6px;
  }
  .filter-info {
    flex: 1;
    min-width: 0;
  }
  .filter-name {
    display: block;
    font-size: 13px;
    font-weight: 500;
  }
  .filter-jql {
    display: block;
    font-size: 11px;
    color: #888;
    margin-top: 2px;
    word-break: break-all;
  }
  .remove-btn {
    padding: 2px 6px;
    border: none;
    background: none;
    color: #999;
    cursor: pointer;
    font-size: 16px;
  }
  .remove-btn:hover {
    color: #c62828;
  }
  .add-filter {
    display: flex;
    gap: 8px;
  }
  .add-filter input {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 13px;
  }
  .save-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #eee;
  }
  .save-btn {
    background: #1a73e8;
    color: white;
    border: none;
    padding: 8px 24px;
    font-size: 14px;
    font-weight: 500;
  }
  .save-btn:hover:not(:disabled) {
    background: #1565c0;
  }
  .save-message {
    font-size: 13px;
    color: #2e7d32;
  }
</style>
