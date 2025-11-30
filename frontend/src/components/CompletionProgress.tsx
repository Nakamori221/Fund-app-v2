// 充填率プログレスコンポーネント
import {
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentMagnifyingGlassIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import type { CaseCompletionSummary, PhaseCompletion, SectionCompletion, NextAction, CollectionPhase } from '../types'

interface CompletionProgressProps {
  summary: CaseCompletionSummary
}

// フェーズアイコンを取得
function getPhaseIcon(phase: CollectionPhase) {
  switch (phase) {
    case 'phase1_existing':
      return DocumentTextIcon
    case 'phase2_web':
      return DocumentMagnifyingGlassIcon
    case 'phase3_conf':
      return ChartBarIcon
    case 'phase4_interview':
      return UserGroupIcon
    default:
      return DocumentTextIcon
  }
}

// 完了率に応じた色を取得
function getCompletionColor(rate: number): string {
  if (rate >= 80) return 'text-emerald-600'
  if (rate >= 50) return 'text-amber-600'
  return 'text-rose-600'
}

function getCompletionBgColor(rate: number): string {
  if (rate >= 80) return 'bg-emerald-500'
  if (rate >= 50) return 'bg-amber-500'
  return 'bg-rose-500'
}

// メインの充填率サマリーカード
export function CompletionSummaryCard({ summary }: CompletionProgressProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-secondary-900">充填率サマリー</h2>
        <span className={`text-3xl font-bold ${getCompletionColor(summary.overall_completion_rate)}`}>
          {summary.overall_completion_rate}%
        </span>
      </div>
      
      {/* 全体プログレスバー */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-secondary-600 mb-2">
          <span>全体進捗</span>
          <span>{summary.filled_fields} / {summary.total_fields} フィールド</span>
        </div>
        <div className="h-4 bg-secondary-100 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-500 ${getCompletionBgColor(summary.overall_completion_rate)}`}
            style={{ width: `${summary.overall_completion_rate}%` }}
          />
        </div>
      </div>
      
      {/* IC/LP 別の完了率 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-secondary-50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium text-secondary-500 uppercase tracking-wide">IC資料</span>
            <span className={`text-lg font-bold ${getCompletionColor(summary.ic_completion_rate)}`}>
              {summary.ic_completion_rate}%
            </span>
          </div>
          <div className="h-2 bg-secondary-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${getCompletionBgColor(summary.ic_completion_rate)}`}
              style={{ width: `${summary.ic_completion_rate}%` }}
            />
          </div>
        </div>
        <div className="bg-secondary-50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium text-secondary-500 uppercase tracking-wide">LP資料</span>
            <span className={`text-lg font-bold ${getCompletionColor(summary.lp_completion_rate)}`}>
              {summary.lp_completion_rate}%
            </span>
          </div>
          <div className="h-2 bg-secondary-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${getCompletionBgColor(summary.lp_completion_rate)}`}
              style={{ width: `${summary.lp_completion_rate}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

// フェーズ別プログレス
export function PhaseProgressCard({ phases }: { phases: PhaseCompletion[] }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
      <h2 className="text-xl font-semibold text-secondary-900 mb-6">フェーズ別進捗</h2>
      
      <div className="space-y-6">
        {phases.map((phase, index) => {
          const Icon = getPhaseIcon(phase.phase)
          const isComplete = phase.completion_rate === 100
          
          return (
            <div key={phase.phase} className="relative">
              {/* 接続線 */}
              {index < phases.length - 1 && (
                <div className="absolute left-5 top-12 w-0.5 h-8 bg-secondary-200" />
              )}
              
              <div className="flex items-start gap-4">
                {/* アイコン */}
                <div className={`
                  flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center
                  ${isComplete ? 'bg-emerald-100 text-emerald-600' : 'bg-secondary-100 text-secondary-500'}
                `}>
                  {isComplete ? (
                    <CheckCircleIcon className="h-6 w-6" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                
                {/* コンテンツ */}
                <div className="flex-grow min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-secondary-900">{phase.phase_name}</h3>
                    <span className={`text-sm font-semibold ${getCompletionColor(phase.completion_rate)}`}>
                      {phase.completion_rate}%
                    </span>
                  </div>
                  
                  {/* プログレスバー */}
                  <div className="h-2 bg-secondary-100 rounded-full overflow-hidden mb-1">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${getCompletionBgColor(phase.completion_rate)}`}
                      style={{ width: `${phase.completion_rate}%` }}
                    />
                  </div>
                  
                  <div className="flex justify-between text-xs text-secondary-500">
                    <span>{phase.filled_fields} / {phase.fillable_fields} フィールド</span>
                    <span>累計: {phase.cumulative_rate}%</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// セクション別充填状況
export function SectionCompletionCard({ sections }: { sections: SectionCompletion[] }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
      <h2 className="text-xl font-semibold text-secondary-900 mb-6">セクション別進捗</h2>
      
      <div className="space-y-4">
        {sections.map(section => (
          <div key={section.section_id} className="group">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-secondary-700 group-hover:text-secondary-900">
                {section.section_name}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-secondary-500">
                  {section.filled_fields}/{section.total_fields}
                </span>
                <span className={`text-sm font-semibold ${getCompletionColor(section.completion_rate)}`}>
                  {section.completion_rate}%
                </span>
              </div>
            </div>
            <div className="h-2 bg-secondary-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-300 ${getCompletionBgColor(section.completion_rate)}`}
                style={{ width: `${section.completion_rate}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// 次のアクション
export function NextActionsCard({ actions }: { actions: NextAction[] }) {
  const getPriorityBadge = (priority: NextAction['priority']) => {
    switch (priority) {
      case 'high':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-rose-100 text-rose-700">高</span>
      case 'medium':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-100 text-amber-700">中</span>
      case 'low':
        return <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-secondary-100 text-secondary-700">低</span>
    }
  }
  
  const getActionIcon = (actionType: NextAction['action_type']) => {
    switch (actionType) {
      case 'web_research':
        return DocumentMagnifyingGlassIcon
      case 'collect_conf':
        return DocumentTextIcon
      case 'schedule_interview':
        return UserGroupIcon
      case 'verify_data':
        return CheckCircleIcon
      default:
        return ClockIcon
    }
  }
  
  if (actions.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">次のアクション</h2>
        <div className="text-center py-8">
          <CheckCircleIcon className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
          <p className="text-secondary-600">すべての情報が収集されました！</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
      <h2 className="text-xl font-semibold text-secondary-900 mb-4">次のアクション</h2>
      
      <div className="space-y-3">
        {actions.map((action, index) => {
          const Icon = getActionIcon(action.action_type)
          
          return (
            <div 
              key={index}
              className="flex items-start gap-3 p-3 rounded-xl bg-secondary-50 hover:bg-secondary-100 transition-colors"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-white shadow-sm flex items-center justify-center">
                <Icon className="h-4 w-4 text-secondary-600" />
              </div>
              <div className="flex-grow min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {getPriorityBadge(action.priority)}
                  <span className="text-xs text-secondary-500">{action.responsible_role}</span>
                </div>
                <p className="text-sm text-secondary-900">{action.description}</p>
                <p className="text-xs text-secondary-500 mt-1">
                  対象: {action.target_fields.length}項目
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// 未充填フィールドリスト
export function PendingFieldsCard({ fields, maxItems = 10 }: { fields: CaseCompletionSummary['pending_fields']; maxItems?: number }) {
  const displayFields = fields.slice(0, maxItems)
  const remainingCount = fields.length - maxItems
  
  const getPhaseLabel = (phase: CollectionPhase) => {
    switch (phase) {
      case 'phase1_existing': return 'PUB'
      case 'phase2_web': return 'EXT'
      case 'phase3_conf': return 'CONF'
      case 'phase4_interview': return 'INT'
      default: return ''
    }
  }
  
  const getPhaseBadgeColor = (phase: CollectionPhase) => {
    switch (phase) {
      case 'phase1_existing': return 'bg-blue-100 text-blue-700'
      case 'phase2_web': return 'bg-purple-100 text-purple-700'
      case 'phase3_conf': return 'bg-rose-100 text-rose-700'
      case 'phase4_interview': return 'bg-amber-100 text-amber-700'
      default: return 'bg-secondary-100 text-secondary-700'
    }
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-lg ring-1 ring-secondary-900/5 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-secondary-900">未充填項目</h2>
        <span className="text-sm text-secondary-500">{fields.length}件</span>
      </div>
      
      {fields.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircleIcon className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
          <p className="text-secondary-600">すべて充填済みです！</p>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {displayFields.map(field => (
              <div 
                key={field.field_id}
                className="flex items-center justify-between p-3 rounded-lg bg-secondary-50 hover:bg-secondary-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <ExclamationTriangleIcon className="h-4 w-4 text-amber-500 flex-shrink-0" />
                  <span className="text-sm text-secondary-900">{field.field_name}</span>
                </div>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getPhaseBadgeColor(field.phase_available)}`}>
                  {getPhaseLabel(field.phase_available)}
                </span>
              </div>
            ))}
          </div>
          
          {remainingCount > 0 && (
            <p className="text-sm text-secondary-500 text-center mt-4">
              他 {remainingCount} 件の未充填項目があります
            </p>
          )}
        </>
      )}
    </div>
  )
}

// コンパクトな充填率バー（一覧用）
export function CompletionBar({ rate, size = 'md' }: { rate: number; size?: 'sm' | 'md' }) {
  const height = size === 'sm' ? 'h-1.5' : 'h-2'
  
  return (
    <div className="flex items-center gap-2">
      <div className={`flex-grow ${height} bg-secondary-100 rounded-full overflow-hidden`}>
        <div 
          className={`h-full rounded-full transition-all duration-300 ${getCompletionBgColor(rate)}`}
          style={{ width: `${rate}%` }}
        />
      </div>
      <span className={`text-xs font-medium ${getCompletionColor(rate)} min-w-[2.5rem] text-right`}>
        {rate}%
      </span>
    </div>
  )
}

