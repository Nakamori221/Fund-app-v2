import { RecentActivity } from '../services/dashboardService'
import {
  DocumentTextIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  PencilSquareIcon,
} from '@heroicons/react/24/outline'

interface RecentActivitiesProps {
  activities: RecentActivity[]
  loading?: boolean
}

export default function RecentActivities({
  activities,
  loading = false,
}: RecentActivitiesProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) {
      return `${diffMins}分前`
    } else if (diffHours < 24) {
      return `${diffHours}時間前`
    } else {
      return `${diffDays}日前`
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'case':
        return <DocumentTextIcon className="h-5 w-5 text-secondary-500" />
      case 'observation':
        return <ChartBarIcon className="h-5 w-5 text-primary-500" />
      case 'conflict':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning" />
      case 'approval':
        return <CheckCircleIcon className="h-5 w-5 text-success" />
      default:
        return <PencilSquareIcon className="h-5 w-5 text-secondary-400" />
    }
  }

  const getActivityBackground = (type: string) => {
    switch (type) {
        case 'case': return 'bg-secondary-50 ring-secondary-200'
        case 'observation': return 'bg-primary-50 ring-primary-200'
        case 'conflict': return 'bg-warning/10 ring-warning/20'
        case 'approval': return 'bg-success/10 ring-success/20'
        default: return 'bg-secondary-50 ring-secondary-200'
    }
  }

  if (loading) {
    return (
      <div className="flow-root rounded-lg bg-white p-6 shadow-sm ring-1 ring-secondary-900/5">
        <ul className="-mb-8">
            {[1, 2, 3].map((i) => (
                <li key={i}>
                    <div className="relative pb-8">
                        <div className="flex space-x-3">
                            <div className="h-8 w-8 rounded-full bg-secondary-200 animate-pulse" />
                            <div className="flex-1 space-y-2 py-1">
                                <div className="h-4 bg-secondary-200 rounded w-3/4 animate-pulse" />
                                <div className="h-3 bg-secondary-100 rounded w-1/2 animate-pulse" />
                            </div>
                        </div>
                    </div>
                </li>
            ))}
        </ul>
      </div>
    )
  }

  return (
    <div className="flow-root rounded-lg bg-white p-6 shadow-sm ring-1 ring-secondary-900/5">
      {activities.length === 0 ? (
        <div className="text-center py-6 text-secondary-500">
          活動履歴がありません
        </div>
      ) : (
        <ul role="list" className="-mb-8">
          {activities.map((activity, activityIdx) => (
            <li key={activity.id}>
              <div className="relative pb-8">
                {activityIdx !== activities.length - 1 ? (
                  <span
                    className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-secondary-200"
                    aria-hidden="true"
                  />
                ) : null}
                <div className="relative flex space-x-3">
                  <div>
                    <span
                      className={`h-8 w-8 rounded-full flex items-center justify-center ring-1 ${getActivityBackground(activity.type)}`}
                    >
                      {getActivityIcon(activity.type)}
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-secondary-500">
                        {activity.description}
                      </p>
                    </div>
                    <div className="whitespace-nowrap text-right text-xs text-secondary-400">
                      <time dateTime={activity.timestamp}>{formatTime(activity.timestamp)}</time>
                      <span className="block mt-0.5 font-medium text-secondary-600">{activity.user}</span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
