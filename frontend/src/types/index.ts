// 共通型定義

export interface ApiError {
  error_code: string
  message: string
  details?: Record<string, unknown>
  timestamp?: string
  request_id?: string
}

export interface PaginationParams {
  skip?: number
  limit?: number
  page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: {
    total: number
    page: number
    limit: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}


