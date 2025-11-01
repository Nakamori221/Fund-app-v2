"""Pydantic schemas for request/response validation"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, Enum):
    """User roles"""

    ANALYST = "analyst"
    LEAD_PARTNER = "lead_partner"
    IC_MEMBER = "ic_member"
    ADMIN = "admin"


class CaseStatus(str, Enum):
    """Case statuses"""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class SourceTag(str, Enum):
    """Data source tags for observations"""

    PUBLIC = "PUB"  # Public information
    EXTERNAL = "EXT"  # External proprietary data
    INTERNAL = "INT"  # Internal company data
    CONFIDENTIAL = "CONF"  # Confidential/NDA data
    ANALYSIS = "ANL"  # Analysis/derived data


class DisclosureLevel(str, Enum):
    """Data disclosure levels for RBAC"""

    IC = "IC"  # Investment Committee only
    LP = "LP"  # Limited Partners
    LP_NDA = "LP_NDA"  # Limited Partners with NDA
    PRIVATE = "PRIVATE"  # Private/Internal


class ConflictType(str, Enum):
    """Types of conflicts detected"""

    PRICE_ANOMALY = "price_anomaly"
    DATA_INCONSISTENCY = "data_inconsistency"
    SOURCE_CONFLICT = "source_conflict"
    TIMING_CONFLICT = "timing_conflict"


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema"""

    email: str = Field(..., description="ユーザーメールアドレス")
    full_name: str = Field(..., description="ユーザーフルネーム")
    department: Optional[str] = Field(None, description="部門（オプション）")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema for creating user"""

    password: str = Field(..., description="パスワード（8文字以上）", min_length=8)
    role: UserRole = Field(UserRole.ANALYST, description="ユーザーロール")


class UserUpdate(BaseModel):
    """Schema for updating user"""

    email: Optional[str] = Field(None, description="メールアドレス")
    full_name: Optional[str] = Field(None, description="フルネーム")
    department: Optional[str] = Field(None, description="部門")
    is_active: Optional[bool] = Field(None, description="アクティブフラグ")
    role: Optional[UserRole] = Field(None, description="ロール（Adminのみ変更可）")

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User response schema"""

    id: str = Field(..., description="ユーザーID")
    role: UserRole = Field(..., description="ユーザーロール")
    is_active: bool = Field(True, description="ユーザーアクティブ状態")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, v):
        """UUIDオブジェクトを文字列に変換"""
        if isinstance(v, UUID):
            return str(v)
        return v


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""

    users: List[UserResponse] = Field(..., description="ユーザーリスト")
    total: int = Field(..., description="総ユーザー数")
    skip: int = Field(..., description="スキップ数")
    limit: int = Field(..., description="取得数")


class RoleInfo(BaseModel):
    """ロール情報"""

    role: UserRole = Field(..., description="ロール")
    description: str = Field(..., description="ロール説明")
    permissions: List[str] = Field(..., description="権限リスト")


class RoleListResponse(BaseModel):
    """ロール一覧レスポンス"""

    roles: List[RoleInfo] = Field(..., description="ロールリスト")


class ChangeRoleRequest(BaseModel):
    """ロール変更リクエスト"""

    role: UserRole = Field(..., description="新しいロール")


# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Login request schema"""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str = Field(..., description="Refresh token")


class CurrentUserResponse(BaseModel):
    """Current user response schema"""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    permissions: List[str] = Field(..., description="User permissions")


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogBase(BaseModel):
    """監査ログベース"""

    action: str = Field(
        ..., description="操作: create, read, update, delete, approve"
    )
    resource_type: str = Field(..., description="リソース種別: user, case, observation")
    resource_id: str = Field(..., description="リソースID")

    model_config = ConfigDict(from_attributes=True)


class AuditLogCreate(AuditLogBase):
    """監査ログ作成"""

    user_id: str = Field(..., description="操作ユーザーID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="変更前の値")
    new_values: Optional[Dict[str, Any]] = Field(None, description="変更後の値")
    ip_address: Optional[str] = Field(None, description="IPアドレス")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="追加データ")


class AuditLogResponse(AuditLogBase):
    """監査ログレスポンス"""

    id: str = Field(..., description="監査ログID")
    user_id: str = Field(..., description="操作ユーザーID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="変更前の値")
    new_values: Optional[Dict[str, Any]] = Field(None, description="変更後の値")
    timestamp: datetime = Field(..., description="操作日時")
    ip_address: Optional[str] = Field(None, description="IPアドレス")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")
    created_at: datetime = Field(..., description="作成日時")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, v):
        """UUIDオブジェクトを文字列に変換"""
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_user_id_to_string(cls, v):
        """UUIDオブジェクトを文字列に変換"""
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator("resource_id", mode="before")
    @classmethod
    def convert_resource_id_to_string(cls, v):
        """UUIDオブジェクトを文字列に変換"""
        if isinstance(v, UUID):
            return str(v)
        return v


class AuditLogListResponse(BaseModel):
    """監査ログ一覧レスポンス"""

    logs: List[AuditLogResponse] = Field(..., description="監査ログリスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップ数")
    limit: int = Field(..., description="取得数")


# ============================================================================
# Case Schemas
# ============================================================================

class CaseBase(BaseModel):
    """Base case schema"""

    title: str = Field(..., description="Case title", min_length=5, max_length=255)
    description: Optional[str] = Field(
        None, description="Case description", max_length=2000
    )
    company_name: str = Field(..., description="Company name", min_length=1)
    sector: Optional[str] = Field(None, description="Industry sector")
    status: CaseStatus = Field(CaseStatus.DRAFT, description="Case status")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )

    model_config = ConfigDict(from_attributes=True)


class CaseCreate(CaseBase):
    """Schema for creating case"""

    pass


class CaseUpdate(BaseModel):
    """Schema for updating case"""

    title: Optional[str] = Field(None, description="Case title")
    description: Optional[str] = Field(None, description="Case description")
    status: Optional[CaseStatus] = Field(None, description="Case status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")

    model_config = ConfigDict(from_attributes=True)


class CaseResponse(CaseBase):
    """Case response schema"""

    id: str = Field(..., description="Case ID")
    created_by: str = Field(..., description="User who created case")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    observation_count: int = Field(0, description="Number of observations")


# ============================================================================
# Observation Schemas
# ============================================================================

class ObservationBase(BaseModel):
    """Base observation schema"""

    case_id: str = Field(..., description="Associated case ID")
    section: str = Field(..., description="Report section")
    source_tag: SourceTag = Field(..., description="Data source tag")
    disclosure_level: DisclosureLevel = Field(
        DisclosureLevel.PRIVATE, description="Data disclosure level"
    )
    content: str = Field(..., description="Observation content", min_length=10)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")

    model_config = ConfigDict(from_attributes=True)


class ObservationCreate(ObservationBase):
    """Schema for creating observation"""

    pass


class ObservationUpdate(BaseModel):
    """Schema for updating observation"""

    section: Optional[str] = Field(None, description="Report section")
    content: Optional[str] = Field(None, description="Observation content")
    source_tag: Optional[SourceTag] = Field(None, description="Data source tag")
    disclosure_level: Optional[DisclosureLevel] = Field(
        None, description="Data disclosure level"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")

    model_config = ConfigDict(from_attributes=True)


class ObservationResponse(ObservationBase):
    """Observation response schema"""

    id: str = Field(..., description="Observation ID")
    created_by: str = Field(..., description="User who created observation")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_verified: bool = Field(False, description="Whether verified by lead partner")


# ============================================================================
# Conflict Schemas
# ============================================================================

class ConflictBase(BaseModel):
    """Base conflict schema"""

    case_id: str = Field(..., description="Associated case ID")
    observation_id_1: str = Field(..., description="First observation ID")
    observation_id_2: str = Field(..., description="Second observation ID")
    conflict_type: ConflictType = Field(..., description="Type of conflict")
    severity: float = Field(..., description="Conflict severity (0-1)", ge=0, le=1)
    description: str = Field(..., description="Conflict description")

    model_config = ConfigDict(from_attributes=True)


class ConflictResponse(ConflictBase):
    """Conflict response schema"""

    id: str = Field(..., description="Conflict ID")
    detected_at: datetime = Field(..., description="Detection timestamp")
    is_resolved: bool = Field(False, description="Whether conflict is resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


# ============================================================================
# Report Schemas
# ============================================================================

class ReportBase(BaseModel):
    """Base report schema"""

    case_id: str = Field(..., description="Associated case ID")
    report_type: str = Field(..., description="Type of report")
    title: str = Field(..., description="Report title")
    content: Optional[Dict[str, Any]] = Field(None, description="Report content")

    model_config = ConfigDict(from_attributes=True)


class ReportCreate(ReportBase):
    """Schema for creating report"""

    pass


class ReportResponse(ReportBase):
    """Report response schema"""

    id: str = Field(..., description="Report ID")
    created_by: str = Field(..., description="User who created report")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ============================================================================
# Pagination and Common Schemas
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""

    skip: int = Field(0, description="Number of items to skip", ge=0)
    limit: int = Field(20, description="Number of items to return", ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Generic paginated response"""

    data: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Limit applied")
    has_more: bool = Field(..., description="Whether more items exist")


# ============================================================================
# Error Response Schema
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail schema"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class ErrorResponse(BaseModel):
    """Error response schema"""

    error: ErrorDetail = Field(..., description="Error information")


# ============================================================================
# Health Check Schema
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")
