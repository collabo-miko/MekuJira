export interface NormalizedIssue {
  key: string;
  summary: string;
  status: string;
  status_category: string;
  priority: string;
  assignee: string;
  url: string;
}

export interface BookmarkedIssue extends NormalizedIssue {
  bookmarked_at: string;
  source_filter_id: string;
}

export interface JiraConfig {
  domain: string;
  email: string;
}

export interface JqlFilter {
  id: string;
  name: string;
  jql: string;
  enabled: boolean;
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

export type FilterIssuesMap = Record<string, NormalizedIssue[]>;
