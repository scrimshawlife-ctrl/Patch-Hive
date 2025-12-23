/**
 * TypeScript types matching the backend API schemas.
 */

// Module types
export interface IOPort {
  name: string;
  type: string;
}

export interface Module {
  id: number;
  brand: string;
  name: string;
  hp: number;
  module_type: string;
  power_12v_ma?: number;
  power_neg12v_ma?: number;
  power_5v_ma?: number;
  io_ports: IOPort[];
  tags: string[];
  description?: string;
  manufacturer_url?: string;
  status?: string;
  replacement_module_id?: number | null;
  deprecated_at?: string | null;
  tombstoned_at?: string | null;
  source: string;
  source_reference?: string;
  imported_at: string;
  created_at: string;
  updated_at: string;
}

export interface ModuleListResponse {
  total: number;
  modules: Module[];
}

// Case types
export interface Case {
  id: number;
  brand: string;
  name: string;
  total_hp: number;
  rows: number;
  hp_per_row: number[];
  power_12v_ma?: number;
  power_neg12v_ma?: number;
  power_5v_ma?: number;
  description?: string;
  manufacturer_url?: string;
  meta?: Record<string, unknown>;
  source: string;
  source_reference?: string;
  created_at: string;
  updated_at: string;
}

export interface CaseListResponse {
  total: number;
  cases: Case[];
}

// Rack types
export interface RackModuleSpec {
  module_id: number;
  row_index: number;
  start_hp: number;
}

export interface RackModule extends RackModuleSpec {
  id: number;
  module?: {
    id: number;
    brand: string;
    name: string;
    hp: number;
    module_type: string;
  };
}

export interface Rack {
  id: number;
  user_id: number;
  case_id: number;
  name: string;
  name_suggested?: string;
  description?: string;
  tags: string[];
  is_public: boolean;
  generation_seed?: number;
  created_at: string;
  updated_at: string;
  modules: RackModule[];
  case?: {
    id: number;
    brand: string;
    name: string;
    total_hp: number;
    rows: number;
    hp_per_row: number[];
  };
  vote_count: number;
}

export interface RackListResponse {
  total: number;
  racks: Rack[];
}

// Patch types
export interface Connection {
  from_module_id: number;
  from_port: string;
  to_module_id: number;
  to_port: string;
  cable_type: string;
}

export interface Patch {
  id: number;
  rack_id: number;
  run_id?: number | null;
  name: string;
  suggested_name?: string | null;
  name_override?: string | null;
  category: string;
  description?: string;
  tags?: string[];
  difficulty?: string;
  diagram_svg_url?: string;
  connections: Connection[];
  generation_seed: number;
  generation_version: string;
  engine_config?: Record<string, unknown>;
  waveform_svg_path?: string;
  waveform_params?: Record<string, unknown>;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  vote_count: number;
}

export interface PatchListResponse {
  total: number;
  patches: Patch[];
}

export interface Run {
  id: number;
  rack_id: number;
  status: string;
  created_at: string;
}

export interface RunListResponse {
  total: number;
  runs: Run[];
}

export interface GeneratePatchesRequest {
  seed?: number;
  max_patches?: number;
  allow_feedback?: boolean;
  prefer_simple?: boolean;
}

export interface GeneratePatchesResponse {
  generated_count: number;
  patches: Patch[];
  run_id?: number;
}

export interface RunPatchesResponse {
  run_id: number;
  total: number;
  created_at?: string;
  patches: Patch[];
}

// User types
export interface User {
  id: number;
  username: string;
  email: string;
  display_name?: string;
  avatar_url?: string;
  allow_public_avatar?: boolean;
  bio?: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface CreditLedgerEntry {
  id: number;
  entry_type: string;
  amount: number;
  description?: string;
  created_at: string;
}

export interface CreditsSummary {
  balance: number;
  entries: CreditLedgerEntry[];
}

export interface UserExportRecord {
  id: number;
  export_type: string;
  entity_id: number;
  run_id: string;
  unlocked: boolean;
  license_type?: string;
  created_at: string;
}

export interface ReferralRecord {
  referred_user_id: string;
  status: string;
  rewarded_at?: string;
}

export interface ReferralSummary {
  referral_code: string;
  referral_link: string;
  pending_count: number;
  earned_count: number;
  recent_referrals: ReferralRecord[];
}

export interface LeaderboardEntry {
  rank: number;
  module_name: string;
  manufacturer: string;
  count: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Feed types
export interface FeedItem {
  type: 'rack' | 'patch';
  id: number;
  name: string;
  description?: string;
  user: User;
  vote_count: number;
  created_at: string;
}

export interface FeedResponse {
  total: number;
  items: FeedItem[];
}

// Publishing types
export interface ExportArtifactUrls {
  pdf?: string;
  svg?: string;
  zip?: string;
  waveform_svg?: string;
}

export interface ExportRecord {
  id: number;
  export_type: 'patch' | 'rack';
  license: string;
  run_id: string;
  generated_at: string;
  patch_count?: number;
  manifest_hash: string;
  artifact_urls: ExportArtifactUrls;
}

export interface PublicationRecord {
  id: number;
  export_id: number;
  slug: string;
  visibility: 'public' | 'unlisted';
  status: 'published' | 'hidden' | 'draft' | 'removed';
  allow_download: boolean;
  allow_remix: boolean;
  title: string;
  description?: string;
  cover_image_url?: string;
  published_at?: string;
  updated_at: string;
}

export interface PublicationListResponse {
  publications: PublicationRecord[];
}

export interface PublicPublicationResponse {
  title: string;
  description?: string;
  cover_image_url?: string;
  export_type: 'patch' | 'rack';
  license: string;
  provenance: {
    run_id: string;
    generated_at: string;
    patch_count?: number;
    manifest_hash: string;
  };
  publisher_display: string;
  avatar_url?: string;
  allow_download: boolean;
  download_urls?: {
    pdf_url: string;
    svg_url: string;
    zip_url: string;
  };
}

export interface PublicationCard {
  slug: string;
  title: string;
  description?: string;
  cover_image_url?: string;
  export_type: 'patch' | 'rack';
  published_at?: string;
}

export interface GalleryResponse {
  publications: PublicationCard[];
  next_cursor?: string;
}
