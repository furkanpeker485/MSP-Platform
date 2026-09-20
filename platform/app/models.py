"""Kalıcı veri modeli."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Lane(str, enum.Enum):
    A = "A"  # uç cihaz ajanı
    B = "B"  # Ansible ile uzaktan ayar
    C = "C"  # sağlayıcı arayüzü
    D = "D"  # HR platform kurulumu
    E = "E"  # takvimli iş
    F = "F"  # insan iş emri


class TaskState(str, enum.Enum):
    PENDING = "pending"
    BLOCKED = "blocked"      # ön koşulu tamamlanmadı
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    package: Mapped[str] = mapped_column(String(32))  # Essential | Professional | Enterprise
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entitlements: Mapped[List["Entitlement"]] = relationship(back_populates="tenant")
    devices: Mapped[List["Device"]] = relationship(back_populates="tenant")


class Entitlement(Base):
    """Müşterinin satın aldığı hizmetlerin listesi. Sitedeki hizmet kimliğiyle aynıdır."""
    __tablename__ = "entitlements"
    __table_args__ = (UniqueConstraint("tenant_id", "service_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    service_id: Mapped[str] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(default=True)

    tenant: Mapped[Tenant] = relationship(back_populates="entitlements")


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    uuid: Mapped[str] = mapped_column(String(64), unique=True)   # agent kimliği
    serial: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    hostname: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(64))                # windows-server, switch, ...
    os_family: Mapped[Optional[str]] = mapped_column(String(32), default=None)
    agent_capable: Mapped[bool] = mapped_column(default=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    tenant: Mapped[Tenant] = relationship(back_populates="devices")


class SpecVersion(Base):
    """Derlenmiş arzu edilen durum. Sürümlüdür; geri alma buna dayanır."""
    __tablename__ = "spec_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    version: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSON)
    known_good: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TaskRun(Base):
    __tablename__ = "task_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    spec_version: Mapped[int] = mapped_column(Integer)
    service_id: Mapped[str] = mapped_column(String(80))
    task_id: Mapped[str] = mapped_column(String(120))
    lane: Mapped[Lane] = mapped_column(Enum(Lane))
    state: Mapped[TaskState] = mapped_column(Enum(TaskState), default=TaskState.PENDING)
    detail: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id"), default=None)
    actor: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120))
    payload: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
