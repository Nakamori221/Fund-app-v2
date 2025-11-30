import { useState } from 'react'
import Layout from '../components/Layout/Layout'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

// デモ用のモックデータ
const mockObservations = [
  {
    id: '1',
    field: 'revenue_mrr',
    value: '¥25,000,000',
    case_name: 'TechStartup Inc.',
    source_tag: 'CONF',
    confidence: 0.95,
    status: 'verified',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    created_by: '佐藤 次郎',
  },
  {
    id: '2',
    field: 'paid_accounts',
    value: '150',
    case_name: 'TechStartup Inc.',
    source_tag: 'CONF',
    confidence: 0.90,
    status: 'verified',
    created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    created_by: '田中 花子',
  },
  {
    id: '3',
    field: 'growth_rate',
    value: '15% MoM',
    case_name: 'AI Solutions Ltd.',
    source_tag: 'PUB',
    confidence: 0.70,
    status: 'pending',
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    created_by: '山田 太郎',
  },
  {
    id: '4',
    field: 'total_funding',
    value: '¥500,000,000',
    case_name: 'AI Solutions Ltd.',
    source_tag: 'EXT',
    confidence: 0.85,
    status: 'conflict',
    created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    created_by: '佐藤 次郎',
  },
  {
    id: '5',
    field: 'employee_count',
    value: '45',
    case_name: 'CloudPlatform Co.',
    source_tag: 'INT',
    confidence: 0.80,
    status: 'verified',
    created_at: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
    created_by: '田中 花子',
  },
]

export default function Observations() {
  const [searchQuery, setSearchQuery] = useState('')
  const [sourceFilter, setSourceFilter] = useState<string>('all')

  const filteredObservations = mockObservations.filter((obs) => {
    const matchesSearch =
      obs.field.toLowerCase().includes(searchQuery.toLowerCase()) ||
      obs.case_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesSource = sourceFilter === 'all' || obs.source_tag === sourceFilter
    return matchesSearch && matchesSource
  })

  const getSourceStyle = (tag: string) => {
    switch (tag) {
      case 'CONF': return 'bg-primary-100 text-primary-700'
      case 'PUB': return 'bg-secondary-100 text-secondary-700'
      case 'EXT': return 'bg-info/10 text-info'
      case 'INT': return 'bg-success/10 text-success'
      default: return 'bg-secondary-100 text-secondary-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <CheckCircleIcon className="h-5 w-5 text-success" />
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-warning" />
      case 'conflict':
        return <ExclamationTriangleIcon className="h-5 w-5 text-danger" />
      default:
        return null
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'verified': return '検証済み'
      case 'pending': return '確認中'
      case 'conflict': return '矛盾あり'
      default: return status
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)

    if (diffMins < 60) return `${diffMins}分前`
    if (diffHours < 24) return `${diffHours}時間前`
    return date.toLocaleDateString('ja-JP')
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-secondary-900">
              観察記録
            </h1>
            <p className="mt-3 text-base text-secondary-500">
              すべての案件のデータポイントを管理します
            </p>
          </div>
          <div className="mt-4 sm:ml-16 sm:mt-0">
            <button
              type="button"
              className="inline-flex items-center gap-x-2 rounded-xl bg-primary-600 px-5 py-3 text-base font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 hover:shadow-xl hover:shadow-primary-500/30 transition-all duration-200"
            >
              <PlusIcon className="h-5 w-5" />
              観察記録を追加
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 max-w-lg">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-secondary-400" />
            <input
              type="text"
              placeholder="フィールド名または案件名で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full rounded-xl border-0 py-3.5 pl-12 pr-4 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 placeholder:text-secondary-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 text-base transition-shadow"
            />
          </div>
          <div className="flex items-center gap-3">
            <FunnelIcon className="h-5 w-5 text-secondary-400" />
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="rounded-xl border-0 py-3.5 pl-4 pr-10 text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 focus:ring-2 focus:ring-primary-500 text-base appearance-none bg-white cursor-pointer"
            >
              <option value="all">すべてのソース</option>
              <option value="CONF">CONF（機密）</option>
              <option value="PUB">PUB（公開）</option>
              <option value="EXT">EXT（外部）</option>
              <option value="INT">INT（内部）</option>
            </select>
          </div>
        </div>

        {/* Observations Table */}
        <div className="bg-white shadow-sm ring-1 ring-secondary-200/60 rounded-2xl overflow-hidden">
          <table className="min-w-full divide-y divide-secondary-200">
            <thead className="bg-secondary-50/80">
              <tr>
                <th className="py-4 pl-6 pr-3 text-left text-sm font-semibold text-secondary-900">
                  フィールド
                </th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-secondary-900">
                  値
                </th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-secondary-900">
                  案件
                </th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-secondary-900">
                  ソース
                </th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-secondary-900">
                  信頼度
                </th>
                <th className="px-4 py-4 text-left text-sm font-semibold text-secondary-900">
                  状態
                </th>
                <th className="px-4 py-4 pr-6 text-left text-sm font-semibold text-secondary-900">
                  作成
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-secondary-100">
              {filteredObservations.map((obs) => (
                <tr key={obs.id} className="hover:bg-secondary-50/50 cursor-pointer transition-colors">
                  <td className="whitespace-nowrap py-5 pl-6 pr-3">
                    <div className="flex items-center gap-3">
                      <div className="h-9 w-9 rounded-lg bg-secondary-100 flex items-center justify-center">
                        <ChartBarIcon className="h-5 w-5 text-secondary-500" />
                      </div>
                      <span className="font-semibold text-secondary-900">{obs.field}</span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-4 py-5">
                    <span className="text-base font-bold text-secondary-900">{obs.value}</span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-5 text-sm text-secondary-600">
                    {obs.case_name}
                  </td>
                  <td className="whitespace-nowrap px-4 py-5">
                    <span className={`inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-semibold ${getSourceStyle(obs.source_tag)}`}>
                      {obs.source_tag}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-5">
                    <div className="flex items-center gap-3">
                      <div className="w-20 h-2.5 bg-secondary-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-500"
                          style={{ width: `${obs.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-secondary-600 w-10">{Math.round(obs.confidence * 100)}%</span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-4 py-5">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(obs.status)}
                      <span className="text-sm text-secondary-600">{getStatusLabel(obs.status)}</span>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-4 py-5 pr-6">
                    <div>
                      <div className="text-sm font-medium text-secondary-900">{formatTime(obs.created_at)}</div>
                      <div className="text-xs text-secondary-500 mt-0.5">{obs.created_by}</div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredObservations.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl ring-1 ring-secondary-200/60">
            <div className="mx-auto h-16 w-16 rounded-2xl bg-secondary-100 flex items-center justify-center">
              <ChartBarIcon className="h-8 w-8 text-secondary-400" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-secondary-900">観察記録が見つかりません</h3>
            <p className="mt-2 text-sm text-secondary-500">検索条件を変更してください。</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
