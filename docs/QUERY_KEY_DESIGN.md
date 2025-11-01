# TanStack Query 設計ガイド

**Version**: 1.0.0
**Last Updated**: 2025-11-01

## 目次

1. [設計原則](#設計原則)
2. [Query Key 階層構造](#query-key-階層構造)
3. [Stale Time と Cache Time 設定](#stale-time-と-cache-time-設定)
4. [Invalidation 戦略](#invalidation-戦略)
5. [Optimistic Updates](#optimistic-updates)
6. [Infinite Queries](#infinite-queries)
7. [実装パターン](#実装パターン)
8. [パフォーマンス最適化](#パフォーマンス最適化)

---

## 1. 設計原則

### 1.1 Single Source of Truth
```typescript
// ❌ Bad: Zustand と Query Cache の重複
const useStore = create((set) => ({
  cases: [],        // ❌ Server state を Zustand に保存
  fetchCases: async () => {
    const cases = await api.getCases()
    set({ cases })  // ❌ 重複管理
  }
}))

// ✅ Good: Query Cache のみが Server State を管理
const useCases = () => {
  return useQuery({
    queryKey: ['cases'],
    queryFn: api.getCases,
  })
}

// UI State は Zustand で管理
const useUIStore = create((set) => ({
  selectedCaseId: null,
  filterText: '',
  modalOpen: false,
}))
```

### 1.2 階層的 Query Key 設計
```typescript
// Query Key は階層的に構成し、親子関係を明確にする
type QueryKey =
  | ['cases']                                       // Level 1: リソース
  | ['cases', string]                              // Level 2: 特定リソース
  | ['cases', string, 'observations']              // Level 3: サブリソース
  | ['cases', string, 'observations', FilterObj]   // Level 4: フィルター付き
```

### 1.3 不変性の保持
```typescript
// Query Key は必ず配列で、オブジェクトは最後の要素のみ
// ✅ Good
['cases', caseId, 'observations', { section: 'kpi', sourceTag: 'CONF' }]

// ❌ Bad
['cases', { caseId, type: 'observations' }]  // オブジェクトが途中にある
```

---

## 2. Query Key 階層構造

### 2.1 標準的な Query Key パターン

```typescript
// types/queryKeys.ts
export const queryKeys = {
  // Cases
  cases: {
    all: ['cases'] as const,
    lists: () => [...queryKeys.cases.all, 'list'] as const,
    list: (filters?: CaseFilters) =>
      [...queryKeys.cases.lists(), filters] as const,
    details: () => [...queryKeys.cases.all, 'detail'] as const,
    detail: (id: string) =>
      [...queryKeys.cases.details(), id] as const,

    // Case sub-resources
    observations: (caseId: string) =>
      [...queryKeys.cases.detail(caseId), 'observations'] as const,
    observationsFiltered: (caseId: string, filters: ObservationFilters) =>
      [...queryKeys.cases.observations(caseId), filters] as const,
    conflicts: (caseId: string) =>
      [...queryKeys.cases.detail(caseId), 'conflicts'] as const,
    reports: (caseId: string) =>
      [...queryKeys.cases.detail(caseId), 'reports'] as const,
  },

  // Observations (direct access)
  observations: {
    all: ['observations'] as const,
    lists: () => [...queryKeys.observations.all, 'list'] as const,
    list: (filters?: ObservationFilters) =>
      [...queryKeys.observations.lists(), filters] as const,
    detail: (id: string) =>
      [...queryKeys.observations.all, id] as const,
  },

  // Conflicts
  conflicts: {
    all: ['conflicts'] as const,
    byCaseId: (caseId: string) =>
      [...queryKeys.conflicts.all, caseId] as const,
    detail: (id: string) =>
      [...queryKeys.conflicts.all, id] as const,
  },

  // Reports
  reports: {
    all: ['reports'] as const,
    byCaseId: (caseId: string) =>
      [...queryKeys.reports.all, { caseId }] as const,
    detail: (id: string) =>
      [...queryKeys.reports.all, id] as const,
  },

  // User & Auth
  auth: {
    user: ['auth', 'user'] as const,
    permissions: ['auth', 'permissions'] as const,
  },
}
```

### 2.2 Query Key 使用例

```typescript
// hooks/useCase.ts
export const useCase = (caseId: string) => {
  return useQuery({
    queryKey: queryKeys.cases.detail(caseId),
    queryFn: () => api.getCase(caseId),
    staleTime: 5 * 60 * 1000, // 5分
  })
}

export const useCaseObservations = (
  caseId: string,
  filters?: ObservationFilters
) => {
  return useQuery({
    queryKey: filters
      ? queryKeys.cases.observationsFiltered(caseId, filters)
      : queryKeys.cases.observations(caseId),
    queryFn: () => api.getObservations({ caseId, ...filters }),
    staleTime: 2 * 60 * 1000, // 2分
  })
}
```

---

## 3. Stale Time と Cache Time 設定

### 3.1 データ種別ごとの設定値

```typescript
// config/queryConfig.ts
export const QUERY_CONFIG = {
  staleTime: {
    // 静的データ（ほとんど変更されない）
    userProfile: 30 * 60 * 1000,     // 30分
    permissions: 30 * 60 * 1000,     // 30分
    fieldDictionary: Infinity,        // 永続

    // 準静的データ（たまに変更される）
    cases: 5 * 60 * 1000,             // 5分
    caseDetail: 5 * 60 * 1000,        // 5分

    // 動的データ（頻繁に変更される）
    observations: 2 * 60 * 1000,      // 2分
    conflicts: 60 * 1000,             // 1分
    approvals: 30 * 1000,             // 30秒

    // 生成済みデータ（変更されない）
    reports: Infinity,                // 永続
    exportedPDF: Infinity,            // 永続
  },

  cacheTime: {
    default: 10 * 60 * 1000,          // 10分（デフォルト）
    extended: 30 * 60 * 1000,         // 30分（長期保持）
    temporary: 5 * 60 * 1000,         // 5分（一時的）
  },

  retry: {
    count: 3,
    delay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
  },
}
```

### 3.2 Context による設定のオーバーライド

```typescript
// providers/QueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: QUERY_CONFIG.staleTime.default,
      cacheTime: QUERY_CONFIG.cacheTime.default,
      retry: QUERY_CONFIG.retry.count,
      retryDelay: QUERY_CONFIG.retry.delay,
      refetchOnWindowFocus: false,
      refetchOnReconnect: 'always',
    },
    mutations: {
      retry: 1,
    },
  },
})

export function QueryProvider({ children }: PropsWithChildren) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

---

## 4. Invalidation 戦略

### 4.1 階層的 Invalidation

```typescript
// hooks/mutations/useCaseMutations.ts
export const useUpdateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.updateCase,
    onSuccess: (data, variables) => {
      // 1. 特定の案件詳細を更新
      queryClient.setQueryData(
        queryKeys.cases.detail(variables.caseId),
        data
      )

      // 2. 案件一覧を無効化（再フェッチ）
      queryClient.invalidateQueries({
        queryKey: queryKeys.cases.lists(),
      })

      // 3. 関連する子リソースは無効化しない（パフォーマンス最適化）
      // queryClient.invalidateQueries({
      //   queryKey: queryKeys.cases.observations(variables.caseId),
      // })
    },
  })
}

export const useCreateObservation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.createObservation,
    onSuccess: (data, variables) => {
      // 観測データのみ無効化（親の案件は無効化しない）
      queryClient.invalidateQueries({
        queryKey: queryKeys.cases.observations(variables.caseId),
      })

      // 矛盾検出も無効化（観測データが変わったため）
      queryClient.invalidateQueries({
        queryKey: queryKeys.cases.conflicts(variables.caseId),
      })
    },
  })
}
```

### 4.2 Smart Invalidation パターン

```typescript
// utils/smartInvalidation.ts
export class SmartInvalidator {
  constructor(private queryClient: QueryClient) {}

  // 関連するクエリを賢く無効化
  invalidateObservationRelated(caseId: string, field: string) {
    // 1. 直接影響を受けるクエリ
    this.queryClient.invalidateQueries({
      queryKey: queryKeys.cases.observations(caseId),
      exact: false, // サブクエリも含む
    })

    // 2. field に依存する計算値を無効化
    if (this.isKPIField(field)) {
      this.queryClient.invalidateQueries({
        queryKey: ['calculations', caseId],
      })
    }

    // 3. 矛盾検出を無効化（非同期）
    setTimeout(() => {
      this.queryClient.invalidateQueries({
        queryKey: queryKeys.cases.conflicts(caseId),
      })
    }, 1000)
  }

  private isKPIField(field: string): boolean {
    return ['revenue_mrr', 'revenue_arr', 'ltv_cac_ratio'].includes(field)
  }
}
```

### 4.3 Selective Invalidation

```typescript
// 特定の条件に基づく選択的な無効化
export const useConditionalInvalidation = () => {
  const queryClient = useQueryClient()

  const invalidateIfStale = (queryKey: QueryKey) => {
    const state = queryClient.getQueryState(queryKey)

    if (state && Date.now() - state.dataUpdatedAt > 60000) {
      // 1分以上古いデータのみ無効化
      queryClient.invalidateQueries({ queryKey })
    }
  }

  return { invalidateIfStale }
}
```

---

## 5. Optimistic Updates

### 5.1 基本的な Optimistic Update

```typescript
// hooks/mutations/useOptimisticUpdate.ts
export const useOptimisticObservationUpdate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.updateObservation,

    onMutate: async (newObservation) => {
      // 1. 実行中のクエリをキャンセル
      await queryClient.cancelQueries({
        queryKey: queryKeys.observations.detail(newObservation.id)
      })

      // 2. 現在のデータをスナップショット
      const previousObservation = queryClient.getQueryData(
        queryKeys.observations.detail(newObservation.id)
      )

      // 3. 楽観的更新
      queryClient.setQueryData(
        queryKeys.observations.detail(newObservation.id),
        (old: Observation) => ({
          ...old,
          ...newObservation,
          updatedAt: new Date().toISOString(),
        })
      )

      // 4. Context にスナップショットを保存
      return { previousObservation }
    },

    onError: (err, newObservation, context) => {
      // エラー時はロールバック
      if (context?.previousObservation) {
        queryClient.setQueryData(
          queryKeys.observations.detail(newObservation.id),
          context.previousObservation
        )
      }

      // エラー通知
      toast.error('更新に失敗しました')
    },

    onSettled: (data, error, variables) => {
      // 成功・失敗に関わらず最新データを取得
      queryClient.invalidateQueries({
        queryKey: queryKeys.observations.detail(variables.id)
      })
    },
  })
}
```

### 5.2 リスト更新の Optimistic Update

```typescript
export const useOptimisticListUpdate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.createObservation,

    onMutate: async (newObservation) => {
      const queryKey = queryKeys.cases.observations(newObservation.caseId)

      await queryClient.cancelQueries({ queryKey })

      const previousData = queryClient.getQueryData<Observation[]>(queryKey)

      // リストに楽観的に追加
      queryClient.setQueryData<Observation[]>(queryKey, (old = []) => [
        {
          ...newObservation,
          id: `temp-${Date.now()}`, // 一時ID
          createdAt: new Date().toISOString(),
          status: 'pending', // 保留状態を示す
        },
        ...old,
      ])

      return { previousData }
    },

    onSuccess: (data, variables, context) => {
      const queryKey = queryKeys.cases.observations(variables.caseId)

      // 一時データを実際のデータで置き換え
      queryClient.setQueryData<Observation[]>(queryKey, (old = []) =>
        old.map(item =>
          item.id.startsWith('temp-') ? data : item
        )
      )
    },

    onError: (err, variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(
          queryKeys.cases.observations(variables.caseId),
          context.previousData
        )
      }
    },
  })
}
```

---

## 6. Infinite Queries

### 6.1 無限スクロールの実装

```typescript
// hooks/useInfiniteObservations.ts
export const useInfiniteObservations = (caseId: string) => {
  return useInfiniteQuery({
    queryKey: queryKeys.cases.observations(caseId),
    queryFn: ({ pageParam = 1 }) =>
      api.getObservations({
        caseId,
        page: pageParam,
        limit: 50,
      }),
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.pagination.has_next) {
        return lastPage.pagination.page + 1
      }
      return undefined
    },
    staleTime: 2 * 60 * 1000,
  })
}

// components/ObservationInfiniteList.tsx
export function ObservationInfiniteList({ caseId }: Props) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useInfiniteObservations(caseId)

  const { ref, inView } = useInView()

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage()
    }
  }, [inView, hasNextPage, fetchNextPage])

  if (isLoading) return <Skeleton />
  if (isError) return <ErrorMessage />

  return (
    <div>
      {data.pages.map((page, i) => (
        <React.Fragment key={i}>
          {page.items.map((observation) => (
            <ObservationCard
              key={observation.id}
              observation={observation}
            />
          ))}
        </React.Fragment>
      ))}

      <div ref={ref}>
        {isFetchingNextPage && <LoadingSpinner />}
      </div>
    </div>
  )
}
```

### 6.2 Infinite Query の Invalidation

```typescript
export const useInvalidateInfiniteQuery = () => {
  const queryClient = useQueryClient()

  const invalidateAndReset = (queryKey: QueryKey) => {
    // 1. 現在のデータをクリア
    queryClient.setQueryData(queryKey, (oldData: any) => ({
      pages: oldData?.pages.slice(0, 1) || [],
      pageParams: oldData?.pageParams.slice(0, 1) || [],
    }))

    // 2. 再フェッチ
    queryClient.invalidateQueries({ queryKey })
  }

  return { invalidateAndReset }
}
```

---

## 7. 実装パターン

### 7.1 Custom Hook パターン

```typescript
// hooks/cases/useCaseDetail.ts
interface UseCaseDetailOptions {
  includeObservations?: boolean
  includeConflicts?: boolean
  includeReports?: boolean
}

export const useCaseDetail = (
  caseId: string,
  options: UseCaseDetailOptions = {}
) => {
  const caseQuery = useQuery({
    queryKey: queryKeys.cases.detail(caseId),
    queryFn: () => api.getCase(caseId),
    staleTime: QUERY_CONFIG.staleTime.caseDetail,
  })

  const observationsQuery = useQuery({
    queryKey: queryKeys.cases.observations(caseId),
    queryFn: () => api.getObservations({ caseId }),
    enabled: options.includeObservations && !!caseQuery.data,
    staleTime: QUERY_CONFIG.staleTime.observations,
  })

  const conflictsQuery = useQuery({
    queryKey: queryKeys.cases.conflicts(caseId),
    queryFn: () => api.getConflicts({ caseId }),
    enabled: options.includeConflicts && !!caseQuery.data,
    staleTime: QUERY_CONFIG.staleTime.conflicts,
  })

  return {
    case: caseQuery.data,
    observations: observationsQuery.data,
    conflicts: conflictsQuery.data,
    isLoading: caseQuery.isLoading,
    isError: caseQuery.isError,
    refetch: () => {
      caseQuery.refetch()
      if (options.includeObservations) observationsQuery.refetch()
      if (options.includeConflicts) conflictsQuery.refetch()
    },
  }
}
```

### 7.2 Prefetching パターン

```typescript
// hooks/usePrefetch.ts
export const useCasePrefetch = () => {
  const queryClient = useQueryClient()

  const prefetchCase = async (caseId: string) => {
    // メインデータをプリフェッチ
    await queryClient.prefetchQuery({
      queryKey: queryKeys.cases.detail(caseId),
      queryFn: () => api.getCase(caseId),
      staleTime: QUERY_CONFIG.staleTime.caseDetail,
    })

    // 関連データも並行してプリフェッチ
    await Promise.all([
      queryClient.prefetchQuery({
        queryKey: queryKeys.cases.observations(caseId),
        queryFn: () => api.getObservations({ caseId }),
        staleTime: QUERY_CONFIG.staleTime.observations,
      }),
      queryClient.prefetchQuery({
        queryKey: queryKeys.cases.conflicts(caseId),
        queryFn: () => api.getConflicts({ caseId }),
        staleTime: QUERY_CONFIG.staleTime.conflicts,
      }),
    ])
  }

  return { prefetchCase }
}

// 使用例: ホバー時にプリフェッチ
export function CaseListItem({ case }: Props) {
  const { prefetchCase } = useCasePrefetch()

  return (
    <Link
      to={`/cases/${case.id}`}
      onMouseEnter={() => prefetchCase(case.id)}
    >
      {case.company_name}
    </Link>
  )
}
```

### 7.3 Suspense モード

```typescript
// providers/QueryProvider.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: true, // Suspense を有効化
      useErrorBoundary: true, // Error Boundary を使用
    },
  },
})

// components/CaseDetailSuspense.tsx
export function CaseDetailSuspense({ caseId }: Props) {
  const { data } = useQuery({
    queryKey: queryKeys.cases.detail(caseId),
    queryFn: () => api.getCase(caseId),
    // suspense: true がデフォルトで有効
  })

  // data は必ず存在する（Suspense が解決済み）
  return <CaseDetail case={data} />
}

// pages/CasePage.tsx
export function CasePage() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <Suspense fallback={<LoadingSpinner />}>
        <CaseDetailSuspense caseId={caseId} />
      </Suspense>
    </ErrorBoundary>
  )
}
```

---

## 8. パフォーマンス最適化

### 8.1 Query の並列実行

```typescript
// hooks/useParallelQueries.ts
export const useCaseWithAllData = (caseId: string) => {
  // 並列で全てのデータを取得
  const results = useQueries({
    queries: [
      {
        queryKey: queryKeys.cases.detail(caseId),
        queryFn: () => api.getCase(caseId),
        staleTime: QUERY_CONFIG.staleTime.caseDetail,
      },
      {
        queryKey: queryKeys.cases.observations(caseId),
        queryFn: () => api.getObservations({ caseId }),
        staleTime: QUERY_CONFIG.staleTime.observations,
      },
      {
        queryKey: queryKeys.cases.conflicts(caseId),
        queryFn: () => api.getConflicts({ caseId }),
        staleTime: QUERY_CONFIG.staleTime.conflicts,
      },
      {
        queryKey: queryKeys.cases.reports(caseId),
        queryFn: () => api.getReports({ caseId }),
        staleTime: QUERY_CONFIG.staleTime.reports,
      },
    ],
  })

  return {
    case: results[0].data,
    observations: results[1].data,
    conflicts: results[2].data,
    reports: results[3].data,
    isLoading: results.some(result => result.isLoading),
    isError: results.some(result => result.isError),
  }
}
```

### 8.2 選択的な Query 実行

```typescript
// hooks/useConditionalQuery.ts
export const useSmartObservations = (
  caseId: string,
  options?: {
    autoFetch?: boolean
    filters?: ObservationFilters
  }
) => {
  const [shouldFetch, setShouldFetch] = useState(options?.autoFetch ?? true)

  const query = useQuery({
    queryKey: options?.filters
      ? queryKeys.cases.observationsFiltered(caseId, options.filters)
      : queryKeys.cases.observations(caseId),
    queryFn: () => api.getObservations({ caseId, ...options?.filters }),
    enabled: shouldFetch && !!caseId,
    staleTime: QUERY_CONFIG.staleTime.observations,
    keepPreviousData: true, // フィルター変更時に前のデータを保持
  })

  return {
    ...query,
    fetch: () => setShouldFetch(true),
  }
}
```

### 8.3 メモリ管理

```typescript
// utils/queryMemoryManagement.ts
export const setupQueryGarbageCollection = (queryClient: QueryClient) => {
  // 10分ごとに古いクエリをクリーンアップ
  setInterval(() => {
    const now = Date.now()
    const queries = queryClient.getQueryCache().getAll()

    queries.forEach(query => {
      const state = query.state
      if (
        state.dataUpdatedAt < now - 30 * 60 * 1000 && // 30分以上前
        state.fetchStatus === 'idle' &&
        query.getObserversCount() === 0 // 使用されていない
      ) {
        queryClient.removeQueries({ queryKey: query.queryKey, exact: true })
      }
    })
  }, 10 * 60 * 1000)
}
```

### 8.4 バンドル最適化

```typescript
// プロダクションビルドでは React Query Devtools を除外
const QueryDevtools = lazy(() =>
  import('@tanstack/react-query-devtools').then(module => ({
    default: module.ReactQueryDevtools,
  }))
)

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* アプリケーション */}

      {process.env.NODE_ENV === 'development' && (
        <Suspense fallback={null}>
          <QueryDevtools initialIsOpen={false} />
        </Suspense>
      )}
    </QueryClientProvider>
  )
}
```

---

## まとめ

### Do's ✅
1. **Server State は TanStack Query で管理**
2. **UI State は Zustand で管理**
3. **階層的な Query Key 設計を厳守**
4. **適切な staleTime と cacheTime を設定**
5. **選択的な Invalidation でパフォーマンス最適化**
6. **Optimistic Update で UX 向上**

### Don'ts ❌
1. **Server State を Zustand に複製しない**
2. **Query Key にランダムな値を含めない**
3. **過度に短い staleTime を設定しない**
4. **全体を invalidate せず、必要な部分のみ更新**
5. **enabled を使わずに無駄な fetch を避ける**

この設計ガイドに従うことで、効率的でメンテナブルなデータフェッチング層を構築できます。