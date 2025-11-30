interface StatCardProps {
  title: string
  value: number
  loading?: boolean
  highlight?: boolean
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>
  trend?: {
    value: number
    type: 'increase' | 'decrease'
  }
}

export default function StatCard({
  title,
  value,
  loading = false,
  highlight = false,
  icon: Icon,
  trend
}: StatCardProps) {
  return (
    <div
      className={`
        relative overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-secondary-900/5 transition-all duration-200 hover:shadow-md
        ${highlight ? 'ring-2 ring-warning/50' : ''}
      `}
    >
      <dt>
        <div className="absolute rounded-md bg-primary-50 p-3">
          {Icon ? (
            <Icon className="h-6 w-6 text-primary-600" aria-hidden="true" />
          ) : (
            <div className="h-6 w-6" />
          )}
        </div>
        <p className="ml-16 truncate text-sm font-medium text-secondary-500">{title}</p>
      </dt>
      <dd className="ml-16 flex items-baseline pb-1 sm:pb-2">
        {loading ? (
            <div className="h-8 w-24 animate-pulse rounded bg-secondary-200" />
        ) : (
            <p className="text-2xl font-semibold text-secondary-900">{value.toLocaleString()}</p>
        )}
        
        {trend && !loading && (
            <p
                className={`
                    ml-2 flex items-baseline text-sm font-semibold
                    ${trend.type === 'increase' ? 'text-success' : 'text-danger'}
                `}
            >
                {trend.type === 'increase' ? '↑' : '↓'} {trend.value}%
            </p>
        )}
      </dd>
    </div>
  )
}
