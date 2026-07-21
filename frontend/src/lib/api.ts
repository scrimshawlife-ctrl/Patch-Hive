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
  Module,
  Case,
  Rack,
  Patch,
  User,
  CanonicalExportRecord,
  ReferralSummary,
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

// Visual evidence API (photo → candidates → confirmation → inventory)
export interface EvidenceCandidate {
  candidate_id: string;
  entity_type: string;
  manufacturer?: string | null;
  model?: string | null;
  confidence: number;
  confidence_method: string;
  alternative_candidates: string[];
  classification_status: string;
  evidence_id: string;
  image_asset_id?: string | null;
  gallery_revision_id?: string | null;
  gallery_module_id?: string | null;
}

export interface EvidenceCandidateListResponse {
  total: number;
  candidates: EvidenceCandidate[];
}

export interface MultiImageUploadResponse {
  uploaded: Array<{
    id: string;
    rack_id: number;
    content_sha256: string;
    evidence_status?: string | null;
  }>;
  rejected: Array<{ filename: string; reason: string }>;
}

export interface ConfirmationBatchResponse {
  inventory_revision_id: string;
  inventory_canonical_hash?: string | null;
  confirmed_count: number;
  unresolved_candidate_ids: string[];
  ready_for_generation: boolean;
}

export interface InventoryRevisionSummary {
  inventory_revision_id: string;
  system_id: string;
  rack_id?: number | null;
  confirmed_count: number;
  unresolved_count: number;
  ready_for_generation: boolean;
  canonical_hash?: string | null;
  created_by?: string | null;
  created_at?: string | null;
}

export interface InventoryRevisionListResponse {
  total: number;
  latest: InventoryRevisionSummary | null;
  revisions: InventoryRevisionSummary[];
}

export const evidenceApi = {
  uploadImages: (
    rackId: number,
    files: File[],
    options?: {
      retention_days?: number;
      consent_provider_processing?: boolean;
      run_vision_mock?: boolean;
    },
  ) => {
    const form = new FormData();
    files.forEach((file) => form.append('files', file));
    form.append('retention_days', String(options?.retention_days ?? 30));
    form.append(
      'consent_provider_processing',
      String(options?.consent_provider_processing ?? false),
    );
    form.append('run_vision_mock', String(options?.run_vision_mock ?? true));
    return api.post<MultiImageUploadResponse>(`/racks/${rackId}/evidence/images`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  listImages: (rackId: number) => api.get(`/racks/${rackId}/evidence/images`),

  listCandidates: (rackId: number) =>
    api.get<EvidenceCandidateListResponse>(`/racks/${rackId}/evidence/candidates`),

  reconcile: (rackId: number) =>
    api.get<{
      image_asset_ids: string[];
      image_count: number;
      fused_entities: Array<{
        fuse_id: string;
        entity_key: string;
        manufacturer?: string | null;
        model?: string | null;
        entity_type: string;
        observation_count: number;
        supporting_image_ids: string[];
        mean_confidence: number;
        max_confidence: number;
        conflict: boolean;
        conflict_notes: string[];
        classification_status: string;
        representative_candidate_id?: string | null;
      }>;
      unmatched_candidate_ids: string[];
      conflict_count: number;
      status: string;
      note: string;
    }>(`/racks/${rackId}/evidence/reconcile`),

  confirm: (
    rackId: number,
    body: {
      confirmed_by?: string;
      decisions: Array<{
        candidate_id: string;
        status: string;
        module_revision_id?: string | null;
        notes?: string | null;
      }>;
    },
  ) => api.post<ConfirmationBatchResponse>(`/racks/${rackId}/evidence/confirmations`, body),

  listInventory: (rackId: number) =>
    api.get<InventoryRevisionListResponse>(`/racks/${rackId}/evidence/inventory`),
};

// Run API — list prefers canon alias; patches still legacy until dual-written.
export const runApi = {
  /** @deprecated Prefer `canonApi.listRuns` (same bridge DTO). */
  list: (rackId: number) =>
    api.get<RunListResponse>('/canon/runs', { params: { rig_id: rackId } }),
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

// Community social API clients live under `src/legacy/apiClients.ts` (unrouted MVP).

// Export API
// PDF/SVG file URLs remain on legacy `/export/*` (artifact bytes).
// Debited patch-book requests must use `canonApi.createExport` (ledger boundary).
export const exportApi = {
  patchPdf: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/pdf`,

  rackPdf: (rackId: number) => `${API_BASE_URL}/export/racks/${rackId}/pdf`,

  rackLayoutSvg: (rackId: number) => `${API_BASE_URL}/export/racks/${rackId}/layout.svg`,

  patchDiagramSvg: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/diagram.svg`,

  patchWaveformSvg: (patchId: number) => `${API_BASE_URL}/export/patches/${patchId}/waveform.svg`,
};

// Canonical credits + exports (preferred MVP monetization boundary)
export const canonApi = {
  /** Matrix slice B — same bridge DTO as GET /api/runs?rack_id= */
  listRuns: (rigId: number) =>
    api.get<RunListResponse>('/canon/runs', { params: { rig_id: rigId } }),

  getBalance: () => api.get<{ balance: number }>('/canon/credits/balance'),

  getCreditsSummary: () =>
    api.get<{
      balance: number;
      entries: Array<{
        id: string;
        delta: number;
        entry_type: string;
        export_id: string | null;
        created_at: string;
      }>;
    }>('/canon/credits/summary'),

  listExports: () => api.get<CanonicalExportRecord[]>('/canon/exports'),

  getExport: (exportId: string) => api.get<CanonicalExportRecord>(`/canon/exports/${exportId}`),

  createExport: (body: {
    source_run_id: string;
    source_rig_revision_id: string;
    artifact_manifest_hash: string;
    formats?: Array<'pdf' | 'svg' | 'json' | 'zip'>;
    license?: string;
    credit_cost?: number | null;
    idempotency_key: string;
    style_recipe?: Record<string, unknown> | null;
    style_recipe_id?: string | null;
  }) => api.post<CanonicalExportRecord>('/canon/exports', body),

  /** Free Design Engine preview — no debit (KD-15). */
  previewExport: (body: {
    source_run_id: string;
    source_rig_revision_id: string;
    artifact_manifest_hash: string;
    style_recipe?: Record<string, unknown> | null;
    style_recipe_id?: string | null;
    max_pages?: number;
  }) =>
    api.post<{
      resolved_recipe: Record<string, unknown>;
      resolution_events: Array<{
        code: string;
        severity: string;
        message: string;
        field?: string | null;
      }>;
      style_recipe_hash: string;
      library_content_hash: string;
      load_path: string;
      page_summaries: Array<{
        position: number;
        title: string;
        intent: string;
        edge_count: number;
        steps: Array<{ phase: string; instruction: string }>;
        warnings?: Array<{ code: string; severity: string; message: string }>;
      }>;
      composition_preview_hash?: string | null;
    }>('/canon/exports/preview', body),

  listStyleRecipes: () =>
    api.get<
      Array<{
        id: string;
        name: string;
        notes: string | null;
        style_recipe: Record<string, unknown>;
        recipe_hash: string;
        created_at: string;
        updated_at: string;
      }>
    >('/canon/style-recipes'),

  createStyleRecipe: (body: {
    name: string;
    style_recipe: Record<string, unknown>;
    notes?: string | null;
  }) =>
    api.post<{
      id: string;
      name: string;
      notes: string | null;
      style_recipe: Record<string, unknown>;
      recipe_hash: string;
      created_at: string;
      updated_at: string;
    }>('/canon/style-recipes', body),

  deleteStyleRecipe: (recipeId: string) =>
    api.delete(`/canon/style-recipes/${encodeURIComponent(recipeId)}`),

  createDownloadToken: (exportId: string, ttl_seconds = 300) =>
    api.post<{ export_id: string; token: string; ttl_seconds: number }>(
      `/canon/exports/${exportId}/download-token`,
      { ttl_seconds },
    ),

  listRevisions: (rigId: number) =>
    api.get<{
      total: number;
      revisions: Array<{
        rig_revision_id: string;
        content_hash?: string | null;
        run_count: number;
        latest_run_id?: number | null;
        latest_run_at?: string | null;
        export_bridge_ready: boolean;
      }>;
    }>(`/canon/rigs/${rigId}/revisions`),

  getOverlay: (patchRef: string) =>
    api.get<{
      id: string;
      patch_ref: string;
      notes: string | null;
      favorite: boolean;
      tried: boolean;
      updated_at: string;
    }>(`/canon/overlays/${encodeURIComponent(patchRef)}`),

  upsertOverlay: (
    patchRef: string,
    body: { notes?: string | null; favorite?: boolean; tried?: boolean },
  ) =>
    api.put<{
      id: string;
      patch_ref: string;
      notes: string | null;
      favorite: boolean;
      tried: boolean;
      updated_at: string;
    }>(`/canon/overlays/${encodeURIComponent(patchRef)}`, body),
};

export function legacyPatchRef(patchId: number): string {
  return `legacy-patch-${patchId}`;
}

// Monetization API — balance is a thin alias over the canonical ledger.
export const monetizationApi = {
  balance: () => canonApi.getBalance(),
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

// Publishing / leaderboard clients live under `src/legacy/apiClients.ts`.

// Account API
// Credits/exports prefer the canonical ledger. Referrals remain legacy-flagged.
export const accountApi = {
  getCredits: async () => {
    const summary = await canonApi.getCreditsSummary();
    return {
      ...summary,
      data: {
        balance: summary.data.balance,
        entries: summary.data.entries.map((entry) => ({
          id: entry.id,
          entry_type: entry.entry_type,
          amount: entry.delta,
          description: entry.export_id ? `export ${entry.export_id}` : undefined,
          created_at: entry.created_at,
        })),
      },
    };
  },
  getExports: async () => {
    const listed = await canonApi.listExports();
    return {
      ...listed,
      data: listed.data.map((record) => ({
        id: record.export_id,
        export_type: 'canon',
        entity_id: record.source_run_id,
        run_id: record.source_run_id,
        unlocked: record.status === 'succeeded' || record.status === 'queued' || record.status === 'running',
        license_type: undefined,
        created_at: record.created_at,
        status: record.status,
        source: 'canon' as const,
      })),
    };
  },
  getReferrals: () => api.get<ReferralSummary>('/me/referrals'),
};

export default api;
