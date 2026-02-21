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
  let editingFilterId = $state<string | null>(null);
  let editName = $state("");
  let editJql = $state("");

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
      { id, name: newFilterName, jql: newFilterJql, enabled: true },
    ];
    newFilterName = "";
    newFilterJql = "";
  }

  function removeFilter(id: string) {
    settings.filters = settings.filters.filter((f) => f.id !== id);
  }

  function toggleFilterEnabled(id: string) {
    settings.filters = settings.filters.map((f) =>
      f.id === id ? { ...f, enabled: !f.enabled } : f,
    );
  }

  function startEdit(id: string) {
    const filter = settings.filters.find((f) => f.id === id);
    if (!filter) return;
    editingFilterId = id;
    editName = filter.name;
    editJql = filter.jql;
  }

  function cancelEdit() {
    editingFilterId = null;
    editName = "";
    editJql = "";
  }

  function saveEdit() {
    if (!editingFilterId || !editName || !editJql) return;
    settings.filters = settings.filters.map((f) =>
      f.id === editingFilterId ? { ...f, name: editName, jql: editJql } : f,
    );
    cancelEdit();
  }
</script>

<div class="settings">
  <header class="page-header">
    <h1>設定</h1>
  </header>

  <section>
    <h2>JIRA接続</h2>
    <div class="form-group">
      <label for="domain">ドメイン</label>
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
          <span class="token-badge">保存済み</span>
        {/if}
      </label>
      <input
        id="token"
        type="password"
        bind:value={apiToken}
        placeholder={hasTokenState ? "新しいトークンで上書き" : "APIトークンを入力"}
      />
    </div>
    <div class="actions-row">
      <button class="btn-secondary" onclick={handleTest} disabled={isTesting}>
        {isTesting ? "テスト中..." : "接続テスト"}
      </button>
      {#if testResult}
        <span class="result" class:success={testResult.success} class:error={!testResult.success}>
          {testResult.message}
        </span>
      {/if}
    </div>
  </section>

  <section>
    <h2>JQLフィルター</h2>
    <p class="section-hint">チェックを入れたフィルターが「対象課題一覧」に表示されます</p>
    {#if settings.filters.length > 0}
      <div class="filter-list">
        {#each settings.filters as filter (filter.id)}
          {#if editingFilterId === filter.id}
            <div class="filter-item editing">
              <div class="edit-form">
                <input
                  class="edit-input"
                  type="text"
                  bind:value={editName}
                  placeholder="フィルター名"
                />
                <input
                  class="edit-input edit-jql"
                  type="text"
                  bind:value={editJql}
                  placeholder="JQLクエリ"
                />
                <div class="edit-actions">
                  <button class="btn-edit-save" onclick={saveEdit}>保存</button>
                  <button class="btn-edit-cancel" onclick={cancelEdit}>キャンセル</button>
                </div>
              </div>
            </div>
          {:else}
            <div class="filter-item" class:active={filter.enabled}>
              <label class="filter-toggle">
                <input
                  type="checkbox"
                  checked={filter.enabled}
                  onchange={() => toggleFilterEnabled(filter.id)}
                />
                <div class="filter-info">
                  <span class="filter-name">{filter.name}</span>
                  <code class="filter-jql">{filter.jql}</code>
                </div>
              </label>
              <button class="edit-btn" onclick={() => startEdit(filter.id)} title="編集">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M8.5 1.5l2 2L4 10H2v-2z"/>
                  <path d="M7 3l2 2"/>
                </svg>
              </button>
              {#if filter.id !== "default"}
                <button class="remove-btn" onclick={() => removeFilter(filter.id)} title="削除">
                  <svg width="12" height="12" viewBox="0 0 12 12" stroke="currentColor" stroke-width="1.5" fill="none">
                    <path d="M3 3l6 6M9 3l-6 6"/>
                  </svg>
                </button>
              {/if}
            </div>
          {/if}
        {/each}
      </div>
    {/if}
    <div class="add-filter">
      <input type="text" bind:value={newFilterName} placeholder="フィルター名" />
      <input type="text" bind:value={newFilterJql} placeholder="JQLクエリ" />
      <button class="btn-secondary" onclick={addFilter}>追加</button>
    </div>
  </section>

  <section>
    <h2>一般</h2>
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
      <label class="toggle-label">
        <input id="autostart" type="checkbox" bind:checked={settings.auto_start} />
        <span>macOS起動時に自動起動</span>
      </label>
    </div>
  </section>

  <div class="save-row">
    <button class="btn-primary" onclick={handleSave} disabled={isSaving}>
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
    max-width: 560px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    overflow-y: auto;
    max-height: 100vh;
  }
  .page-header {
    margin-bottom: 28px;
  }
  h1 {
    font-size: 22px;
    font-weight: 700;
    color: #1d1d1f;
    letter-spacing: -0.02em;
  }
  h2 {
    font-size: 13px;
    font-weight: 600;
    color: #6e6e73;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
  }
  .section-hint {
    font-size: 12px;
    color: #6e6e73;
    margin-bottom: 12px;
    margin-top: -4px;
  }
  section {
    margin-bottom: 28px;
  }
  .form-group {
    margin-bottom: 14px;
  }
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 13px;
    font-weight: 500;
    color: #1d1d1f;
  }
  .form-group input[type="text"],
  .form-group input[type="email"],
  .form-group input[type="password"],
  .form-group input[type="number"] {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    color: #1d1d1f;
    background: #f5f5f7;
    outline: none;
    transition: all 0.15s ease;
  }
  .form-group input:focus {
    border-color: #0071e3;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
  }
  .form-group input::placeholder {
    color: #aeaeb2;
  }
  .form-group.checkbox {
    margin-top: 4px;
  }
  .toggle-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #1d1d1f;
  }
  .toggle-label input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: #0071e3;
  }
  .token-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    color: #34c759;
    background: #f0fdf4;
    padding: 1px 6px;
    border-radius: 100px;
    margin-left: 6px;
    vertical-align: middle;
  }
  .actions-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
  .btn-secondary {
    padding: 6px 16px;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    background: #fff;
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
    font-weight: 500;
    color: #1d1d1f;
    transition: all 0.12s ease;
  }
  .btn-secondary:hover:not(:disabled) {
    background: #f5f5f7;
  }
  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .btn-primary {
    padding: 8px 28px;
    border: none;
    border-radius: 8px;
    background: #0071e3;
    color: #fff;
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    font-weight: 500;
    transition: all 0.12s ease;
  }
  .btn-primary:hover:not(:disabled) {
    background: #0077ed;
  }
  .btn-primary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .result {
    font-size: 13px;
  }
  .result.success {
    color: #34c759;
  }
  .result.error {
    color: #ff3b30;
  }
  .filter-list {
    margin-bottom: 12px;
  }
  .filter-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 12px;
    background: #f5f5f7;
    border-radius: 8px;
    margin-bottom: 6px;
    transition: background 0.12s ease;
  }
  .filter-item.active {
    background: #eff6ff;
  }
  .filter-toggle {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    flex: 1;
    min-width: 0;
    cursor: pointer;
  }
  .filter-toggle input[type="checkbox"] {
    margin-top: 2px;
    width: 16px;
    height: 16px;
    accent-color: #0071e3;
    flex-shrink: 0;
  }
  .filter-info {
    flex: 1;
    min-width: 0;
  }
  .filter-name {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: #1d1d1f;
  }
  .filter-jql {
    display: block;
    font-size: 11px;
    color: #6e6e73;
    margin-top: 2px;
    word-break: break-all;
    font-family: "SF Mono", "Menlo", monospace;
  }
  .edit-btn,
  .remove-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    padding: 0;
    border: none;
    background: none;
    color: #aeaeb2;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.12s ease;
  }
  .edit-btn:hover {
    background: rgba(0, 113, 227, 0.1);
    color: #0071e3;
  }
  .remove-btn:hover {
    background: rgba(255, 59, 48, 0.1);
    color: #ff3b30;
  }
  .filter-item.editing {
    padding: 12px;
    background: #fff;
    border: 1px solid #0071e3;
  }
  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
  }
  .edit-input {
    width: 100%;
    padding: 6px 10px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    font-size: 13px;
    font-family: inherit;
    color: #1d1d1f;
    background: #f5f5f7;
    outline: none;
    transition: all 0.15s ease;
  }
  .edit-input:focus {
    border-color: #0071e3;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
  }
  .edit-input.edit-jql {
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 12px;
  }
  .edit-actions {
    display: flex;
    gap: 6px;
  }
  .btn-edit-save {
    padding: 4px 14px;
    border: none;
    border-radius: 6px;
    background: #0071e3;
    color: #fff;
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.12s ease;
  }
  .btn-edit-save:hover {
    background: #0077ed;
  }
  .btn-edit-cancel {
    padding: 4px 14px;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    background: #fff;
    color: #6e6e73;
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.12s ease;
  }
  .btn-edit-cancel:hover {
    background: #f5f5f7;
  }
  .add-filter {
    display: flex;
    gap: 8px;
  }
  .add-filter input {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    background: #f5f5f7;
    color: #1d1d1f;
    outline: none;
    transition: all 0.15s ease;
  }
  .add-filter input:focus {
    border-color: #0071e3;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.12);
  }
  .add-filter input::placeholder {
    color: #aeaeb2;
  }
  .save-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-top: 20px;
    border-top: 1px solid #e5e5e5;
  }
  .save-message {
    font-size: 13px;
    color: #34c759;
  }
</style>
