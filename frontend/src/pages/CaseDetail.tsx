// 案件詳細ページ - 充填率ダッシュボード
import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout/Layout'
import {
  CompletionSummaryCard,
  PhaseProgressCard,
  SectionCompletionCard,
  NextActionsCard,
  PendingFieldsCard,
} from '../components/CompletionProgress'
import {
  calculateCompletionSummary,
  generateMockObservations,
  PHASES,
} from '../services/completionService'
import type { Case, CaseCompletionSummary, Observation } from '../types'
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  TagIcon,
  CalendarIcon,
  DocumentTextIcon,
  PencilSquareIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

// デモ用のモックケースデータ
const MOCK_CASES: Record<string, Case> = {
  '1': {
    id: '1',
    company_name: 'TechCorp Inc.',
    stage: 'early',
    status: 'active',
    industry: 'SaaS / Enterprise',
    website_url: 'https://techcorp.example.com',
    location: '東京都渋谷区',
    description: 'B2B向けAI分析プラットフォームを提供するスタートアップ。急成長中のSaaS企業。',
    analyst_id: 'user-1',
    lead_partner_id: 'user-2',
    created_at: '2025-10-15T00:00:00Z',
    updated_at: '2025-11-28T00:00:00Z',
  },
  '2': {
    id: '2',
    company_name: 'HealthAI株式会社',
    stage: 'growth',
    status: 'active',
    industry: 'HealthTech / AI',
    website_url: 'https://healthai.example.com',
    location: '東京都港区',
    description: '医療AIソリューションを提供。画像診断AIで急成長中。',
    analyst_id: 'user-1',
    lead_partner_id: 'user-3',
    created_at: '2025-09-01T00:00:00Z',
    updated_at: '2025-11-25T00:00:00Z',
  },
  '3': {
    id: '3',
    company_name: 'GreenEnergy Co.',
    stage: 'seed',
    status: 'pending',
    industry: 'CleanTech / Energy',
    website_url: 'https://greenenergy.example.com',
    location: '大阪府大阪市',
    description: '再生可能エネルギー管理プラットフォーム。初期段階だが有望な技術。',
    analyst_id: 'user-2',
    created_at: '2025-11-01T00:00:00Z',
    updated_at: '2025-11-20T00:00:00Z',
  },
}

// デモ用の充填レベル
const MOCK_COMPLETION_LEVELS: Record<string, number> = {
  '1': 72,
  '2': 45,
  '3': 25,
}

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>()
  const [caseData, setCaseData] = useState<Case | null>(null)
  const [observations, setObservations] = useState<Observation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'fields' | 'history'>('overview')
  
  // データ取得（デモ用）
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      
      // デモ用の遅延
      await new Promise(resolve => setTimeout(resolve, 500))
      
      if (caseId && MOCK_CASES[caseId]) {
        setCaseData(MOCK_CASES[caseId])
        const completionLevel = MOCK_COMPLETION_LEVELS[caseId] || 30
        setObservations(generateMockObservations(caseId, completionLevel))
      }
      
      setIsLoading(false)
    }
    
    loadData()
  }, [caseId])
  
  // 充填率サマリーを計算
  const completionSummary = useMemo<CaseCompletionSummary | null>(() => {
    if (!caseId || observations.length === 0) {
      // 観測データがない場合も空のサマリーを返す
      if (caseId) {
        return calculateCompletionSummary(caseId, [])
      }
      return null
    }
    return calculateCompletionSummary(caseId, observations)
  }, [caseId, observations])
  
  // ステージのラベルと色
  const getStageInfo = (stage: Case['stage']) => {
    const stageMap = {
      seed: { label: 'Seed', color: 'bg-purple-100 text-purple-700' },
      early: { label: 'Early', color: 'bg-blue-100 text-blue-700' },
      growth: { label: 'Growth', color: 'bg-emerald-100 text-emerald-700' },
      late: { label: 'Late', color: 'bg-amber-100 text-amber-700' },
    }
    return stageMap[stage] || { label: stage, color: 'bg-secondary-100 text-secondary-700' }
  }
  
  // ステータスのラベルと色
  const getStatusInfo = (status: Case['status']) => {
    const statusMap = {
      active: { label: '進行中', color: 'bg-emerald-100 text-emerald-700' },
      pending: { label: '保留中', color: 'bg-amber-100 text-amber-700' },
      completed: { label: '完了', color: 'bg-blue-100 text-blue-700' },
      archived: { label: 'アーカイブ', color: 'bg-secondary-100 text-secondary-700' },
    }
    return statusMap[status] || { label: status, color: 'bg-secondary-100 text-secondary-700' }
  }
  
  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <ArrowPathIcon className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-4" />
            <p className="text-secondary-600">読み込み中...</p>
          </div>
        </div>
      </Layout>
    )
  }
  
  if (!caseData) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center py-12">
            <DocumentTextIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-secondary-900 mb-2">案件が見つかりません</h2>
            <p className="text-secondary-600 mb-6">指定された案件は存在しないか、アクセス権がありません。</p>
            <Link
              to="/cases"
              className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700"
            >
              <ArrowLeftIcon className="h-4 w-4" />
              案件一覧に戻る
            </Link>
          </div>
        </div>
      </Layout>
    )
  }
  
  const stageInfo = getStageInfo(caseData.stage)
  const statusInfo = getStatusInfo(caseData.status)
  
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <Link
            to="/cases"
            className="inline-flex items-center gap-2 text-sm text-secondary-500 hover:text-secondary-700 mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4" />
            案件一覧に戻る
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-secondary-900">{caseData.company_name}</h1>
                <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${stageInfo.color}`}>
                  {stageInfo.label}
                </span>
                <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
              </div>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-secondary-600">
                {caseData.industry && (
                  <span className="flex items-center gap-1">
                    <TagIcon className="h-4 w-4" />
                    {caseData.industry}
                  </span>
                )}
                {caseData.location && (
                  <span className="flex items-center gap-1">
                    <BuildingOfficeIcon className="h-4 w-4" />
                    {caseData.location}
                  </span>
                )}
                {caseData.website_url && (
                  <a 
                    href={caseData.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary-600 hover:text-primary-700"
                  >
                    <GlobeAltIcon className="h-4 w-4" />
                    Webサイト
                  </a>
                )}
              </div>
            </div>
            
            <div className="flex gap-3">
              <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-secondary-700 bg-white rounded-lg border border-secondary-300 hover:bg-secondary-50 transition-colors">
                <PencilSquareIcon className="h-4 w-4" />
                編集
              </button>
              <button className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors">
                <DocumentTextIcon className="h-4 w-4" />
                レポート生成
              </button>
            </div>
          </div>
        </div>
        
        {/* タブ */}
        <div className="border-b border-secondary-200 mb-8">
          <nav className="flex gap-8">
            {[
              { id: 'overview', label: '充填率概要' },
              { id: 'fields', label: 'フィールド詳細' },
              { id: 'history', label: '更新履歴' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`
                  pb-4 text-sm font-medium border-b-2 transition-colors
                  ${activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        
        {/* 充填率概要タブ */}
        {activeTab === 'overview' && completionSummary && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左カラム: サマリー + フェーズ */}
            <div className="lg:col-span-2 space-y-6">
              <CompletionSummaryCard summary={completionSummary} />
              <PhaseProgressCard phases={completionSummary.phases} />
            </div>
            
            {/* 右カラム: アクション + 未充填 */}
            <div className="space-y-6">
              <NextActionsCard actions={completionSummary.next_actions} />
              <PendingFieldsCard fields={completionSummary.pending_fields} maxItems={8} />
            </div>
          </div>
        )}
        
        {/* フィールド詳細タブ */}
        {activeTab === 'fields' && completionSummary && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SectionCompletionCard sections={completionSummary.sections} />
            <PendingFieldsCard fields={completionSummary.pending_fields} maxItems={20} />
          </div>
        )}
        
        {/* 更新履歴タブ（プレースホルダー） */}
        {activeTab === 'history' && (
          <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
            <h2 className="text-xl font-semibold text-secondary-900 mb-6">更新履歴</h2>
            <div className="space-y-4">
              {[
                { date: '2025-11-28', action: 'KPIデータを更新', user: '田中 太郎', fields: ['revenue_arr', 'revenue_mrr'] },
                { date: '2025-11-25', action: '競合分析を追加', user: '田中 太郎', fields: ['competition.landscape_summary'] },
                { date: '2025-11-20', action: '会社概要を入力', user: '田中 太郎', fields: ['business.problem_summary', 'business.solution_summary'] },
                { date: '2025-11-15', action: '案件を作成', user: '田中 太郎', fields: [] },
              ].map((item, index) => (
                <div key={index} className="flex items-start gap-4 p-4 rounded-lg bg-secondary-50">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                    <CalendarIcon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-secondary-900">{item.action}</span>
                      <span className="text-xs text-secondary-500">{item.date}</span>
                    </div>
                    <p className="text-xs text-secondary-600">by {item.user}</p>
                    {item.fields.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {item.fields.map(field => (
                          <span key={field} className="px-2 py-0.5 text-xs bg-secondary-200 text-secondary-700 rounded">
                            {field}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

