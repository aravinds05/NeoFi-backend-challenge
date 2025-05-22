from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

#enum
class UserRole(str, Enum):
    OWNER = "Owner"
    EDITOR = "Editor"
    VIEWER = "Viewer"

class PermissionEnum(str, Enum):
    VIEWER = "Viewer"
    EDITOR = "Editor"

class RecurrenceEnum(str, Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
#user
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True

#auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(UserCreate):
    pass
#events
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    recurrence: RecurrenceEnum = RecurrenceEnum.NONE

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

#sharing
class ShareEvent(BaseModel):
    user_id: int
    permission: PermissionEnum

class ShareResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    permission: PermissionEnum

    class Config:
        from_attributes = True

class PermissionOut(BaseModel):
    user_id: int
    permission: PermissionEnum

    class Config:
        from_attributes = True

class EventVersionOut(BaseModel):
    id: int
    event_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    timestamp: datetime
    modified_by: int

    class Config:
        from_attributes = True

# log
class AuditLogOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    action: str
    timestamp: datetime
    details: Optional[str]

    class Config:
        from_attributes = True
