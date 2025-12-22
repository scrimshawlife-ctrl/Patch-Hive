export interface AdminUser {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  role: string;
  created_at: string;
}

export interface AdminUserList {
  total: number;
  users: AdminUser[];
}

export interface AdminModule {
  id: number;
  brand: string;
  name: string;
  status: string;
  replacement_module_id?: number;
  deprecated_at?: string;
  tombstoned_at?: string;
}

export interface AdminGalleryRevision {
  id: number;
  module_key: string;
  revision_id: string;
  status: string;
  created_at: string;
}

export interface AdminGalleryRevisionList {
  total: number;
  revisions: AdminGalleryRevision[];
}

export interface AdminRun {
  id: number;
  rack_id: number;
  status: string;
  created_at: string;
}

export interface AdminRunList {
  total: number;
  runs: AdminRun[];
}

export interface AdminLeaderboardEntry {
  label: string;
  count: number;
}
