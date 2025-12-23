/**
 * API client for PatchHive backend.
 */
import axios from 'axios';
import type {
  ModuleListResponse,
  CaseListResponse,
  RackListResponse,
  PatchListResponse,
  GeneratePatchesRequest,
  GeneratePatchesResponse,
  RunListResponse,
  RunPatchesResponse,
  LoginRequest,
  TokenResponse,
  FeedResponse,
  Module,
  Case,
  Rack,
  Patch,
  User,
  ExportRecord,
  PublicationListResponse,
  PublicationRecord,
  PublicPublicationResponse,
  GalleryResponse,
  CreditsSummary,
  ReferralSummary,
  LeaderboardEntry,
} from '@/types/api';
import type {
  AdminUserList,
  AdminGalleryRevisionList,
  AdminRunList,
  AdminLeaderboardEntry,
} from '@/types/admin';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Module API
export const moduleApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    brand?: string;
    module_type?: string;
    hp_min?: number;
    hp_max?: number;
    tag?: string;
  }) => api.get<ModuleListResponse>('/modules', { params }),

  get: (id: number) => api.get<Module>(`/modules/${id}`),

  create: (data: Partial<Module>) => api.post<Module>('/modules', data),

  update: (id: number, data: Partial<Module>) => api.patch<Module>(`/modules/${id}`, data),

  delete: (id: number) => api.delete(`/modules/${id}`),
};

// Case API
export const caseApi = {
  list: (params?: { skip?: number; limit?: number; brand?: string; min_hp?: number }) =>
    api.get<CaseListResponse>('/cases', { params }),

  get: (id: number) => api.get<Case>(`/cases/${id}`),

  create: (data: Partial<Case>) => api.post<Case>('/cases', data),

  update: (id: number, data: Partial<Case>) => api.patch<Case>(`/cases/${id}`, data),

  delete: (id: number) => api.delete(`/cases/${id}`),
};

// Rack API
export const rackApi = {
  list: (params?: { skip?: number; limit?: number; is_public?: boolean; user_id?: number }) =>
    api.get<RackListResponse>('/racks', { params }),

  get: (id: number) => api.get<Rack>(`/racks/${id}`),

  create: (data: Partial<Rack>) => api.post<Rack>('/racks', data),

  update: (id: number, data: Partial<Rack>) => api.patch<Rack>(`/racks/${id}`, data),

  delete: (id: number) => api.delete(`/racks/${id}`),
};

// Patch API
export const patchApi = {
  list: (params?: {
    skip?: number;
    limit?: number;
    rack_id?: number;
    category?: string;
    is_public?: boolean;
  }) => api.get<PatchListResponse>('/patches', { params }),

  get: (id: number) => api.get<Patch>(`/patches/${id}`),

  create: (data: Partial<Patch>) => api.post<Patch>('/patches', data),

  update: (id: number, data: Partial<Patch>) => api.patch<Patch>(`/patches/${id}`, data),

  delete: (id: number) => api.delete(`/patches/${id}`),

  generate: (rackId: number, request: GeneratePatchesRequest) =>
    api.post<GeneratePatchesResponse>(`/patches/generate/${rackId}`, request),
};

// Run API
export const runApi = {
  list: (rackId: number) => api.get<RunListResponse>('/runs', { params: { rack_id: rackId } }),
  patches: (runId: number) => api.get<RunPatchesResponse>(`/runs/${runId}/patches`),
};

// Auth API
export const authApi = {
  login: (data: LoginRequest) => api.post<TokenResponse>('/community/auth/login', data),

  register: (data: { username: string; email: string; password: string }) =>
    api.post<User>('/community/users', data),

  getUser: (id: number) => api.get<User>(`/community/users/${id}`),

  getUserByUsername: (username: string) => api.get<User>(`/community/users/username/${username}`),

  updateProfile: (data: { avatar_url?: string; bio?: string; display_name?: string; allow_public_avatar?: boolean }) =>
    api.patch<User>('/community/users/me', data),

  getMe: () => api.get<User>('/community/users/me'),
};

// Community API
export const communityApi = {
  getFeed: (params?: { skip?: number; limit?: number }) =>
    api.get<FeedResponse>('/community/feed', { params }),

  vote: (data: { rack_id?: number; patch_id?: number }) =>
    api.post('/community/votes', data),

  deleteVote: (voteId: number) => api.delete(`/community/votes/${voteId}`),

  comment: (data: { rack_id?: number; patch_id?: number; content: string }) =>
    api.post('/community/comments', data),

  getComments: (params: { rack_id?: number; patch_id?: number }) =>
    api.get('/community/comments', { params }),
};

// Export API
export const exportApi = {
  patchPdf: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/pdf`,

  rackPdf: (rackId: number) => `${API_BASE_URL}/export/racks/${rackId}/pdf`,

  rackLayoutSvg: (rackId: number) => `${API_BASE_URL}/export/racks/${rackId}/layout.svg`,

  patchDiagramSvg: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/diagram.svg`,

  patchWaveformSvg: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/waveform.svg`,

  patchbookExport: (runId: number) => api.post(`/export/runs/${runId}/patchbook`),
};

// Monetization API
export const monetizationApi = {
  balance: () => api.get<{ balance: number }>(`/monetization/credits/balance`),
};

// Admin API
export const adminApi = {
  listUsers: (query?: string) =>
    api.get<AdminUserList>('/admin/users', { params: query ? { query } : undefined }),

  updateUserRole: (userId: number, role: string, reason: string) =>
    api.patch(`/admin/users/${userId}/role`, { role, reason }),

  updateUserAvatar: (userId: number, avatar_url: string | null, reason: string) =>
    api.patch(`/admin/users/${userId}/avatar`, { avatar_url, reason }),

  grantCredits: (userId: number, credits: number, reason: string) =>
    api.post(`/admin/users/${userId}/credits/grant`, { credits, reason }),

  createModule: (payload: Record<string, unknown>) => api.post(`/admin/modules`, payload),

  importModules: (payload: Record<string, unknown>) => api.post(`/admin/modules/import`, payload),

  updateModuleStatus: (moduleId: number, status: string, reason: string) =>
    api.patch(`/admin/modules/${moduleId}/status`, { status, reason }),

  mergeModule: (moduleId: number, replacement_module_id: number, reason: string) =>
    api.patch(`/admin/modules/${moduleId}/merge`, { replacement_module_id, reason }),

  listGalleryRevisions: (status?: string) =>
    api.get<AdminGalleryRevisionList>('/admin/gallery/revisions', {
      params: status ? { status } : undefined,
    }),

  approveRevision: (revisionId: number) => api.post(`/admin/gallery/revisions/${revisionId}/approve`),

  confirmRevision: (revisionId: number) => api.post(`/admin/gallery/revisions/${revisionId}/confirm`),

  listRuns: (status?: string) =>
    api.get<AdminRunList>('/admin/runs', { params: status ? { status } : undefined }),

  rerunRig: (rigId: number) => api.post(`/admin/runs/${rigId}/rerun`),

  unlockExport: (exportId: number, reason: string) =>
    api.post(`/admin/exports/${exportId}/unlock`, { reason }),

  revokeExport: (exportId: number, reason: string) =>
    api.post(`/admin/exports/${exportId}/revoke`, { reason }),

  invalidateCache: (payload: { run_id?: number; export_type?: string; reason: string }) =>
    api.post(`/admin/cache/invalidate`, payload),

  popularModules: () => api.get<AdminLeaderboardEntry[]>(`/admin/leaderboards/modules/popular`),

  trendingModules: (window_days: number) =>
    api.get<AdminLeaderboardEntry[]>(`/admin/leaderboards/modules/trending`, {
      params: { window_days },
    }),

  exportedCategories: () =>
    api.get<AdminLeaderboardEntry[]>(`/admin/leaderboards/categories/exported`),
};

// Publishing API
export const publishingApi = {
  createExport: (data: { source_type: 'patch' | 'rack'; source_id: number }) =>
    api.post<ExportRecord>('/me/exports', data),

  listExports: () => api.get<ExportRecord[]>('/me/exports'),

  createPublication: (data: {
    export_id: number;
    title: string;
    description?: string;
    visibility: 'public' | 'unlisted';
    allow_download: boolean;
    allow_remix: boolean;
    cover_image_url?: string;
  }) => api.post<PublicationRecord>('/me/publications', data),

  updatePublication: (publicationId: number, data: Partial<PublicationRecord>) =>
    api.patch<PublicationRecord>(`/me/publications/${publicationId}`, data),

  listPublications: () => api.get<PublicationListResponse>('/me/publications'),

  getPublication: (slug: string) => api.get<PublicPublicationResponse>(`/p/${slug}`),

  listGallery: (params?: {
    limit?: number;
    cursor?: string;
    export_type?: string;
    recent_days?: number;
  }) => api.get<GalleryResponse>('/gallery/publications', { params }),

  reportPublication: (slug: string, data: { reason: string; details?: string }) =>
    api.post(`/p/${slug}/report`, data),
};

// Account API
export const accountApi = {
  getCredits: () => api.get<CreditsSummary>('/me/credits'),
  getExports: () => api.get<ExportRecord[]>('/me/exports'),
  getReferrals: () => api.get<ReferralSummary>('/me/referrals'),
};

// Leaderboards API
export const leaderboardsApi = {
  getPopularModules: () => api.get<LeaderboardEntry[]>('/leaderboards/modules/popular'),
  getTrendingModules: (windowDays = 30) =>
    api.get<LeaderboardEntry[]>('/leaderboards/modules/trending', { params: { window_days: windowDays } }),
};

export default api;
