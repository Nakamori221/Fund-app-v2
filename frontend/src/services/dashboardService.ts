import api from './api'

export interface DashboardStats {
  totalCases: number
  activeCases: number
  totalObservations: number
  totalConflicts: number
  pendingApprovals: number
}

export interface RecentActivity {
  id: string
  type: 'case' | 'observation' | 'conflict' | 'approval'
  action: string
  description: string
  user: string
  timestamp: string
}

export interface CaseSummary {
  case_id: string
  company_name: string
  status: string
  stage: string
  observation_count: number
  conflict_count: number
  updated_at: string
  completion_rate?: number  // 充填率（0-100）
}

// モックデータ（実際のAPIが接続できるまで使用）
export const getMockDashboardStats = (): DashboardStats => ({
  totalCases: 24,
  activeCases: 18,
  totalObservations: 342,
  totalConflicts: 8,
  pendingApprovals: 5,
})

export const getMockRecentActivities = (): RecentActivity[] => [
  {
    id: '1',
    type: 'case',
    action: 'created',
    description: '新規案件「TechStartup Inc.」を作成',
    user: '佐藤 次郎',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: '2',
    type: 'observation',
    action: 'created',
    description: '観察記録「revenue_mrr」を追加',
    user: '田中 花子',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  },
  {
    id: '3',
    type: 'conflict',
    action: 'detected',
    description: '矛盾が検出されました: revenue_mrr',
    user: 'システム',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  },
  {
    id: '4',
    type: 'approval',
    action: 'pending',
    description: '承認待ち: investment_amount',
    user: '山田 太郎',
    timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
  },
]

export const getMockCases = (): CaseSummary[] => [
  {
    case_id: '1',
    company_name: 'TechCorp Inc.',
    status: 'active',
    stage: 'early',
    observation_count: 25,
    conflict_count: 2,
    updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    completion_rate: 72,
  },
  {
    case_id: '2',
    company_name: 'HealthAI株式会社',
    status: 'active',
    stage: 'growth',
    observation_count: 42,
    conflict_count: 1,
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    completion_rate: 45,
  },
  {
    case_id: '3',
    company_name: 'GreenEnergy Co.',
    status: 'on_hold',
    stage: 'seed',
    observation_count: 10,
    conflict_count: 0,
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    completion_rate: 25,
  },
  {
    case_id: '4',
    company_name: 'FinTech Solutions',
    status: 'active',
    stage: 'late',
    observation_count: 58,
    conflict_count: 0,
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    completion_rate: 92,
  },
  {
    case_id: '5',
    company_name: 'EdTech Labs',
    status: 'active',
    stage: 'early',
    observation_count: 15,
    conflict_count: 1,
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    completion_rate: 38,
  },
]

// 実際のAPI呼び出し（後で実装）
export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  try {
    // TODO: 実際のAPIエンドポイントに接続
    // const response = await api.get('/dashboard/stats')
    // return response.data
    
    // 今はモックデータを返す
    return getMockDashboardStats()
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
    return getMockDashboardStats()
  }
}

export const fetchRecentActivities = async (): Promise<RecentActivity[]> => {
  try {
    // TODO: 実際のAPIエンドポイントに接続
    // const response = await api.get('/audit-logs?limit=10')
    // return response.data.items
    
    return getMockRecentActivities()
  } catch (error) {
    console.error('Failed to fetch recent activities:', error)
    return getMockRecentActivities()
  }
}

export const fetchCases = async (): Promise<CaseSummary[]> => {
  try {
    // TODO: 実際のAPIエンドポイントに接続
    // const response = await api.get('/cases?limit=10')
    // return response.data.items
    
    return getMockCases()
  } catch (error) {
    console.error('Failed to fetch cases:', error)
    return getMockCases()
  }
}

