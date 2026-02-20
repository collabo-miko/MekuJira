import { writable } from "svelte/store";
import type { FocusState } from "$lib/types";

const defaultFocusState: FocusState = {
  focused_issues: [],
  widget_visible: false,
  widget_minimized: false,
  widget_position: null,
};

export const focusState = writable<FocusState>(defaultFocusState);
