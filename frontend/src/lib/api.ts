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
} from '@/types/api';

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

// Auth API
export const authApi = {
  login: (data: LoginRequest) => api.post<TokenResponse>('/community/auth/login', data),

  register: (data: { username: string; email: string; password: string }) =>
    api.post<User>('/community/users', data),

  getUser: (id: number) => api.get<User>(`/community/users/${id}`),

  getUserByUsername: (username: string) => api.get<User>(`/community/users/username/${username}`),

  updateProfile: (data: { avatar_url?: string; bio?: string; display_name?: string; allow_public_avatar?: boolean }) =>
    api.patch<User>('/community/users/me', data),
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

export default api;
