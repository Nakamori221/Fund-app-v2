import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  fetchDashboardStats,
  fetchRecentActivities,
  fetchCases,
} from '../services/dashboardService'
import StatCard from '../components/StatCard'
import RecentActivities from '../components/RecentActivities'
import CasesTable from '../components/CasesTable'
import Layout from '../components/Layout/Layout'
import {
  BriefcaseIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  FolderIcon
} from '@heroicons/react/24/outline'

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
  })

  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['recent-activities'],
    queryFn: fetchRecentActivities,
  })

  const { data: cases, isLoading: casesLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: fetchCases,
  })

  return (
    <Layout>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="sm:flex sm:items-center sm:justify-between">
            <div>
                <h1 className="text-2xl font-bold leading-7 text-secondary-900 sm:truncate sm:text-3xl sm:tracking-tight">
                    ダッシュボード
                </h1>
                <p className="mt-2 text-sm text-secondary-500">
                    現在のファンド活動状況と重要指標の概要
                </p>
            </div>
            <div className="mt-4 flex gap-3 sm:ml-4 sm:mt-0">
                <Link
                    to="/reports"
                    className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-secondary-900 shadow-sm ring-1 ring-inset ring-secondary-300 hover:bg-secondary-50"
                >
                    レポート作成
                </Link>
                <Link
                    to="/cases/new"
                    className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                >
                    新規案件
                </Link>
            </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="総案件数"
            value={stats?.totalCases ?? 0}
            loading={statsLoading}
            icon={FolderIcon}
            trend={{ value: 12, type: 'increase' }}
          />
          <StatCard
            title="進行中案件"
            value={stats?.activeCases ?? 0}
            loading={statsLoading}
            icon={BriefcaseIcon}
            trend={{ value: 5, type: 'increase' }}
          />
          <StatCard
            title="観察記録数"
            value={stats?.totalObservations ?? 0}
            loading={statsLoading}
            icon={ChartBarIcon}
            trend={{ value: 24, type: 'increase' }}
          />
          <StatCard
            title="検出された矛盾"
            value={stats?.totalConflicts ?? 0}
            loading={statsLoading}
            highlight={stats && stats.totalConflicts > 0}
            icon={ExclamationTriangleIcon}
            trend={{ value: 2, type: 'decrease' }}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Left Column (Cases Table) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium leading-6 text-secondary-900">
                    最近の案件
                </h2>
                <Link to="/cases" className="text-sm font-semibold text-primary-600 hover:text-primary-500">
                    すべて見る
                </Link>
            </div>
            <CasesTable cases={cases ?? []} loading={casesLoading} />
          </div>

          {/* Right Column (Recent Activities) */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium leading-6 text-secondary-900">
                    最近の活動
                </h2>
            </div>
            <RecentActivities
              activities={activities ?? []}
              loading={activitiesLoading}
            />
            
            {/* Quick Actions Card */}
            <div className="overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-secondary-900/5">
                <div className="p-6">
                    <h3 className="text-base font-semibold leading-6 text-secondary-900">
                        クイックアクション
                    </h3>
                    <div className="mt-4 flex flex-col gap-3">
                        <Link 
                            to="/observations"
                            className="flex items-center justify-between rounded-md bg-secondary-50 px-4 py-3 text-sm font-medium text-secondary-700 hover:bg-secondary-100 transition-colors"
                        >
                            <span>観察記録を追加</span>
                            <span className="text-secondary-400">→</span>
                        </Link>
                        <Link 
                            to="/cases"
                            className="flex items-center justify-between rounded-md bg-secondary-50 px-4 py-3 text-sm font-medium text-secondary-700 hover:bg-secondary-100 transition-colors"
                        >
                            <span>矛盾チェック実行</span>
                            <span className="text-secondary-400">→</span>
                        </Link>
                    </div>
                </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
