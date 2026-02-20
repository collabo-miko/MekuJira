import { invoke } from "@tauri-apps/api/core";
import type { FocusState } from "$lib/types";

export async function getFocusState(): Promise<FocusState> {
  return invoke("get_focus_state");
}

export async function toggleFocusIssue(issueKey: string): Promise<FocusState> {
  return invoke("toggle_focus_issue", { issueKey });
}

export async function updateWidgetPosition(
  x: number,
  y: number
): Promise<void> {
  return invoke("update_widget_position", { x, y });
}

export async function setWidgetMinimized(minimized: boolean): Promise<void> {
  return invoke("set_widget_minimized", { minimized });
}
