<script lang="ts">
  import { onMount } from "svelte";
  import { getVersion } from "@tauri-apps/api/app";
  import { check } from "@tauri-apps/plugin-updater";
  import { relaunch } from "@tauri-apps/plugin-process";
  import { getSettings, saveSettings, saveApiToken, hasApiToken } from "$lib/api/settings";
  import { testConnection } from "$lib/api/jira";
  import type { AppSettings } from "$lib/types";

  let appVersion = $state("");
  let updateStatus = $state<"checking" | "latest" | "updating" | "ready" | "error" | "">("");
  let updateError = $state("");

  let settings = $state<AppSettings>({
    jira: { domain: "", email: "" },
    filters: [],
    polling_interval_secs: 3600,
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

  async function checkForUpdates() {
    updateStatus = "checking";
    updateError = "";
    try {
      const update = await check();
      if (update) {
        updateStatus = "updating";
        await update.downloadAndInstall();
        updateStatus = "ready";
      } else {
        updateStatus = "latest";
      }
    } catch (e) {
      updateStatus = "error";
      updateError = String(e);
    }
  }

  onMount(async () => {
    try {
      appVersion = await getVersion();
      settings = await getSettings();
      hasTokenState = await hasApiToken();
    } catch (e) {
      console.error("Failed to load settings:", e);
    }
    checkForUpdates();
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
    {#if appVersion}
      <span class="app-version">v{appVersion}</span>
    {/if}
    {#if updateStatus === "checking"}
      <span class="update-status checking">更新を確認中...</span>
    {:else if updateStatus === "latest"}
      <span class="update-status latest">最新です</span>
    {:else if updateStatus === "updating"}
      <span class="update-status updating">ダウンロード中...</span>
    {:else if updateStatus === "ready"}
      <button class="update-status ready" onclick={() => relaunch()}>再起動して更新</button>
    {:else if updateStatus === "error"}
      <span class="update-status error" title={updateError}>更新確認に失敗</span>
    {/if}
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
        max="7200"
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
    font-family: var(--font-family);
    overflow-y: auto;
    max-height: 100vh;
    background: var(--color-bg);
    color: var(--color-text-primary);
  }
  .page-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 28px;
  }
  .app-version {
    font-size: 13px;
    font-weight: 500;
    color: var(--color-text-tertiary);
  }
  .update-status {
    font-size: 12px;
    font-weight: 500;
    padding: 1px 8px;
    border-radius: 100px;
  }
  .update-status.checking,
  .update-status.updating {
    color: var(--color-text-tertiary);
  }
  .update-status.latest {
    color: var(--color-success);
    background: var(--color-success-bg);
  }
  .update-status.ready {
    color: #fff;
    background: var(--color-accent);
    border: none;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.12s ease;
  }
  .update-status.ready:hover {
    background: var(--color-accent-hover);
  }
  .update-status.error {
    color: var(--color-error);
    cursor: help;
  }
  h1 {
    font-size: 24px;
    font-weight: 700;
    color: var(--color-text-primary);
    letter-spacing: -0.02em;
  }
  h2 {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
  }
  .section-hint {
    font-size: 14px;
    color: var(--color-text-secondary);
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
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-primary);
  }
  .form-group input[type="text"],
  .form-group input[type="email"],
  .form-group input[type="password"],
  .form-group input[type="number"] {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--color-border);
    border-radius: 8px;
    font-size: 15px;
    font-family: inherit;
    color: var(--color-text-primary);
    background: var(--color-surface);
    outline: none;
    transition: all 0.15s ease;
  }
  .form-group input:focus {
    border-color: var(--color-accent);
    background: var(--color-elevated);
    box-shadow: 0 0 0 3px var(--color-focus-ring);
  }
  .form-group input::placeholder {
    color: var(--color-text-tertiary);
  }
  .form-group.checkbox {
    margin-top: 4px;
  }
  .toggle-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 15px;
    color: var(--color-text-primary);
  }
  .toggle-label input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--color-accent);
  }
  .token-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-success);
    background: var(--color-success-bg);
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
    border: 1px solid var(--color-border);
    border-radius: 8px;
    background: var(--color-elevated);
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    font-weight: 500;
    color: var(--color-text-primary);
    transition: all 0.12s ease;
  }
  .btn-secondary:hover:not(:disabled) {
    background: var(--color-surface);
  }
  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .btn-primary {
    padding: 8px 28px;
    border: none;
    border-radius: 8px;
    background: var(--color-accent);
    color: #fff;
    cursor: pointer;
    font-size: 15px;
    font-family: inherit;
    font-weight: 500;
    transition: all 0.12s ease;
  }
  .btn-primary:hover:not(:disabled) {
    background: var(--color-accent-hover);
  }
  .btn-primary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .result {
    font-size: 14px;
  }
  .result.success {
    color: var(--color-success);
  }
  .result.error {
    color: var(--color-error);
  }
  .filter-list {
    margin-bottom: 12px;
  }
  .filter-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 12px;
    background: var(--color-surface);
    border-radius: 8px;
    margin-bottom: 6px;
    transition: background 0.12s ease;
  }
  .filter-item.active {
    background: var(--color-accent-bg);
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
    accent-color: var(--color-accent);
    flex-shrink: 0;
  }
  .filter-info {
    flex: 1;
    min-width: 0;
  }
  .filter-name {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-primary);
  }
  .filter-jql {
    display: block;
    font-size: 14px;
    color: var(--color-text-secondary);
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
    color: var(--color-text-tertiary);
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.12s ease;
  }
  .edit-btn:hover {
    background: var(--color-accent-bg);
    color: var(--color-accent);
  }
  .remove-btn:hover {
    background: var(--color-error-bg-hover);
    color: var(--color-error);
  }
  .filter-item.editing {
    padding: 12px;
    background: var(--color-elevated);
    border: 1px solid var(--color-accent);
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
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
    color: var(--color-text-primary);
    background: var(--color-surface);
    outline: none;
    transition: all 0.15s ease;
  }
  .edit-input:focus {
    border-color: var(--color-accent);
    background: var(--color-elevated);
    box-shadow: 0 0 0 3px var(--color-focus-ring);
  }
  .edit-input.edit-jql {
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 14px;
  }
  .edit-actions {
    display: flex;
    gap: 6px;
  }
  .btn-edit-save {
    padding: 4px 14px;
    border: none;
    border-radius: 6px;
    background: var(--color-accent);
    color: #fff;
    font-size: 14px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.12s ease;
  }
  .btn-edit-save:hover {
    background: var(--color-accent-hover);
  }
  .btn-edit-cancel {
    padding: 4px 14px;
    border: 1px solid var(--color-border);
    border-radius: 6px;
    background: var(--color-elevated);
    color: var(--color-text-secondary);
    font-size: 14px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.12s ease;
  }
  .btn-edit-cancel:hover {
    background: var(--color-surface);
  }
  .add-filter {
    display: flex;
    gap: 8px;
  }
  .add-filter input {
    flex: 1;
    padding: 6px 10px;
    border: 1px solid var(--color-border);
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    background: var(--color-surface);
    color: var(--color-text-primary);
    outline: none;
    transition: all 0.15s ease;
  }
  .add-filter input:focus {
    border-color: var(--color-accent);
    background: var(--color-elevated);
    box-shadow: 0 0 0 3px var(--color-focus-ring);
  }
  .add-filter input::placeholder {
    color: var(--color-text-tertiary);
  }
  .save-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-top: 20px;
    border-top: 1px solid var(--color-border);
  }
  .save-message {
    font-size: 14px;
    color: var(--color-success);
  }
</style>
