from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import UniqueConstraint

from rememzo.utils import utc_now


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    # NOTE: keep username, pass, email nullable, so easy to locally setup for single user in v0.1
    id = Column(Uuid, primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Uuid, primary_key=True, default=uuid4)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    key_hash = Column(String(64), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    expired_at = Column(DateTime(timezone=True), nullable=True)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Uuid, primary_key=True, default=uuid4)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True) # Owner
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False) # problematic, many user can have project customer-support-agent, if we want to add unique slug then id already solve this
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Membership(Base):
    __tablename__ = "memberships"

    class RoleChoices(str, Enum):
        ADMIN = "admin"
        MEMBER = "member"
        GUEST = "guest"
    
    id = Column(Uuid, primary_key=True, default=uuid4)
    project_id = Column(ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, default=RoleChoices.MEMBER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    __table_args__ = (UniqueConstraint('project_id', 'user_id', name='project_members')),


class Memory(Base):
    __tablename__ = "memories"

    class ScopeChoices(str, Enum):
        USER = "user"
        PROJECT = "project"

    id = Column(Uuid, primary_key=True, default=uuid4)
    user_id = Column(ForeignKey("users.id"), nullable=True, index=True)
    project_id = Column(ForeignKey("projects.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    # vector = ? guess field. requires future discussion
    scope = Column(String, default=ScopeChoices.USER.value)
    is_active = Column(Boolean, default=True)
    extra = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    expired_at = Column(DateTime(timezone=True), nullable=True)
