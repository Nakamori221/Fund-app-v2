import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout/Layout'
import { fetchCases, CaseSummary } from '../services/dashboardService'
import { CompletionBar } from '../components/CompletionProgress'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  BriefcaseIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon,
  DocumentChartBarIcon,
} from '@heroicons/react/24/outline'

export default function Cases() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: fetchCases,
  })

  const filteredCases = cases?.filter((c: CaseSummary) => {
    const matchesSearch = c.company_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter
    return matchesSearch && matchesStatus
  })

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
    switch (status) {
      case 'active': return '進行中'
      case 'on_hold': return '保留'
      case 'closed': return '完了'
      default: return status
    }
  }

  const getStageLabel = (stage: string) => {
    switch (stage) {
      case 'seed': return 'Seed'
      case 'early': return 'Early'
      case 'growth': return 'Growth'
      case 'late': return 'Late'
      default: return stage
    }
  }

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-secondary-900">
              案件管理
            </h1>
            <p className="mt-3 text-base text-secondary-500">
              すべての投資案件を管理・追跡します
            </p>
          </div>
          <div className="mt-4 sm:ml-16 sm:mt-0">
            <Link
              to="/cases/new"
              className="inline-flex items-center gap-x-2 rounded-xl bg-primary-600 px-5 py-3 text-base font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 hover:shadow-xl hover:shadow-primary-500/30 transition-all duration-200"
            >
              <PlusIcon className="h-5 w-5" aria-hidden="true" />
              新規案件
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 max-w-lg">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-secondary-400" />
            <input
              type="text"
              placeholder="会社名で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full rounded-xl border-0 py-3.5 pl-12 pr-4 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 text-base transition-shadow"
            />
          </div>
          <div className="flex items-center gap-3">
            <FunnelIcon className="h-5 w-5 text-secondary-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-xl border-0 py-3.5 pl-4 pr-10 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base appearance-none bg-white cursor-pointer"
            >
              <option value="all">すべてのステータス</option>
              <option value="active">進行中</option>
              <option value="on_hold">保留</option>
              <option value="closed">完了</option>
            </select>
          </div>
        </div>

        {/* Cases Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="animate-pulse rounded-2xl bg-white p-8 shadow-sm ring-1 ring-secondary-200/60">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-xl bg-secondary-200" />
                  <div className="flex-1">
                    <div className="h-5 w-3/4 rounded-lg bg-secondary-200" />
                    <div className="mt-2 h-4 w-1/2 rounded-lg bg-secondary-100" />
                  </div>
                </div>
                <div className="mt-8 h-10 w-full rounded-lg bg-secondary-100" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredCases?.map((caseItem: CaseSummary) => (
              <Link
                key={caseItem.case_id}
                to={`/cases/${caseItem.case_id}`}
                className="group relative rounded-2xl bg-white p-6 shadow-sm ring-1 ring-secondary-200/60 hover:shadow-lg hover:ring-primary-500/30 transition-all duration-300"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center text-primary-600 group-hover:from-primary-200 group-hover:to-primary-100 transition-colors">
                      <BriefcaseIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-secondary-900 group-hover:text-primary-600 transition-colors">
                        {caseItem.company_name}
                      </h3>
                      <p className="text-sm text-secondary-500 mt-0.5">{getStageLabel(caseItem.stage)} Stage</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${getStatusStyle(caseItem.status)}`}>
                    {getStatusLabel(caseItem.status)}
                  </span>
                </div>

                {/* 充填率バー */}
                <div className="mt-5 pt-4 border-t border-secondary-100">
                  <div className="flex items-center gap-2 mb-2">
                    <DocumentChartBarIcon className="h-4 w-4 text-secondary-400" />
                    <span className="text-xs font-medium text-secondary-600">充填率</span>
                  </div>
                  <CompletionBar rate={caseItem.completion_rate || 0} size="sm" />
                </div>

                <div className="mt-4 pt-4 border-t border-secondary-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1.5 text-secondary-600">
                        <ChartBarIcon className="h-4 w-4" />
                        <span className="text-sm font-medium">{caseItem.observation_count} 観察</span>
                      </div>
                      {caseItem.conflict_count > 0 && (
                        <div className="flex items-center gap-1.5 text-danger">
                          <ExclamationTriangleIcon className="h-4 w-4" />
                          <span className="text-sm font-medium">{caseItem.conflict_count} 矛盾</span>
                        </div>
                      )}
                    </div>
                    <ArrowRightIcon className="h-5 w-5 text-secondary-300 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                  </div>
                  <p className="mt-2 text-xs text-secondary-400">
                    更新: {formatDate(caseItem.updated_at)}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}

        {filteredCases?.length === 0 && !isLoading && (
          <div className="text-center py-16 bg-white rounded-2xl ring-1 ring-secondary-200/60">
            <div className="mx-auto h-16 w-16 rounded-2xl bg-secondary-100 flex items-center justify-center">
              <BriefcaseIcon className="h-8 w-8 text-secondary-400" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-secondary-900">案件が見つかりません</h3>
            <p className="mt-2 text-sm text-secondary-500">検索条件を変更するか、新規案件を作成してください。</p>
            <div className="mt-8">
              <Link
                to="/cases/new"
                className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 transition-all"
              >
                <PlusIcon className="h-5 w-5" aria-hidden="true" />
                新規案件を作成
              </Link>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
