import { useState } from 'react'
import Layout from '../components/Layout/Layout'
import {
  PlusIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  ClockIcon,
  CheckCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

// デモ用のモックデータ
const mockReports = [
  {
    id: '1',
    title: 'TechStartup Inc. - IC投資メモ',
    case_name: 'TechStartup Inc.',
    template: 'IC Default',
    status: 'completed',
    format: 'PDF',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    created_by: '佐藤 次郎',
    word_count: 5420,
  },
  {
    id: '2',
    title: 'AI Solutions Ltd. - 投資推奨サマリー',
    case_name: 'AI Solutions Ltd.',
    template: 'LP Summary',
    status: 'completed',
    format: 'Word',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    created_by: '田中 花子',
    word_count: 3200,
  },
  {
    id: '3',
    title: 'CloudPlatform Co. - デューデリジェンスレポート',
    case_name: 'CloudPlatform Co.',
    template: 'DD Report',
    status: 'generating',
    format: 'PDF',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    created_by: '山田 太郎',
    word_count: 0,
  },
]

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)

  const getStatusBadge = (status: string) => {
    if (status === 'completed') {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-success/10 px-3 py-1.5 text-xs font-semibold text-success ring-1 ring-inset ring-success/20">
          <CheckCircleIcon className="h-4 w-4" />
          完了
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1.5 rounded-lg bg-warning/10 px-3 py-1.5 text-xs font-semibold text-warning ring-1 ring-inset ring-warning/20">
        <SparklesIcon className="h-4 w-4 animate-pulse" />
        生成中...
      </span>
    )
  }

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-secondary-900">
              レポート
            </h1>
            <p className="mt-3 text-base text-secondary-500">
              生成されたレポートの管理とダウンロード
            </p>
          </div>
          <div className="mt-4 sm:ml-16 sm:mt-0">
            <button
              type="button"
              className="inline-flex items-center gap-x-2 rounded-xl bg-primary-600 px-5 py-3 text-base font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 hover:shadow-xl hover:shadow-primary-500/30 transition-all duration-200"
            >
              <PlusIcon className="h-5 w-5" />
              新規レポート作成
            </button>
          </div>
        </div>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {mockReports.map((report) => (
            <div
              key={report.id}
              className={`group bg-white shadow-sm ring-1 ring-secondary-200/60 rounded-2xl p-8 hover:shadow-lg transition-all duration-300 cursor-pointer ${
                selectedReport === report.id ? 'ring-2 ring-primary-500 shadow-lg' : ''
              }`}
              onClick={() => setSelectedReport(report.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center group-hover:from-primary-200 group-hover:to-primary-100 transition-colors">
                    <DocumentTextIcon className="h-7 w-7 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-secondary-900 group-hover:text-primary-600 transition-colors">{report.title}</h3>
                    <p className="text-sm text-secondary-500 mt-1">{report.case_name}</p>
                  </div>
                </div>
                {getStatusBadge(report.status)}
              </div>

              <div className="mt-8 grid grid-cols-3 gap-6">
                <div className="bg-secondary-50/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-secondary-500 font-medium">テンプレート</p>
                  <p className="font-semibold text-secondary-900 mt-1">{report.template}</p>
                </div>
                <div className="bg-secondary-50/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-secondary-500 font-medium">形式</p>
                  <p className="font-semibold text-secondary-900 mt-1">{report.format}</p>
                </div>
                <div className="bg-secondary-50/50 rounded-xl px-4 py-3">
                  <p className="text-xs text-secondary-500 font-medium">文字数</p>
                  <p className="font-semibold text-secondary-900 mt-1">
                    {report.word_count > 0 ? report.word_count.toLocaleString() : '—'}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-secondary-100">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-secondary-500">
                    <span className="font-medium text-secondary-700">{report.created_by}</span>
                    <span className="mx-2">•</span>
                    <span>{formatDate(report.created_at)}</span>
                  </div>
                  {report.status === 'completed' && (
                    <div className="flex items-center gap-3">
                      <button className="inline-flex items-center gap-1.5 text-sm text-primary-600 hover:text-primary-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-colors">
                        <EyeIcon className="h-4 w-4" />
                        プレビュー
                      </button>
                      <button className="inline-flex items-center gap-1.5 text-sm text-primary-600 hover:text-primary-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-primary-50 transition-colors">
                        <ArrowDownTrayIcon className="h-4 w-4" />
                        ダウンロード
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {mockReports.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl ring-1 ring-secondary-200/60">
            <div className="mx-auto h-16 w-16 rounded-2xl bg-secondary-100 flex items-center justify-center">
              <DocumentTextIcon className="h-8 w-8 text-secondary-400" />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-secondary-900">レポートがありません</h3>
            <p className="mt-2 text-sm text-secondary-500">新規レポートを作成してください。</p>
            <div className="mt-8">
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-primary-500/25 hover:bg-primary-500 transition-all"
              >
                <PlusIcon className="h-5 w-5" />
                新規レポート作成
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
