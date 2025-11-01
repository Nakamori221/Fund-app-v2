# Fund IC Automation System - 統合アーキテクチャ設計書

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: Phase 1 実装開始準備完了

## 📋 目次

1. [システム全体構成](#システム全体構成)
2. [データフロー設計](#データフロー設計)
3. [API エンドポイント仕様](#api-エンドポイント仕様)
4. [データモデル設計](#データモデル設計)
5. [状態管理アーキテクチャ](#状態管理アーキテクチャ)
6. [セキュリティ設計](#セキュリティ設計)
7. [リアルタイム通信設計](#リアルタイム通信設計)
8. [エラーハンドリング戦略](#エラーハンドリング戦略)
9. [パフォーマンス最適化](#パフォーマンス最適化)
10. [デプロイメント戦略](#デプロイメント戦略)

---

## 1. システム全体構成

### 1.1 技術スタック

```mermaid
graph TB
    subgraph "Frontend"
        React[React 18.2]
        Vite[Vite 5.0]
        TQ[TanStack Query v5]
        Zustand[Zustand 4.4]
        Socket[Socket.io-client]
    end

    subgraph "Backend"
        FastAPI[FastAPI 0.104]
        SQLAlchemy[SQLAlchemy 2.0]
        Pydantic[Pydantic v2]
        JWT[PyJWT]
        OpenAI[OpenAI API]
    end

    subgraph "Infrastructure"
        PostgreSQL[PostgreSQL 15]
        Redis[Redis 7.0]
        S3[AWS S3 / LocalStorage]
        Docker[Docker Compose]
    end

    Frontend --> Backend
    Backend --> Infrastructure
```

### 1.2 レイヤー分離原則

| レイヤー | 責務 | 技術 |
|---------|-----|------|
| **Presentation** | UI レンダリング、ユーザー操作 | React Components |
| **State Management** | クライアント状態管理 | TanStack Query (Server State) + Zustand (UI State) |
| **API Gateway** | HTTP/WebSocket 通信 | FastAPI Router |
| **Business Logic** | ビジネスルール実装 | Service Classes |
| **Data Access** | データ永続化 | SQLAlchemy ORM |
| **External Services** | 外部 API 連携 | OpenAI, Playwright |

---

## 2. データフロー設計

### 2.1 案件作成から報告書生成までのフロー

```mermaid
sequenceDiagram
    participant U as User (FE)
    participant API as FastAPI
    participant DB as PostgreSQL
    participant AI as OpenAI
    participant WS as WebSocket

    U->>API: POST /cases (新規案件)
    API->>DB: INSERT case
    API-->>U: 201 Created {case_id}

    U->>API: POST /cases/{id}/collect-pub
    API->>AI: Extract from website
    API->>DB: INSERT observations (PUB)
    API-->>WS: Notify: "PUB collected"
    WS-->>U: Real-time update

    U->>API: POST /observations (INT/CONF)
    API->>DB: INSERT observation
    API-->>U: 201 Created

    U->>API: POST /cases/{id}/detect-conflicts
    API->>DB: SELECT observations
    API->>API: Run ConflictDetector
    API->>DB: INSERT conflicts
    API-->>U: 200 {conflicts}

    U->>API: POST /conflicts/{id}/resolve
    API->>DB: UPDATE observation.selected
    API-->>U: 200 {resolution}

    U->>API: POST /cases/{id}/generate-report
    API->>DB: SELECT all data
    API->>AI: Generate report text
    API->>DB: INSERT report
    API-->>U: 200 {report_id}
```

### 2.2 データ種別と処理優先度

| データ種別 | Source Tag | 処理 | 優先度 | Disclosure Level |
|-----------|------------|------|--------|-----------------|
| 公開情報 | PUB | Web スクレイピング + AI 抽出 | 3 | LP |
| 外部資料 | EXT | 手動入力 / ファイルインポート | 2 | LP |
| 内部分析 | ANL | アナリスト入力 | 4 | IC |
| 機密情報 | CONF | 限定メンバーのみ入力 | 5 | IC |
| インタビュー | INT | 議事録から抽出 | 1 | LP_NDA |

---

## 3. API エンドポイント仕様

### 3.1 Phase 1 エンドポイント (Week 1-8)

#### 認証 API

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/auth/register` | ユーザー登録 | `{email, password, role}` | `{user_id, email}` |
| POST | `/api/v1/auth/login` | ログイン | `{email, password}` | `{access_token, refresh_token}` |
| POST | `/api/v1/auth/refresh` | トークン更新 | `{refresh_token}` | `{access_token}` |
| GET | `/api/v1/auth/me` | 現在のユーザー情報 | - | `{user_id, email, role}` |

#### 案件管理 API

| Method | Path | Description | Query Params | Request Body | Response |
|--------|------|-------------|--------------|--------------|----------|
| GET | `/api/v1/cases` | 案件一覧 | `?status=&stage=&page=&limit=` | - | `{items[], total, page}` |
| POST | `/api/v1/cases` | 案件作成 | - | `{company_name, stage, website_url}` | `{case_id, ...}` |
| GET | `/api/v1/cases/{id}` | 案件詳細 | - | - | `{case details}` |
| PUT | `/api/v1/cases/{id}` | 案件更新 | - | `{updates}` | `{updated case}` |
| DELETE | `/api/v1/cases/{id}` | 案件削除 | - | - | `204 No Content` |

#### 観測データ API

```python
# Pydantic Schema
class ObservationCreate(BaseModel):
    case_id: UUID
    section: str
    field: str
    value_type: Literal["number", "string", "date", "boolean", "json"]
    value_number: Optional[float] = None
    value_string: Optional[str] = None
    value_date: Optional[datetime] = None
    value_boolean: Optional[bool] = None
    value_json: Optional[Dict] = None
    unit: Optional[str] = None
    source_tag: Literal["PUB", "EXT", "INT", "CONF", "ANL"]
    evidence: Optional[str] = None
    as_of: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    disclosure_level: Literal["IC", "LP", "LP_NDA", "PRIVATE"]

    @validator('value_number', 'value_string', 'value_date', 'value_boolean', 'value_json')
    def only_one_value_type(cls, v, values):
        """Ensure only one value_* field is populated"""
        # Implementation
```

| Method | Path | Description | Query Params | Request Body |
|--------|------|-------------|--------------|--------------|
| GET | `/api/v1/observations` | 観測一覧 | `?case_id=&source_tag=&section=` | - |
| POST | `/api/v1/observations` | 観測作成 | - | `ObservationCreate` |
| GET | `/api/v1/observations/{id}` | 観測詳細 | - | - |
| PUT | `/api/v1/observations/{id}` | 観測更新 | - | `ObservationUpdate` |
| DELETE | `/api/v1/observations/{id}` | 観測削除 | - | - |
| POST | `/api/v1/observations/bulk` | 一括作成 | - | `ObservationCreate[]` |

### 3.2 Phase 2 エンドポイント (Week 9-14)

#### 矛盾検出・解決 API

```python
class ConflictDetectionRequest(BaseModel):
    case_id: UUID
    sections: Optional[List[str]] = None
    strategy: Literal["numeric", "string", "date", "all"] = "all"

class ConflictResponse(BaseModel):
    conflict_id: UUID
    field: str
    observation_ids: List[UUID]
    deviation_pct: float
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    suggested_resolution: Dict
    metadata: Dict
```

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/cases/{id}/detect-conflicts` | 矛盾検出実行 | `ConflictDetectionRequest` | `ConflictResponse[]` |
| GET | `/api/v1/conflicts` | 矛盾一覧 | - | `{items[], total}` |
| POST | `/api/v1/conflicts/{id}/resolve` | 矛盾解決 | `{resolution, reason, selected_id}` | `{updated observations}` |

#### レポート生成 API

```python
class ReportGenerationRequest(BaseModel):
    case_id: UUID
    template_id: Literal["ic_default", "lp_default"]
    include_sections: Optional[List[str]] = None
    exclude_sections: Optional[List[str]] = None
    disclosure_level: Literal["IC", "LP"]

class ReportResponse(BaseModel):
    report_id: UUID
    case_id: UUID
    template_id: str
    status: Literal["generating", "completed", "failed"]
    markdown_content: Optional[str] = None
    pdf_url: Optional[str] = None
    generated_at: datetime
```

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/cases/{id}/generate-report` | レポート生成 |
| GET | `/api/v1/reports/{id}` | レポート取得 |
| GET | `/api/v1/reports/{id}/download` | PDF ダウンロード |

### 3.3 エラーレスポンス統一形式

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime
    request_id: str

    class Config:
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid field value",
                "details": {"field": "confidence", "reason": "must be between 0 and 1"},
                "timestamp": "2025-11-01T10:30:00Z",
                "request_id": "req_abc123"
            }
        }
```

| Status Code | Error Code | Description | Action |
|------------|------------|-------------|--------|
| 400 | `VALIDATION_ERROR` | 入力値バリデーション失敗 | 修正して再送 |
| 401 | `AUTHENTICATION_ERROR` | 認証失敗 | ログイン必要 |
| 403 | `AUTHORIZATION_ERROR` | 権限不足 | 権限昇格必要 |
| 404 | `NOT_FOUND` | リソース不存在 | ID 確認 |
| 409 | `CONFLICT_ERROR` | データ競合 | 最新データ取得後リトライ |
| 429 | `RATE_LIMIT_ERROR` | レート制限超過 | 時間をおいてリトライ |
| 500 | `INTERNAL_ERROR` | サーバーエラー | 自動リトライ |
| 503 | `SERVICE_UNAVAILABLE` | 外部サービス不可 | 時間をおいてリトライ |

---

## 4. データモデル設計

### 4.1 ER 図

```mermaid
erDiagram
    Users ||--o{ Cases : creates
    Users ||--o{ Observations : creates
    Users ||--o{ AuditLogs : generates
    Cases ||--o{ Observations : contains
    Cases ||--o{ Documents : has
    Cases ||--o{ Reports : generates
    Observations ||--o{ Conflicts : involves
    Roles ||--o{ Users : assigns

    Users {
        uuid id PK
        string email UK
        string password_hash
        uuid role_id FK
        boolean is_active
        datetime created_at
        datetime last_login
    }

    Cases {
        uuid id PK
        string company_name
        string stage
        string status
        string website_url
        uuid lead_partner_id FK
        uuid analyst_id FK
        datetime ic_date
        datetime created_at
        datetime updated_at
    }

    Observations {
        uuid id PK
        uuid case_id FK
        string section
        string field
        string value_type
        float value_number
        string value_string
        datetime value_date
        boolean value_boolean
        json value_json
        string unit
        string source_tag
        string evidence
        datetime as_of
        float confidence
        string disclosure_level
        uuid created_by FK
        datetime created_at
    }
```

### 4.2 インデックス戦略

```sql
-- Performance critical indexes
CREATE INDEX idx_cases_status_created ON cases(status, created_at DESC);
CREATE INDEX idx_observations_case_source ON observations(case_id, source_tag);
CREATE INDEX idx_observations_field_lookup ON observations(case_id, section, field);
CREATE INDEX idx_audit_user_timestamp ON audit_logs(user_id, timestamp DESC);

-- JSON field indexes (PostgreSQL GIN)
CREATE INDEX idx_observations_json ON observations USING GIN (value_json);

-- Full-text search (future)
CREATE INDEX idx_observations_evidence ON observations USING GIN (to_tsvector('english', evidence));
```

---

## 5. 状態管理アーキテクチャ

### 5.1 Server State vs UI State 分離原則

```typescript
// ❌ アンチパターン: Zustand に Server State を保存
const useStore = create((set) => ({
  cases: [],        // ❌ Server state
  observations: [], // ❌ Server state
  modalOpen: false, // ✅ UI state
}))

// ✅ 正しいパターン: 明確な分離
// Server State: TanStack Query
const { data: cases } = useQuery({
  queryKey: ['cases'],
  queryFn: fetchCases,
})

// UI State: Zustand
const useUIStore = create((set) => ({
  modalOpen: false,
  selectedRows: [],
  filterText: '',
  rightPaneWidth: 400,
}))
```

### 5.2 TanStack Query Key 階層設計

```typescript
// Query Key 命名規則
type QueryKey =
  | ['cases']                                    // 全案件
  | ['cases', caseId]                           // 特定案件
  | ['cases', caseId, 'observations']           // 案件の観測データ
  | ['cases', caseId, 'observations', filters]  // フィルター付き
  | ['observations']                            // 全観測データ
  | ['observations', observationId]             // 特定観測
  | ['conflicts', caseId]                       // 案件の矛盾
  | ['reports', reportId]                       // レポート

// Invalidation 戦略
const handleObservationUpdate = async () => {
  await updateObservation(data)
  // 特定の階層のみ無効化
  queryClient.invalidateQueries({
    queryKey: ['cases', caseId, 'observations']
  })
  // 親は invalidate しない（パフォーマンス最適化）
}

// Stale Time 設定
const queryOptions = {
  staleTime: {
    cases: 5 * 60 * 1000,        // 5分
    observations: 2 * 60 * 1000,  // 2分
    conflicts: 60 * 1000,         // 1分（頻繁に変更）
    reports: Infinity,            // 変更されない
  },
  cacheTime: 10 * 60 * 1000,     // 10分
}
```

### 5.3 Optimistic Updates 実装パターン

```typescript
const useUpdateObservation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateObservation,
    onMutate: async (newData) => {
      // 1. Cancel in-flight queries
      await queryClient.cancelQueries(['observations', newData.id])

      // 2. Snapshot previous value
      const previousData = queryClient.getQueryData(['observations', newData.id])

      // 3. Optimistically update
      queryClient.setQueryData(['observations', newData.id], newData)

      return { previousData }
    },
    onError: (err, newData, context) => {
      // Rollback on error
      queryClient.setQueryData(
        ['observations', newData.id],
        context.previousData
      )
    },
    onSettled: () => {
      // Always refetch after mutation
      queryClient.invalidateQueries(['observations'])
    }
  })
}
```

---

## 6. セキュリティ設計

### 6.1 認証フロー (JWT)

```python
# Backend: JWT Token Generation
from datetime import datetime, timedelta
from jose import JWTError, jwt

class AuthService:
    def create_access_token(self, user_id: UUID, role: str) -> str:
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=60),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

### 6.2 RBAC (Role-Based Access Control)

```python
# Permission Matrix
PERMISSIONS = {
    "analyst": {
        "create": ["case", "observation"],
        "read": ["case:own", "observation:own"],
        "update": ["case:own", "observation:own"],
        "delete": ["observation:own"],
    },
    "lead_partner": {
        "create": ["case", "observation", "report"],
        "read": ["case:all", "observation:all", "report:all"],
        "update": ["case:all", "observation:all"],
        "delete": ["case:all", "observation:all"],
        "approve": ["observation:all"],
    },
    "ic_member": {
        "create": ["*"],
        "read": ["*"],
        "update": ["*"],
        "delete": ["*"],
        "approve": ["*"],
        "export": ["ic_report", "lp_report"],
    },
    "admin": ["*"]  # All permissions
}

# FastAPI Dependency
def require_permission(resource: str, action: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ):
        user_permissions = PERMISSIONS.get(current_user.role, {})

        if action not in user_permissions:
            raise HTTPException(status_code=403, detail="Permission denied")

        allowed_resources = user_permissions[action]
        if "*" in allowed_resources or resource in allowed_resources:
            return current_user

        # Check ownership-based permissions
        if f"{resource}:own" in allowed_resources:
            # Additional ownership check logic
            pass

        raise HTTPException(status_code=403, detail="Permission denied")

    return permission_checker

# Usage in endpoints
@router.post("/observations")
async def create_observation(
    data: ObservationCreate,
    user: User = Depends(require_permission("observation", "create"))
):
    # Implementation
```

### 6.3 データマスキング戦略

```python
class MaskingService:
    """Disclosure level に基づくデータマスキング"""

    MASKING_RULES = {
        "numeric_usd": {
            "IC": lambda v: f"${v:,.2f}",              # $12,345,678.90
            "LP": lambda v: f"${round(v, -5):,.0f}",   # $12,300,000
            "LP_NDA": lambda v: f"${round(v/1e6)}M",   # $12M
            "PRIVATE": lambda v: "***"
        },
        "percent": {
            "IC": lambda v: f"{v:.2%}",                # 12.34%
            "LP": lambda v: f"{round(v, 2):.1%}",      # 12.3%
            "LP_NDA": lambda v: f"{round(v, 1):.0%}",  # 12%
            "PRIVATE": lambda v: "***"
        },
        "string": {
            "IC": lambda v: v,                         # Full text
            "LP": lambda v: self.partial_mask(v),      # Tana** T***
            "LP_NDA": lambda v: "****",
            "PRIVATE": lambda v: None
        }
    }

    def mask_value(self, value: Any, field_type: str,
                   disclosure_level: str, user_role: str) -> Any:
        # Apply masking based on combination of factors
        if user_role == "admin":
            return value  # No masking for admin

        masking_func = self.MASKING_RULES.get(field_type, {}).get(disclosure_level)
        if masking_func:
            return masking_func(value)
        return value

    def partial_mask(self, text: str, keep_ratio: float = 0.3) -> str:
        """Partial masking for names/strings"""
        if len(text) <= 3:
            return "***"
        keep_chars = max(1, int(len(text) * keep_ratio))
        return text[:keep_chars] + "*" * (len(text) - keep_chars)
```

---

## 7. リアルタイム通信設計

### 7.1 WebSocket Architecture (Phase 2)

```python
# Backend: FastAPI WebSocket Handler
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    async def broadcast_to_role(self, message: dict, role: str):
        # Get users with specific role
        users = await get_users_by_role(role)
        for user in users:
            await self.send_personal_message(message, str(user.id))

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Heartbeat or receive messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
```

### 7.2 Frontend WebSocket Integration

```typescript
// Frontend: Socket.io Client with Zustand
import { io, Socket } from 'socket.io-client'
import { create } from 'zustand'

interface WebSocketStore {
  socket: Socket | null
  connected: boolean
  notifications: Notification[]
  connect: (token: string) => void
  disconnect: () => void
  addNotification: (notification: Notification) => void
}

const useWebSocketStore = create<WebSocketStore>((set, get) => ({
  socket: null,
  connected: false,
  notifications: [],

  connect: (token: string) => {
    const socket = io(import.meta.env.VITE_WS_URL, {
      auth: { token },
      transports: ['websocket'],
    })

    socket.on('connect', () => {
      set({ connected: true, socket })
    })

    socket.on('notification', (data) => {
      get().addNotification(data)

      // Trigger query invalidation based on notification type
      if (data.type === 'observation_updated') {
        queryClient.invalidateQueries(['observations', data.observationId])
      }
    })

    socket.on('disconnect', () => {
      set({ connected: false })
    })
  },

  disconnect: () => {
    get().socket?.disconnect()
    set({ socket: null, connected: false })
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [...state.notifications, notification]
    }))
  }
}))
```

---

## 8. エラーハンドリング戦略

### 8.1 Backend Error Hierarchy

```python
# Custom Exception Classes
class APIException(Exception):
    """Base API Exception"""
    status_code = 500
    error_code = "INTERNAL_ERROR"
    message = "An error occurred"

class ValidationException(APIException):
    status_code = 400
    error_code = "VALIDATION_ERROR"

class AuthenticationException(APIException):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"

class AuthorizationException(APIException):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"

class NotFoundException(APIException):
    status_code = 404
    error_code = "NOT_FOUND"

class ConflictException(APIException):
    status_code = 409
    error_code = "CONFLICT_ERROR"

class RateLimitException(APIException):
    status_code = 429
    error_code = "RATE_LIMIT_ERROR"

# Global Exception Handler
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": getattr(exc, "details", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.headers.get("X-Request-ID", str(uuid4()))
        }
    )
```

### 8.2 Frontend Error Handling

```typescript
// API Client with Retry Logic
class APIClient {
  private async request<T>(
    url: string,
    options: RequestInit,
    retries = 3
  ): Promise<T> {
    let lastError: Error | null = null

    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getToken()}`,
            ...options.headers,
          },
        })

        if (!response.ok) {
          const error = await response.json()

          // Retry on specific errors
          if (error.error_code === 'RATE_LIMIT_ERROR' && i < retries - 1) {
            await this.delay(Math.pow(2, i) * 1000) // Exponential backoff
            continue
          }

          throw new APIError(error)
        }

        return await response.json()
      } catch (error) {
        lastError = error as Error

        // Network errors - retry
        if (error instanceof TypeError && i < retries - 1) {
          await this.delay(Math.pow(2, i) * 1000)
          continue
        }

        throw error
      }
    }

    throw lastError
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// React Error Boundary
class ErrorBoundary extends React.Component<Props, State> {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to Sentry
    Sentry.captureException(error, { contexts: { react: errorInfo } })

    // Display user-friendly error
    this.setState({
      hasError: true,
      errorMessage: this.getErrorMessage(error)
    })
  }

  getErrorMessage(error: Error): string {
    if (error instanceof APIError) {
      switch (error.code) {
        case 'AUTHENTICATION_ERROR':
          return 'ログインが必要です'
        case 'AUTHORIZATION_ERROR':
          return '権限がありません'
        case 'RATE_LIMIT_ERROR':
          return 'リクエストが多すぎます。しばらくお待ちください'
        default:
          return 'エラーが発生しました'
      }
    }
    return 'システムエラーが発生しました'
  }
}
```

---

## 9. パフォーマンス最適化

### 9.1 Backend 最適化

```python
# Database Query Optimization
from sqlalchemy.orm import selectinload, joinedload

class CaseService:
    async def get_case_with_observations(self, case_id: UUID) -> Case:
        # N+1 problem prevention
        query = (
            select(Case)
            .options(
                selectinload(Case.observations),  # Eager load
                joinedload(Case.lead_partner),     # Join load
                joinedload(Case.analyst)
            )
            .where(Case.id == case_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_cases_paginated(
        self,
        page: int = 1,
        limit: int = 50,
        filters: CaseFilters = None
    ) -> PaginatedResponse:
        # Efficient pagination with total count
        count_query = select(func.count()).select_from(Case)
        data_query = select(Case).limit(limit).offset((page - 1) * limit)

        if filters:
            count_query = count_query.where(self._build_filters(filters))
            data_query = data_query.where(self._build_filters(filters))

        # Execute both queries in parallel
        total_task = self.db.scalar(count_query)
        data_task = self.db.execute(data_query)

        total, result = await asyncio.gather(total_task, data_task)

        return PaginatedResponse(
            items=result.scalars().all(),
            total=total,
            page=page,
            pages=math.ceil(total / limit)
        )
```

### 9.2 Frontend 最適化

```typescript
// Virtual Scrolling for Large Lists
import { useVirtualizer } from '@tanstack/react-virtual'

function ObservationTable({ caseId }: Props) {
  const { data: observations = [] } = useQuery({
    queryKey: ['cases', caseId, 'observations'],
    queryFn: () => fetchObservations(caseId),
    staleTime: 2 * 60 * 1000,
  })

  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: observations.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Row height
    overscan: 10, // Render 10 extra rows
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const observation = observations[virtualRow.index]
          return (
            <ObservationRow
              key={observation.id}
              observation={observation}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualRow.start}px)`,
              }}
            />
          )
        })}
      </div>
    </div>
  )
}

// Code Splitting
const Dashboard = lazy(() => import('./pages/Dashboard'))
const CaseDetail = lazy(() => import('./pages/CaseDetail'))
const Reports = lazy(() => import('./pages/Reports'))

// Image Optimization
function CompanyLogo({ url }: Props) {
  return (
    <img
      src={url}
      alt="Company"
      loading="lazy"
      decoding="async"
      width={200}
      height={100}
    />
  )
}
```

### 9.3 Caching Strategy

```python
# Redis Cache Implementation
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(expiry: int = 300):
    """Cache decorator with Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                expiry,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator

class ReportService:
    @cache_result(expiry=3600)  # Cache for 1 hour
    async def get_report(self, report_id: UUID) -> Report:
        # Expensive report generation
        return await self._generate_report(report_id)
```

---

## 10. デプロイメント戦略

### 10.1 Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: fund_user
      POSTGRES_PASSWORD: fund_dev_password
      POSTGRES_DB: fund_ic_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fund_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://fund_user:fund_dev_password@postgres:5432/fund_ic_dev
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://backend:8000/api/v1
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  postgres_data:
  redis_data:
```

### 10.2 Production Deployment (AWS)

```yaml
# GitHub Actions CI/CD
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml

      - name: Run Frontend Tests
        run: |
          cd frontend
          npm ci
          npm run test:ci
          npm run build

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster fund-cluster \
            --service fund-backend \
            --force-new-deployment

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to S3 + CloudFront
        run: |
          aws s3 sync ./frontend/dist s3://fund-frontend-bucket
          aws cloudfront create-invalidation \
            --distribution-id $DISTRIBUTION_ID \
            --paths "/*"
```

### 10.3 監視・ロギング

```python
# Structured Logging
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage in API endpoints
@router.post("/observations")
async def create_observation(data: ObservationCreate):
    logger.info(
        "Creating observation",
        case_id=str(data.case_id),
        source_tag=data.source_tag,
        user_id=str(current_user.id)
    )

    try:
        observation = await service.create_observation(data)

        logger.info(
            "Observation created",
            observation_id=str(observation.id),
            case_id=str(data.case_id)
        )

        return observation

    except Exception as e:
        logger.error(
            "Failed to create observation",
            error=str(e),
            case_id=str(data.case_id)
        )
        raise

# Metrics Collection (Prometheus)
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_latency = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint']
)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    api_latency.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## まとめ

この統合アーキテクチャ設計書は、Fund IC Automation System の Phase 1-6 実装に必要な全ての技術的詳細を網羅しています。

### 重要な設計原則

1. **Server State と UI State の明確な分離** - TanStack Query と Zustand の責務分離
2. **階層的な Query Key 設計** - 効率的なキャッシュ無効化戦略
3. **RBAC による細粒度の権限管理** - ロールベースのデータアクセス制御
4. **段階的なデータマスキング** - disclosure level に応じた情報開示
5. **エラーハンドリングの統一** - 一貫したエラーレスポンス形式
6. **パフォーマンス最適化** - Virtual scrolling, Code splitting, Caching
7. **監視とロギング** - 構造化ログとメトリクス収集

この設計に基づいて Phase 1 の実装を開始し、段階的に機能を追加していくことで、安定した拡張可能なシステムを構築できます。