"""SQLAlchemy ORM models for database tables"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base
from app.models.schemas import CaseStatus, SourceTag, DisclosureLevel, ConflictType, UserRole


class User(Base):
    """User account model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True, default=None)  # 部門（オプション）
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    cases = relationship(
        "Case", back_populates="created_by_user", foreign_keys="Case.created_by"
    )
    observations = relationship(
        "Observation",
        back_populates="created_by_user",
        foreign_keys="Observation.created_by",
    )
    reports = relationship(
        "Report", back_populates="created_by_user", foreign_keys="Report.created_by"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", foreign_keys="AuditLog.user_id"
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Case(Base):
    """Case/deal model"""

    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    company_name = Column(String(255), nullable=False, index=True)
    sector = Column(String(255), nullable=True)
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.DRAFT)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_deleted = Column(Boolean, default=False, nullable=False)
    extra_data = Column(JSON, default={}, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="cases", foreign_keys=[created_by])
    observations = relationship("Observation", back_populates="case", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case {self.title} - {self.status}>"


class Observation(Base):
    """Observation/finding model"""

    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    section = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_tag = Column(Enum(SourceTag), nullable=False, default=SourceTag.PUBLIC)
    disclosure_level = Column(
        Enum(DisclosureLevel), nullable=False, default=DisclosureLevel.PRIVATE
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    extra_data = Column(JSON, default={}, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="observations", foreign_keys=[case_id])
    created_by_user = relationship(
        "User", back_populates="observations", foreign_keys=[created_by]
    )
    conflicts_1 = relationship(
        "Conflict",
        back_populates="observation_1",
        foreign_keys="Conflict.observation_id_1",
        cascade="all, delete-orphan",
    )
    conflicts_2 = relationship(
        "Conflict",
        back_populates="observation_2",
        foreign_keys="Conflict.observation_id_2",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Observation {self.section} - {self.source_tag}>"


class Conflict(Base):
    """Data conflict model"""

    __tablename__ = "conflicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    observation_id_1 = Column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    observation_id_2 = Column(
        UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False
    )
    conflict_type = Column(Enum(ConflictType), nullable=False)
    severity = Column(Float, nullable=False)  # 0.0 - 1.0
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    extra_data = Column(JSON, default={}, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="conflicts", foreign_keys=[case_id])
    observation_1 = relationship(
        "Observation", back_populates="conflicts_1", foreign_keys=[observation_id_1]
    )
    observation_2 = relationship(
        "Observation", back_populates="conflicts_2", foreign_keys=[observation_id_2]
    )
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self):
        return f"<Conflict {self.conflict_type} - severity {self.severity}>"


class Report(Base):
    """Report model"""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    report_type = Column(String(255), nullable=False)  # ic_report, lp_report, etc.
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=True)  # Report sections and data
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSON, default={}, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="reports", foreign_keys=[case_id])
    created_by_user = relationship("User", back_populates="reports", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Report {self.report_type} for case {self.case_id}>"


class AuditLog(Base):
    """Audit log for compliance tracking"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)  # create, read, update, delete, approve
    resource_type = Column(String(255), nullable=False)  # case, observation, report
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(1000), nullable=True)
    extra_data = Column(JSON, default={}, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} {self.resource_id}>"


# Index definitions for performance
# NOTE: Indexes are defined at the column level instead of globally
# to avoid "index already exists" errors when using fresh in-memory databases in tests
# Global Index objects cause issues with SQLAlchemy's metadata caching
