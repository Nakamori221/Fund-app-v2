// 充填率計算サービス
import type {
  SourceTag,
  CollectionPhase,
  FieldDefinition,
  Observation,
  FieldCompletionStatus,
  SectionCompletion,
  PhaseCompletion,
  CaseCompletionSummary,
  NextAction,
} from '../types'

// フェーズ定義
export const PHASES: Record<CollectionPhase, { name: string; description: string; source_tags: SourceTag[]; order: number }> = {
  phase1_existing: {
    name: 'Phase 1: 既存資料',
    description: '営業資料、HP、公開情報から収集',
    source_tags: ['PUB'],
    order: 1,
  },
  phase2_web: {
    name: 'Phase 2: Web調査',
    description: 'Crunchbase、LinkedIn、業界レポート等から収集',
    source_tags: ['PUB', 'EXT'],
    order: 2,
  },
  phase3_conf: {
    name: 'Phase 3: 機密情報',
    description: 'Term Sheet、財務モデル、Cap Table等',
    source_tags: ['CONF'],
    order: 3,
  },
  phase4_interview: {
    name: 'Phase 4: インタビュー',
    description: '経営陣ヒアリング、詳細確認',
    source_tags: ['INT'],
    order: 4,
  },
}

// セクション定義（レポートテンプレートに基づく）
export const SECTIONS = [
  { id: 'exec_summary', name: '投資推奨サマリー', order: 10 },
  { id: 'company_overview', name: '会社概要・課題解決', order: 20 },
  { id: 'market_analysis', name: '市場規模・Why Now', order: 30 },
  { id: 'competition', name: '競合・差別化', order: 40 },
  { id: 'kpi_overview', name: '主要KPI', order: 50 },
  { id: 'financials', name: '財務ハイライト', order: 60 },
  { id: 'team', name: 'チーム', order: 70 },
  { id: 'deal_terms', name: 'ディール条件', order: 80 },
  { id: 'valuation_return', name: 'バリュエーション', order: 90 },
  { id: 'risk_mitigation', name: 'リスク・対策', order: 100 },
  { id: 'value_creation', name: '価値創造計画', order: 110 },
  { id: 'appendix', name: '想定Q&A', order: 120 },
]

// フィールド定義（field_dictionary_v0_1.jsonに基づく簡略版）
export const FIELD_DEFINITIONS: FieldDefinition[] = [
  // エグゼクティブサマリー
  { id: 'thesis.statement', category: 'exec_summary', section: 'exec_summary', display_name: '投資テーゼ', value_type: 'string', source_priority: ['ANL', 'INT'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'thesis.reason_1', category: 'exec_summary', section: 'exec_summary', display_name: '投資理由1', value_type: 'string', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'thesis.reason_2', category: 'exec_summary', section: 'exec_summary', display_name: '投資理由2', value_type: 'string', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: false },
  { id: 'thesis.reason_3', category: 'exec_summary', section: 'exec_summary', display_name: '投資理由3', value_type: 'string', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: false },
  
  // 会社概要
  { id: 'business.problem_summary', category: 'business', section: 'company_overview', display_name: '課題サマリー', value_type: 'string', source_priority: ['PUB', 'INT'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'business.solution_summary', category: 'business', section: 'company_overview', display_name: 'ソリューション', value_type: 'string', source_priority: ['PUB'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'business.model_summary', category: 'business', section: 'company_overview', display_name: 'ビジネスモデル', value_type: 'string', source_priority: ['ANL', 'PUB'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'product.overview', category: 'product', section: 'company_overview', display_name: 'プロダクト概要', value_type: 'string', source_priority: ['PUB'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'product.roadmap_key', category: 'product', section: 'company_overview', display_name: 'ロードマップ', value_type: 'json', source_priority: ['INT', 'CONF'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  
  // 市場分析
  { id: 'market.size_tam', category: 'market', section: 'market_analysis', display_name: 'TAM', value_type: 'json', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'market.size_sam', category: 'market', section: 'market_analysis', display_name: 'SAM', value_type: 'json', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'market.size_som', category: 'market', section: 'market_analysis', display_name: 'SOM', value_type: 'json', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: false },
  { id: 'market.why_now', category: 'market', section: 'market_analysis', display_name: 'Why Now', value_type: 'string', source_priority: ['PUB', 'ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  
  // 競合
  { id: 'competition.landscape_summary', category: 'competition', section: 'competition', display_name: '競合環境', value_type: 'string', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'competition.key_differentiators', category: 'competition', section: 'competition', display_name: '差別化要因', value_type: 'json', source_priority: ['ANL', 'INT'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  
  // KPI
  { id: 'revenue_arr', category: 'kpi', section: 'kpi_overview', display_name: 'ARR', value_type: 'number', unit: 'USD', source_priority: ['CONF', 'ANL', 'PUB'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'revenue_mrr', category: 'kpi', section: 'kpi_overview', display_name: 'MRR', value_type: 'number', unit: 'USD', source_priority: ['CONF', 'ANL', 'PUB'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'net_dollar_retention_annual', category: 'kpi', section: 'kpi_overview', display_name: 'NDR', value_type: 'number', unit: 'percent', source_priority: ['CONF', 'INT', 'ANL'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: true },
  { id: 'logo_churn_rate_monthly', category: 'kpi', section: 'kpi_overview', display_name: 'チャーン率', value_type: 'number', unit: 'percent', source_priority: ['CONF', 'INT'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  { id: 'ltv_cac_ratio', category: 'kpi', section: 'kpi_overview', display_name: 'LTV/CAC', value_type: 'number', unit: 'ratio', source_priority: ['ANL'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  { id: 'paid_accounts', category: 'kpi_support', section: 'kpi_overview', display_name: '有料アカウント数', value_type: 'number', unit: 'count', source_priority: ['CONF', 'INT', 'PUB'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  { id: 'gross_margin_pct', category: 'kpi_support', section: 'kpi_overview', display_name: '粗利率', value_type: 'number', unit: 'percent', source_priority: ['CONF', 'INT'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  
  // 財務
  { id: 'financials.summary', category: 'financials', section: 'financials', display_name: '財務サマリー', value_type: 'string', source_priority: ['CONF'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  { id: 'financials.forecast_highlights', category: 'financials', section: 'financials', display_name: '予測ハイライト', value_type: 'string', source_priority: ['CONF', 'ANL'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  
  // チーム
  { id: 'team.overview', category: 'team', section: 'team', display_name: 'チーム概要', value_type: 'string', source_priority: ['PUB', 'CONF'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'team.gap_and_plan', category: 'team', section: 'team', display_name: '採用計画', value_type: 'string', source_priority: ['INT'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  
  // ディール条件
  { id: 'deal.investment_amount', category: 'deal_terms', section: 'deal_terms', display_name: '投資額', value_type: 'number', unit: 'USD', source_priority: ['CONF'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  { id: 'deal.ownership', category: 'deal_terms', section: 'deal_terms', display_name: '持分比率', value_type: 'number', unit: 'percent', source_priority: ['CONF'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  { id: 'deal.valuation_pre', category: 'valuation', section: 'deal_terms', display_name: 'Pre-Money評価額', value_type: 'number', unit: 'USD', source_priority: ['CONF'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  { id: 'deal.key_terms_summary', category: 'deal_terms', section: 'deal_terms', display_name: '主要条件', value_type: 'string', source_priority: ['CONF'], disclosure_default: 'IC', required_for_ic: true, required_for_lp: false },
  
  // バリュエーション
  { id: 'deal.valuation_pre_range', category: 'valuation', section: 'valuation_return', display_name: '評価額レンジ', value_type: 'range', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: false, required_for_lp: true },
  
  // リスク
  { id: 'risk.top_list', category: 'risk', section: 'risk_mitigation', display_name: '主要リスク', value_type: 'json', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'risk.mitigations', category: 'risk', section: 'risk_mitigation', display_name: 'リスク対策', value_type: 'json', source_priority: ['ANL', 'INT'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  
  // 価値創造
  { id: 'value_creation.plan_summary', category: 'value_creation', section: 'value_creation', display_name: '価値創造計画', value_type: 'string', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: true, required_for_lp: true },
  { id: 'value_creation.next_milestones', category: 'value_creation', section: 'value_creation', display_name: '次のマイルストーン', value_type: 'json', source_priority: ['CONF', 'INT'], disclosure_default: 'LP_NDA', required_for_ic: true, required_for_lp: false },
  
  // 補足
  { id: 'appendix.key_questions', category: 'appendix', section: 'appendix', display_name: '想定Q&A', value_type: 'json', source_priority: ['ANL'], disclosure_default: 'LP', required_for_ic: false, required_for_lp: false },
]

// ソースタグからフェーズを判定
export function getPhaseFromSourceTag(sourceTag: SourceTag): CollectionPhase {
  switch (sourceTag) {
    case 'PUB':
      return 'phase1_existing'
    case 'EXT':
      return 'phase2_web'
    case 'CONF':
      return 'phase3_conf'
    case 'INT':
      return 'phase4_interview'
    case 'ANL':
      // ANLは他のデータから派生するため、最も遅いフェーズに分類
      return 'phase4_interview'
    default:
      return 'phase1_existing'
  }
}

// フィールドが収集可能な最も早いフェーズを判定
export function getEarliestPhaseForField(field: FieldDefinition): CollectionPhase {
  const priorities = field.source_priority
  
  // PUBが最優先なら Phase 1
  if (priorities.includes('PUB')) return 'phase1_existing'
  // EXTが含まれるなら Phase 2
  if (priorities.includes('EXT')) return 'phase2_web'
  // CONFが含まれるなら Phase 3
  if (priorities.includes('CONF')) return 'phase3_conf'
  // INTが含まれるなら Phase 4
  if (priorities.includes('INT')) return 'phase4_interview'
  // ANLのみなら Phase 4（分析は最後）
  return 'phase4_interview'
}

// 充填率を計算
export function calculateCompletionSummary(
  caseId: string,
  observations: Observation[]
): CaseCompletionSummary {
  const filledFieldIds = new Set(observations.map(o => o.field_id))
  
  // フィールド別の充填状況を計算
  const fieldStatuses: FieldCompletionStatus[] = FIELD_DEFINITIONS.map(field => {
    const observation = observations.find(o => o.field_id === field.id)
    return {
      field_id: field.id,
      field_name: field.display_name,
      section: field.section,
      is_filled: filledFieldIds.has(field.id),
      current_source: observation?.source_tag,
      required_source: field.source_priority,
      disclosure_level: observation?.disclosure_level,
      filled_at: observation?.created_at,
      filled_by: observation?.created_by,
      phase_available: getEarliestPhaseForField(field),
    }
  })
  
  // セクション別の充填状況を計算
  const sectionCompletions: SectionCompletion[] = SECTIONS.map(section => {
    const sectionFields = fieldStatuses.filter(f => f.section === section.id)
    const filledCount = sectionFields.filter(f => f.is_filled).length
    return {
      section_id: section.id,
      section_name: section.name,
      total_fields: sectionFields.length,
      filled_fields: filledCount,
      completion_rate: sectionFields.length > 0 ? Math.round((filledCount / sectionFields.length) * 100) : 0,
      fields: sectionFields,
    }
  }).filter(s => s.total_fields > 0)
  
  // フェーズ別の充填状況を計算
  const phaseOrder: CollectionPhase[] = ['phase1_existing', 'phase2_web', 'phase3_conf', 'phase4_interview']
  let cumulativeTotal = 0
  let cumulativeFilled = 0
  
  const phaseCompletions: PhaseCompletion[] = phaseOrder.map(phaseId => {
    const phaseFields = fieldStatuses.filter(f => f.phase_available === phaseId)
    const filledCount = phaseFields.filter(f => f.is_filled).length
    
    cumulativeTotal += phaseFields.length
    cumulativeFilled += filledCount
    
    return {
      phase: phaseId,
      phase_name: PHASES[phaseId].name,
      fillable_fields: phaseFields.length,
      filled_fields: filledCount,
      completion_rate: phaseFields.length > 0 ? Math.round((filledCount / phaseFields.length) * 100) : 0,
      cumulative_rate: cumulativeTotal > 0 ? Math.round((cumulativeFilled / cumulativeTotal) * 100) : 0,
    }
  })
  
  // IC/LP別の充填率
  const icFields = FIELD_DEFINITIONS.filter(f => f.required_for_ic)
  const lpFields = FIELD_DEFINITIONS.filter(f => f.required_for_lp)
  const icFilled = icFields.filter(f => filledFieldIds.has(f.id)).length
  const lpFilled = lpFields.filter(f => filledFieldIds.has(f.id)).length
  
  // 未充填フィールド（優先度順）
  const pendingFields = fieldStatuses
    .filter(f => !f.is_filled)
    .sort((a, b) => {
      // フェーズ順でソート
      const phaseOrderMap: Record<CollectionPhase, number> = {
        phase1_existing: 1,
        phase2_web: 2,
        phase3_conf: 3,
        phase4_interview: 4,
      }
      return phaseOrderMap[a.phase_available] - phaseOrderMap[b.phase_available]
    })
  
  // 次のアクション提案
  const nextActions = generateNextActions(pendingFields, phaseCompletions)
  
  return {
    case_id: caseId,
    total_fields: FIELD_DEFINITIONS.length,
    filled_fields: filledFieldIds.size,
    overall_completion_rate: Math.round((filledFieldIds.size / FIELD_DEFINITIONS.length) * 100),
    ic_completion_rate: icFields.length > 0 ? Math.round((icFilled / icFields.length) * 100) : 0,
    lp_completion_rate: lpFields.length > 0 ? Math.round((lpFilled / lpFields.length) * 100) : 0,
    phases: phaseCompletions,
    sections: sectionCompletions,
    pending_fields: pendingFields,
    next_actions: nextActions,
  }
}

// 次のアクションを生成
function generateNextActions(
  pendingFields: FieldCompletionStatus[],
  phaseCompletions: PhaseCompletion[]
): NextAction[] {
  const actions: NextAction[] = []
  
  // Phase 1 が未完了なら Web調査を推奨
  const phase1 = phaseCompletions.find(p => p.phase === 'phase1_existing')
  if (phase1 && phase1.completion_rate < 100) {
    const phase1Pending = pendingFields.filter(f => f.phase_available === 'phase1_existing')
    if (phase1Pending.length > 0) {
      actions.push({
        priority: 'high',
        action_type: 'web_research',
        description: '公開情報の収集を完了してください',
        target_fields: phase1Pending.map(f => f.field_id),
        responsible_role: 'analyst',
      })
    }
  }
  
  // Phase 2 の未完了項目
  const phase2Pending = pendingFields.filter(f => f.phase_available === 'phase2_web')
  if (phase2Pending.length > 0 && phase1 && phase1.completion_rate >= 50) {
    actions.push({
      priority: 'medium',
      action_type: 'web_research',
      description: '外部データソース（Crunchbase等）から情報を収集',
      target_fields: phase2Pending.map(f => f.field_id),
      responsible_role: 'analyst',
    })
  }
  
  // Phase 3 の CONF 項目
  const phase3Pending = pendingFields.filter(f => f.phase_available === 'phase3_conf')
  if (phase3Pending.length > 0) {
    actions.push({
      priority: 'high',
      action_type: 'collect_conf',
      description: '機密情報（Term Sheet、財務モデル等）の入手',
      target_fields: phase3Pending.map(f => f.field_id),
      responsible_role: 'lead_partner',
    })
  }
  
  // Phase 4 の INT 項目
  const phase4Pending = pendingFields.filter(f => f.phase_available === 'phase4_interview')
  if (phase4Pending.length > 0) {
    actions.push({
      priority: 'medium',
      action_type: 'schedule_interview',
      description: '経営陣インタビューの実施',
      target_fields: phase4Pending.map(f => f.field_id),
      responsible_role: 'analyst',
    })
  }
  
  return actions.slice(0, 5) // 最大5件
}

// デモ用のモックデータ生成
export function generateMockObservations(caseId: string, completionLevel: number): Observation[] {
  const observations: Observation[] = []
  const fieldsToFill = Math.floor(FIELD_DEFINITIONS.length * (completionLevel / 100))
  
  // 優先度順にフィールドを選択
  const sortedFields = [...FIELD_DEFINITIONS].sort((a, b) => {
    const phaseOrder: Record<CollectionPhase, number> = {
      phase1_existing: 1,
      phase2_web: 2,
      phase3_conf: 3,
      phase4_interview: 4,
    }
    return phaseOrder[getEarliestPhaseForField(a)] - phaseOrder[getEarliestPhaseForField(b)]
  })
  
  for (let i = 0; i < fieldsToFill && i < sortedFields.length; i++) {
    const field = sortedFields[i]
    const sourceTag = field.source_priority[0]
    
    observations.push({
      id: `obs-${caseId}-${field.id}`,
      case_id: caseId,
      field_id: field.id,
      value: getMockValue(field),
      source_tag: sourceTag,
      disclosure_level: field.disclosure_default,
      evidence_url: `https://example.com/evidence/${field.id}`,
      as_of_date: new Date().toISOString().split('T')[0],
      created_by: 'demo-user',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_approved: Math.random() > 0.3,
    })
  }
  
  return observations
}

function getMockValue(field: FieldDefinition): string | number | object {
  switch (field.value_type) {
    case 'number':
      if (field.unit === 'USD') return Math.floor(Math.random() * 10000000) + 100000
      if (field.unit === 'percent') return Math.floor(Math.random() * 100)
      if (field.unit === 'ratio') return Math.round((Math.random() * 5 + 1) * 10) / 10
      return Math.floor(Math.random() * 1000)
    case 'string':
      return `${field.display_name}のサンプルデータ`
    case 'json':
      return { items: ['項目1', '項目2', '項目3'] }
    default:
      return ''
  }
}

