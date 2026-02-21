<div class="popup">
  <header class="header">
    <h1>Menubar Template</h1>
  </header>
  <main class="content">
    <p>Hello! This is your menu bar app.</p>
    <p class="hint">Edit this page at <code>src/routes/popup/+page.svelte</code></p>
  </main>
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
  .header {
    padding: 16px 20px 12px;
    border-bottom: 1px solid var(--color-border);
  }
  .header h1 {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text-primary);
  }
  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px;
    color: var(--color-text-secondary);
    font-size: 15px;
  }
  .hint {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
  .hint code {
    font-family: "SF Mono", "Menlo", monospace;
    background: var(--color-surface);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }
</style>
