import { CaseSummary } from '../services/dashboardService'
import {
    BriefcaseIcon,
    ChartBarIcon,
    ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

interface CasesTableProps {
  cases: CaseSummary[]
  loading?: boolean
}

export default function CasesTable({ cases, loading = false }: CasesTableProps) {
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success ring-success/20'
      case 'on_hold':
        return 'bg-warning/10 text-warning ring-warning/20'
      case 'closed':
        return 'bg-secondary-100 text-secondary-600 ring-secondary-500/10'
      default:
        return 'bg-secondary-100 text-secondary-600 ring-secondary-500/10'
    }
  }

  const getStatusLabel = (status: string) => {
      switch(status) {
          case 'active': return '進行中'
          case 'on_hold': return '保留'
          case 'closed': return '完了'
          default: return status
      }
  }

  const getStageLabel = (stage: string) => {
      return stage.charAt(0).toUpperCase() + stage.slice(1)
  }

  if (loading) {
    return (
        <div className="overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-secondary-900/5 p-6">
            <div className="animate-pulse space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-12 bg-secondary-100 rounded-md" />
                ))}
            </div>
        </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-secondary-900/5">
      <table className="min-w-full divide-y divide-secondary-300">
        <thead className="bg-secondary-50">
          <tr>
            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-secondary-900 sm:pl-6">
              会社名
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-secondary-900">
              ステージ
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-secondary-900">
              ステータス
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-secondary-900">
              観察記録
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-secondary-900">
              矛盾
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-secondary-900">
              最終更新
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-secondary-200 bg-white">
          {cases.length === 0 ? (
            <tr>
              <td colSpan={6} className="py-8 text-center text-secondary-500">
                案件がありません
              </td>
            </tr>
          ) : (
            cases.map((caseItem) => (
              <tr
                key={caseItem.case_id}
                className="hover:bg-secondary-50 transition-colors duration-150 cursor-pointer"
              >
                <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-secondary-900 sm:pl-6">
                  <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600">
                          <BriefcaseIcon className="h-4 w-4" />
                      </div>
                      {caseItem.company_name}
                  </div>
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-secondary-500">
                  {getStageLabel(caseItem.stage)}
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm">
                  <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getStatusStyle(caseItem.status)}`}>
                    {getStatusLabel(caseItem.status)}
                  </span>
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-secondary-500">
                    <div className="flex items-center gap-1">
                        <ChartBarIcon className="h-4 w-4 text-secondary-400" />
                        {caseItem.observation_count}
                    </div>
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-secondary-500">
                  {caseItem.conflict_count > 0 ? (
                    <span className="inline-flex items-center gap-1 rounded-md bg-danger/10 px-2 py-1 text-xs font-medium text-danger ring-1 ring-inset ring-danger/20">
                      <ExclamationTriangleIcon className="h-3 w-3" />
                      {caseItem.conflict_count}
                    </span>
                  ) : (
                    <span className="text-secondary-400">-</span>
                  )}
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-secondary-500">
                  {formatDate(caseItem.updated_at)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
