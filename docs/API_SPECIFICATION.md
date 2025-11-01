# Fund IC Automation System - API 詳細仕様書

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Base URL**: `https://api.fund-ic.example.com/api/v1`

## 目次

1. [認証 API](#1-認証-api)
2. [案件管理 API](#2-案件管理-api)
3. [観測データ API](#3-観測データ-api)
4. [矛盾検出・解決 API](#4-矛盾検出解決-api)
5. [レポート生成 API](#5-レポート生成-api)
6. [ドキュメント管理 API](#6-ドキュメント管理-api)
7. [WebSocket API](#7-websocket-api)
8. [共通仕様](#8-共通仕様)

---

## 1. 認証 API

### 1.1 POST /auth/register
**Description**: 新規ユーザー登録

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "山田 太郎",
  "role": "analyst"  // analyst | lead_partner | ic_member | admin
}
```

**Response (201 Created)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "山田 太郎",
  "role": "analyst",
  "created_at": "2025-11-01T10:00:00Z"
}
```

**Validation Rules**:
- Email: Valid email format, unique in database
- Password: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- Role: Must be one of the defined roles

### 1.2 POST /auth/login
**Description**: ユーザーログイン

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "analyst",
    "permissions": ["create:case", "read:case:own", "create:observation"]
  }
}
```

### 1.3 POST /auth/refresh
**Description**: アクセストークン更新

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### 1.4 GET /auth/me
**Description**: 現在のユーザー情報取得

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response (200 OK)**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "山田 太郎",
  "role": "analyst",
  "permissions": ["create:case", "read:case:own", "create:observation"],
  "last_login": "2025-11-01T09:30:00Z",
  "cases_owned": 5,
  "observations_created": 42
}
```

---

## 2. 案件管理 API

### 2.1 GET /cases
**Description**: 案件一覧取得（フィルタリング、ページネーション対応）

**Query Parameters**:
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| page | integer | No | ページ番号（1始まり） | 1 |
| limit | integer | No | 1ページあたりの件数（最大100） | 50 |
| status | string | No | ステータスフィルター | "active" |
| stage | string | No | ステージフィルター | "early" |
| lead_partner_id | UUID | No | リードパートナーでフィルター | |
| created_after | datetime | No | 作成日時の開始 | "2025-10-01T00:00:00Z" |
| created_before | datetime | No | 作成日時の終了 | "2025-10-31T23:59:59Z" |
| sort_by | string | No | ソート項目 | "created_at" |
| sort_order | string | No | ソート順序 | "desc" |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "case_id": "123e4567-e89b-12d3-a456-426614174000",
      "company_name": "TechStartup Inc.",
      "stage": "early",
      "status": "active",
      "website_url": "https://techstartup.com",
      "lead_partner": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "full_name": "田中 花子"
      },
      "analyst": {
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "full_name": "佐藤 次郎"
      },
      "ic_date": "2025-11-15T14:00:00Z",
      "created_at": "2025-10-15T10:30:00Z",
      "updated_at": "2025-10-20T15:45:00Z",
      "observation_count": 25,
      "conflict_count": 3,
      "completion_percentage": 75.5
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2.2 POST /cases
**Description**: 新規案件作成

**Request Body**:
```json
{
  "company_name": "TechStartup Inc.",
  "stage": "early",  // seed | early | growth | late
  "website_url": "https://techstartup.com",
  "industry": "SaaS",
  "location": "Tokyo, Japan",
  "founded_date": "2020-01-01",
  "description": "AI-powered analytics platform for e-commerce",
  "lead_partner_id": "550e8400-e29b-41d4-a716-446655440000",
  "analyst_id": "660e8400-e29b-41d4-a716-446655440001",
  "ic_date": "2025-11-15T14:00:00Z",
  "metadata": {
    "source": "referral",
    "priority": "high"
  }
}
```

**Response (201 Created)**:
```json
{
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "TechStartup Inc.",
  "stage": "early",
  "status": "active",
  "created_at": "2025-11-01T10:30:00Z",
  "created_by": "660e8400-e29b-41d4-a716-446655440001"
}
```

### 2.3 GET /cases/{case_id}
**Description**: 案件詳細取得

**Path Parameters**:
- `case_id` (UUID): 案件ID

**Query Parameters**:
- `include` (string[]): 含めるリレーション ["observations", "conflicts", "reports", "documents"]

**Response (200 OK)**:
```json
{
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "company_name": "TechStartup Inc.",
  "stage": "early",
  "status": "active",
  "website_url": "https://techstartup.com",
  "industry": "SaaS",
  "location": "Tokyo, Japan",
  "founded_date": "2020-01-01",
  "description": "AI-powered analytics platform for e-commerce",
  "lead_partner": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "田中 花子",
    "email": "tanaka@fund.com"
  },
  "analyst": {
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "full_name": "佐藤 次郎",
    "email": "sato@fund.com"
  },
  "ic_date": "2025-11-15T14:00:00Z",
  "created_at": "2025-10-15T10:30:00Z",
  "updated_at": "2025-10-20T15:45:00Z",
  "statistics": {
    "observation_count": 25,
    "conflict_count": 3,
    "resolved_conflicts": 1,
    "report_count": 2,
    "document_count": 5,
    "completion_percentage": 75.5,
    "last_activity": "2025-10-20T15:45:00Z"
  },
  "metadata": {
    "source": "referral",
    "priority": "high",
    "tags": ["ai", "saas", "b2b"]
  }
}
```

### 2.4 PUT /cases/{case_id}
**Description**: 案件情報更新

**Request Body** (Partial Update):
```json
{
  "status": "on_hold",
  "ic_date": "2025-11-20T14:00:00Z",
  "metadata": {
    "priority": "medium",
    "notes": "Waiting for additional financial data"
  }
}
```

**Response (200 OK)**: Updated case object

### 2.5 DELETE /cases/{case_id}
**Description**: 案件削除（ソフトデリート）

**Response (204 No Content)**: No body

---

## 3. 観測データ API

### 3.1 GET /observations
**Description**: 観測データ一覧取得

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | UUID | No | 案件IDでフィルター |
| section | string | No | セクション（kpi, business, market等） |
| field | string | No | フィールド名 |
| source_tag | string | No | ソースタグ（PUB, EXT, INT, CONF, ANL） |
| value_type | string | No | 値の型（number, string, date, boolean, json） |
| disclosure_level | string | No | 開示レベル（IC, LP, LP_NDA, PRIVATE） |
| created_after | datetime | No | 作成日時開始 |
| created_before | datetime | No | 作成日時終了 |
| page | integer | No | ページ番号 |
| limit | integer | No | 件数/ページ |

**Response (200 OK)**:
```json
{
  "items": [
    {
      "observation_id": "234e5678-e89b-12d3-a456-426614174001",
      "case_id": "123e4567-e89b-12d3-a456-426614174000",
      "section": "kpi",
      "field": "revenue_mrr",
      "value_type": "number",
      "value_number": 250000.00,
      "unit": "USD",
      "source_tag": "CONF",
      "evidence": "Financial statement Q3 2025",
      "evidence_url": "https://storage.example.com/docs/q3-2025.pdf#page=12",
      "as_of": "2025-09-30T23:59:59Z",
      "confidence": 0.95,
      "disclosure_level": "IC",
      "requires_approval": false,
      "is_selected": true,
      "notes": "Verified with CFO during interview",
      "created_by": {
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "full_name": "佐藤 次郎"
      },
      "created_at": "2025-10-20T14:30:00Z",
      "updated_at": "2025-10-20T14:30:00Z"
    }
  ],
  "pagination": {
    "total": 125,
    "page": 1,
    "limit": 50,
    "pages": 3
  }
}
```

### 3.2 POST /observations
**Description**: 観測データ作成

**Request Body**:
```json
{
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "section": "kpi",
  "field": "revenue_mrr",
  "value_type": "number",
  "value_number": 250000.00,
  "unit": "USD",
  "source_tag": "CONF",
  "evidence": "Financial statement Q3 2025",
  "evidence_url": "https://storage.example.com/docs/q3-2025.pdf#page=12",
  "as_of": "2025-09-30T23:59:59Z",
  "confidence": 0.95,
  "disclosure_level": "IC",
  "notes": "Verified with CFO during interview"
}
```

**Validation Rules**:
- Only one value_* field should be populated
- confidence must be between 0.0 and 1.0
- as_of cannot be in the future
- source_tag and disclosure_level must be valid enums

**Response (201 Created)**: Created observation object

### 3.3 POST /observations/bulk
**Description**: 複数観測データ一括作成

**Request Body**:
```json
{
  "observations": [
    {
      "case_id": "123e4567-e89b-12d3-a456-426614174000",
      "section": "kpi",
      "field": "revenue_mrr",
      "value_type": "number",
      "value_number": 250000.00,
      "unit": "USD",
      "source_tag": "CONF",
      "as_of": "2025-09-30T23:59:59Z",
      "confidence": 0.95,
      "disclosure_level": "IC"
    },
    {
      "case_id": "123e4567-e89b-12d3-a456-426614174000",
      "section": "kpi",
      "field": "paid_accounts",
      "value_type": "number",
      "value_number": 150,
      "unit": "count",
      "source_tag": "CONF",
      "as_of": "2025-09-30T23:59:59Z",
      "confidence": 0.95,
      "disclosure_level": "LP_NDA"
    }
  ]
}
```

**Response (201 Created)**:
```json
{
  "created": 2,
  "failed": 0,
  "observations": [
    { /* observation 1 */ },
    { /* observation 2 */ }
  ],
  "errors": []
}
```

### 3.4 GET /observations/{observation_id}
**Description**: 観測データ詳細取得

**Response (200 OK)**: Full observation object with all fields

### 3.5 PUT /observations/{observation_id}
**Description**: 観測データ更新

**Request Body**: Partial update supported

**Response (200 OK)**: Updated observation object

### 3.6 DELETE /observations/{observation_id}
**Description**: 観測データ削除

**Response (204 No Content)**: No body

### 3.7 POST /cases/{case_id}/collect-pub
**Description**: 公開情報自動収集（Web スクレイピング + AI 抽出）

**Request Body**:
```json
{
  "url": "https://techstartup.com",
  "sections": ["kpi", "business", "team"],  // Optional: specific sections to extract
  "max_pages": 5  // Optional: max pages to crawl
}
```

**Response (202 Accepted)**:
```json
{
  "job_id": "job_789e0123-e89b-12d3-a456-426614174002",
  "status": "processing",
  "estimated_duration_seconds": 30,
  "webhook_url": "https://api.fund-ic.example.com/api/v1/jobs/job_789e0123"
}
```

---

## 4. 矛盾検出・解決 API

### 4.1 POST /cases/{case_id}/detect-conflicts
**Description**: 矛盾検出実行

**Request Body**:
```json
{
  "sections": ["kpi", "financials"],  // Optional: specific sections
  "strategy": "all",  // all | numeric | string | date
  "threshold": {
    "numeric_deviation_pct": 10,
    "string_similarity": 0.9
  }
}
```

**Response (200 OK)**:
```json
{
  "conflicts": [
    {
      "conflict_id": "345e6789-e89b-12d3-a456-426614174002",
      "case_id": "123e4567-e89b-12d3-a456-426614174000",
      "field": "revenue_mrr",
      "conflict_type": "numeric_deviation",
      "severity": "WARNING",  // INFO | WARNING | CRITICAL
      "observations": [
        {
          "observation_id": "234e5678-e89b-12d3-a456-426614174001",
          "value": 250000,
          "source_tag": "CONF",
          "as_of": "2025-09-30T23:59:59Z",
          "confidence": 0.95
        },
        {
          "observation_id": "234e5678-e89b-12d3-a456-426614174002",
          "value": 280000,
          "source_tag": "PUB",
          "as_of": "2025-10-01T00:00:00Z",
          "confidence": 0.70
        }
      ],
      "statistics": {
        "min": 250000,
        "max": 280000,
        "mean": 265000,
        "deviation_pct": 12.0
      },
      "suggested_resolution": {
        "strategy": "source_priority",
        "recommended_observation_id": "234e5678-e89b-12d3-a456-426614174001",
        "reason": "CONF source has higher priority than PUB"
      },
      "created_at": "2025-11-01T11:00:00Z"
    }
  ],
  "summary": {
    "total_conflicts": 3,
    "by_severity": {
      "INFO": 1,
      "WARNING": 1,
      "CRITICAL": 1
    },
    "by_type": {
      "numeric_deviation": 2,
      "missing_required": 1
    }
  }
}
```

### 4.2 GET /conflicts
**Description**: 矛盾一覧取得

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| case_id | UUID | 案件IDでフィルター |
| severity | string | 重要度でフィルター |
| status | string | resolved / unresolved |
| field | string | フィールド名でフィルター |

**Response (200 OK)**: List of conflicts with pagination

### 4.3 GET /conflicts/{conflict_id}
**Description**: 矛盾詳細取得

**Response (200 OK)**: Full conflict details with all related observations

### 4.4 POST /conflicts/{conflict_id}/resolve
**Description**: 矛盾解決

**Request Body**:
```json
{
  "resolution": "select",  // select | merge | custom
  "selected_observation_id": "234e5678-e89b-12d3-a456-426614174001",
  "reason": "CONF source verified with management team",
  "custom_value": null,  // Used if resolution = "custom"
  "apply_to_future": true  // Apply this resolution rule to future conflicts
}
```

**Response (200 OK)**:
```json
{
  "conflict_id": "345e6789-e89b-12d3-a456-426614174002",
  "status": "resolved",
  "resolution": {
    "type": "select",
    "selected_observation_id": "234e5678-e89b-12d3-a456-426614174001",
    "reason": "CONF source verified with management team",
    "resolved_by": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "田中 花子"
    },
    "resolved_at": "2025-11-01T11:30:00Z"
  },
  "affected_observations": [
    {
      "observation_id": "234e5678-e89b-12d3-a456-426614174002",
      "action": "deselected",
      "is_selected": false
    }
  ]
}
```

---

## 5. レポート生成 API

### 5.1 POST /cases/{case_id}/generate-report
**Description**: レポート生成開始

**Request Body**:
```json
{
  "template_id": "ic_default",  // ic_default | lp_default | custom
  "format": "markdown",  // markdown | pdf | docx
  "disclosure_level": "IC",  // IC | LP
  "sections": {
    "include": ["exec_summary", "kpi_overview", "team"],
    "exclude": ["financials"]
  },
  "options": {
    "include_charts": true,
    "include_appendix": true,
    "language": "ja"  // ja | en
  }
}
```

**Response (202 Accepted)**:
```json
{
  "report_id": "456e7890-e89b-12d3-a456-426614174003",
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "generating",
  "estimated_duration_seconds": 60,
  "created_at": "2025-11-01T12:00:00Z"
}
```

### 5.2 GET /reports/{report_id}
**Description**: レポート取得

**Response (200 OK)**:
```json
{
  "report_id": "456e7890-e89b-12d3-a456-426614174003",
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "template_id": "ic_default",
  "status": "completed",  // generating | completed | failed
  "format": "markdown",
  "disclosure_level": "IC",
  "content": {
    "markdown": "# 投資推奨サマリー\n\n## 投資案件: TechStartup Inc.\n\n...",
    "sections": [
      {
        "section_id": "exec_summary",
        "title": "投資推奨サマリー",
        "content": "...",
        "data_sources": ["CONF", "INT", "ANL"]
      }
    ]
  },
  "metadata": {
    "word_count": 5420,
    "charts_included": 8,
    "data_points_used": 125,
    "generation_time_seconds": 45
  },
  "download_urls": {
    "markdown": "https://storage.example.com/reports/456e7890.md",
    "pdf": "https://storage.example.com/reports/456e7890.pdf"
  },
  "created_by": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "田中 花子"
  },
  "created_at": "2025-11-01T12:00:00Z",
  "completed_at": "2025-11-01T12:00:45Z"
}
```

### 5.3 GET /reports
**Description**: レポート一覧取得

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| case_id | UUID | 案件IDでフィルター |
| template_id | string | テンプレートIDでフィルター |
| status | string | ステータスでフィルター |
| created_after | datetime | 作成日時開始 |
| created_before | datetime | 作成日時終了 |

### 5.4 PUT /reports/{report_id}
**Description**: レポート手動編集

**Request Body**:
```json
{
  "sections": {
    "exec_summary": {
      "content": "Updated executive summary content..."
    }
  },
  "metadata": {
    "edited_by": "Manual review by IC member"
  }
}
```

### 5.5 DELETE /reports/{report_id}
**Description**: レポート削除

---

## 6. ドキュメント管理 API

### 6.1 POST /cases/{case_id}/documents
**Description**: ドキュメントアップロード

**Request**: Multipart/form-data
```
file: (binary)
metadata: {
  "document_type": "financial_statement",
  "period": "Q3 2025",
  "is_confidential": true,
  "tags": ["quarterly", "audited"]
}
```

**Response (201 Created)**:
```json
{
  "document_id": "567e8901-e89b-12d3-a456-426614174004",
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "file_name": "Q3_2025_Financial_Statement.pdf",
  "file_type": "application/pdf",
  "file_size": 2485760,
  "storage_url": "https://storage.example.com/documents/567e8901.pdf",
  "is_confidential": true,
  "metadata": {
    "document_type": "financial_statement",
    "period": "Q3 2025",
    "tags": ["quarterly", "audited"]
  },
  "uploaded_by": {
    "user_id": "660e8400-e29b-41d4-a716-446655440001",
    "full_name": "佐藤 次郎"
  },
  "uploaded_at": "2025-11-01T13:00:00Z"
}
```

### 6.2 GET /cases/{case_id}/documents
**Description**: 案件のドキュメント一覧

**Response (200 OK)**: List of documents with metadata

### 6.3 GET /documents/{document_id}
**Description**: ドキュメントメタデータ取得

### 6.4 GET /documents/{document_id}/download
**Description**: ドキュメントダウンロード

**Response**: Binary file stream or redirect to signed URL

### 6.5 DELETE /documents/{document_id}
**Description**: ドキュメント削除

---

## 7. WebSocket API

### 7.1 Connection
**URL**: `wss://api.fund-ic.example.com/ws`

**Authentication**:
```javascript
const socket = io('wss://api.fund-ic.example.com', {
  auth: {
    token: 'Bearer eyJhbGciOiJIUzI1NiIs...'
  }
})
```

### 7.2 Events

#### Server → Client Events

**observation.created**
```json
{
  "event": "observation.created",
  "data": {
    "observation_id": "234e5678-e89b-12d3-a456-426614174001",
    "case_id": "123e4567-e89b-12d3-a456-426614174000",
    "field": "revenue_mrr",
    "created_by": "佐藤 次郎",
    "timestamp": "2025-11-01T14:00:00Z"
  }
}
```

**conflict.detected**
```json
{
  "event": "conflict.detected",
  "data": {
    "conflict_id": "345e6789-e89b-12d3-a456-426614174002",
    "case_id": "123e4567-e89b-12d3-a456-426614174000",
    "field": "revenue_mrr",
    "severity": "WARNING",
    "timestamp": "2025-11-01T14:05:00Z"
  }
}
```

**report.completed**
```json
{
  "event": "report.completed",
  "data": {
    "report_id": "456e7890-e89b-12d3-a456-426614174003",
    "case_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "download_url": "https://storage.example.com/reports/456e7890.pdf"
  }
}
```

**approval.required**
```json
{
  "event": "approval.required",
  "data": {
    "observation_id": "234e5678-e89b-12d3-a456-426614174001",
    "case_id": "123e4567-e89b-12d3-a456-426614174000",
    "field": "deal.investment_amount",
    "sla_deadline": "2025-11-01T16:00:00Z",
    "priority": "high"
  }
}
```

#### Client → Server Events

**subscribe.case**
```json
{
  "event": "subscribe.case",
  "data": {
    "case_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**unsubscribe.case**
```json
{
  "event": "unsubscribe.case",
  "data": {
    "case_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

---

## 8. 共通仕様

### 8.1 認証
全てのAPI（認証エンドポイントを除く）は Bearer Token 認証が必要：
```
Authorization: Bearer {access_token}
```

### 8.2 エラーレスポンス形式
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid field value",
  "details": {
    "field": "confidence",
    "value": 1.5,
    "reason": "Value must be between 0.0 and 1.0"
  },
  "timestamp": "2025-11-01T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

### 8.3 HTTPステータスコード

| Code | Meaning | Error Code | Action |
|------|---------|------------|--------|
| 200 | OK | - | Success |
| 201 | Created | - | Resource created |
| 202 | Accepted | - | Async processing started |
| 204 | No Content | - | Success with no body |
| 400 | Bad Request | VALIDATION_ERROR | Fix request |
| 401 | Unauthorized | AUTHENTICATION_ERROR | Login required |
| 403 | Forbidden | AUTHORIZATION_ERROR | Insufficient permissions |
| 404 | Not Found | NOT_FOUND | Check resource ID |
| 409 | Conflict | CONFLICT_ERROR | Resolve conflict |
| 429 | Too Many Requests | RATE_LIMIT_ERROR | Retry with backoff |
| 500 | Internal Server Error | INTERNAL_ERROR | Retry or contact support |
| 503 | Service Unavailable | SERVICE_UNAVAILABLE | Retry later |

### 8.4 Rate Limiting
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1667318400
```

### 8.5 Request ID
全てのレスポンスに Request ID を含める：
```
X-Request-ID: req_abc123def456
```

### 8.6 CORS
```
Access-Control-Allow-Origin: https://app.fund-ic.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

### 8.7 Pagination
標準ページネーションパラメータ：
- `page`: ページ番号（1始まり）
- `limit`: 1ページあたりの件数（デフォルト50、最大100）
- `sort_by`: ソート項目
- `sort_order`: asc | desc

レスポンス形式：
```json
{
  "items": [...],
  "pagination": {
    "total": 250,
    "page": 1,
    "limit": 50,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### 8.8 Date/Time Format
全て ISO 8601 形式（UTC）：
```
2025-11-01T10:30:00Z
```

### 8.9 UUID Format
全ての ID は UUID v4：
```
550e8400-e29b-41d4-a716-446655440000
```

---

## API Version Management

### Current Version
- Version: 1.0.0
- Base URL: `/api/v1`

### Deprecation Policy
- 新バージョンリリース後、旧バージョンは最低6ヶ月間サポート
- Deprecation は `Sunset` header で通知
- Breaking changes は新バージョンでのみ実施

### Version History
- v1.0.0 (2025-11-01): Initial release

---

**End of API Specification**