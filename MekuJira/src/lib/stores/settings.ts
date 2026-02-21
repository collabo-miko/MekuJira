import { writable } from "svelte/store";
import type { AppSettings } from "$lib/types";

const defaultSettings: AppSettings = {
  jira: { domain: "", email: "" },
  filters: [
    {
      id: "default",
      name: "自分の未完了課題",
      jql: "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC",
      enabled: true,
    },
  ],
  polling_interval_secs: 60,
  auto_start: false,
};

export const settings = writable<AppSettings>(defaultSettings);
