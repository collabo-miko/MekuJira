export interface NormalizedIssue {
  key: string;
  summary: string;
  status: string;
  status_category: string;
  priority: string;
  assignee: string;
  url: string;
}

export interface JiraConfig {
  domain: string;
  email: string;
}

export interface JqlFilter {
  id: string;
  name: string;
  jql: string;
  is_active: boolean;
}

export interface AppSettings {
  jira: JiraConfig;
  filters: JqlFilter[];
  polling_interval_secs: number;
  auto_start: boolean;
}

export interface IssueCache {
  last_fetched: string | null;
  filter_id: string;
  issues: NormalizedIssue[];
}

export interface FocusState {
  focused_issues: string[];
  widget_visible: boolean;
  widget_minimized: boolean;
  widget_position: { x: number; y: number } | null;
}
