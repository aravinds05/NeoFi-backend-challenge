from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base  

#enum
class UserRole(str, enum.Enum):
    OWNER = "Owner"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class PermissionEnum(str, enum.Enum):
    VIEWER = "Viewer"
    EDITOR = "Editor"

class RecurrenceEnum(str, enum.Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

# models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)

    events = relationship("Event", back_populates="owner", cascade="all, delete")
    shared_events = relationship("EventShare", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    recurrence = Column(Enum(RecurrenceEnum), default=RecurrenceEnum.NONE)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="events")
    shared_with = relationship("EventShare", back_populates="event")
    versions = relationship("EventVersion", back_populates="event")
    audit_logs = relationship("AuditLog", back_populates="event")

class EventShare(Base):
    __tablename__ = "shared_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    permission = Column(Enum(PermissionEnum), default=PermissionEnum.VIEWER)

    event = relationship("Event", back_populates="shared_with")
    user = relationship("User", back_populates="shared_events")

class EventVersion(Base):
    __tablename__ = "event_versions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    title = Column(String)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    timestamp = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(Integer, ForeignKey("users.id"))

    event = relationship("Event", back_populates="versions")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)

    event = relationship("Event", back_populates="audit_logs")