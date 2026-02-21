import { writable } from "svelte/store";
import type { NormalizedIssue } from "$lib/types";

export const issues = writable<NormalizedIssue[]>([]);
export const isLoading = writable(false);
export const error = writable<string | null>(null);
export const lastFetched = writable<string | null>(null);
