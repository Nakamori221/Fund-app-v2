// 共通型定義

export interface ApiError {
  error_code: string
  message: string
  details?: Record<string, unknown>
  timestamp?: string
  request_id?: string
}

export interface PaginationParams {
  skip?: number
  limit?: number
  page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    total: number
    page: number
    limit: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}

// ソースタグ定義
export type SourceTag = 'PUB' | 'EXT' | 'INT' | 'CONF' | 'ANL'

// 開示レベル定義
export type DisclosureLevel = 'IC' | 'LP' | 'LP_NDA' | 'PRIVATE'

// フィールド定義
export interface FieldDefinition {
  id: string
  category: string
  section: string
  display_name: string
  value_type: 'number' | 'string' | 'json' | 'date' | 'range'
  unit?: string
  source_priority: SourceTag[]
  disclosure_default: DisclosureLevel
  required_for_ic: boolean
  required_for_lp: boolean
}

// 観測データ（フィールド値）
export interface Observation {
  id: string
  case_id: string
  field_id: string
  value: string | number | object | null
  source_tag: SourceTag
  disclosure_level: DisclosureLevel
  evidence_url?: string
  as_of_date: string
  created_by: string
  created_at: string
  updated_at: string
  is_approved: boolean
}

// フェーズ定義
export type CollectionPhase = 'phase1_existing' | 'phase2_web' | 'phase3_conf' | 'phase4_interview'

export interface PhaseInfo {
  id: CollectionPhase
  name: string
  description: string
  source_tags: SourceTag[]
  order: number
}

// 充填状況
export interface FieldCompletionStatus {
  field_id: string
  field_name: string
  section: string
  is_filled: boolean
  current_source?: SourceTag
  required_source: SourceTag[]
  disclosure_level?: DisclosureLevel
  filled_at?: string
  filled_by?: string
  phase_available: CollectionPhase
}

// セクション別充填状況
export interface SectionCompletion {
  section_id: string
  section_name: string
  total_fields: number
  filled_fields: number
  completion_rate: number
  fields: FieldCompletionStatus[]
}

// フェーズ別充填状況
export interface PhaseCompletion {
  phase: CollectionPhase
  phase_name: string
  fillable_fields: number
  filled_fields: number
  completion_rate: number
  cumulative_rate: number
}

// 案件の充填率サマリー
export interface CaseCompletionSummary {
  case_id: string
  total_fields: number
  filled_fields: number
  overall_completion_rate: number
  ic_completion_rate: number
  lp_completion_rate: number
  phases: PhaseCompletion[]
  sections: SectionCompletion[]
  pending_fields: FieldCompletionStatus[]
  next_actions: NextAction[]
}

// 次のアクション提案
export interface NextAction {
  priority: 'high' | 'medium' | 'low'
  action_type: 'collect_conf' | 'schedule_interview' | 'web_research' | 'verify_data'
  description: string
  target_fields: string[]
  responsible_role: string
}

// 案件型
export interface Case {
  id: string
  company_name: string
  stage: 'seed' | 'early' | 'growth' | 'late'
  status: 'active' | 'pending' | 'completed' | 'archived'
  industry?: string
  website_url?: string
  location?: string
  description?: string
  analyst_id: string
  lead_partner_id?: string
  created_at: string
  updated_at: string
  completion_summary?: CaseCompletionSummary
}

// ユーザー型
export interface User {
  id: string
  email: string
  name: string
  role: 'analyst' | 'lead_partner' | 'ic_member' | 'admin'
  is_active: boolean
  created_at: string
}
