import sys
sys.path.append("../")
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import (
    EventCreate, EventUpdate, EventOut,
    ShareEvent, ShareResponse, PermissionOut
)
from models import Event, User, EventShare
from auth.utils import get_current_user

router = APIRouter(prefix="/api/events", tags=["Events"])

# --- Helper: Check access permission ---
def get_event_if_authorized(db: Session, event_id: int, user: User):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.owner_id == user.id:
        return event

    shared = db.query(EventShare).filter_by(event_id=event_id, user_id=user.id).first()
    if not shared:
        raise HTTPException(status_code=403, detail="Access denied")

    return event


@router.post("/", response_model=EventOut)
def create_event(event_data: EventCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = Event(**event_data.dict(), owner_id=user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# user access events' list
@router.get("/", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned = db.query(Event).filter_by(owner_id=user.id).all()
    shared_ids = db.query(EventShare.event_id).filter_by(user_id=user.id).all()
    shared = db.query(Event).filter(Event.id.in_([id for (id,) in shared_ids])).all()
    return owned + shared


#fetch event by id
@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_event_if_authorized(db, event_id, user)

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, update_data: EventUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = get_event_if_authorized(db, event_id, user)  
    if event.owner_id != user.id:
        shared = db.query(EventShare).filter_by(event_id=event.id, user_id=user.id).first()
        if not shared or shared.permission != "Editor":
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.query(Event).filter_by(id=event_id, owner_id=user.id).first()
    if not event:
        raise HTTPException(status_code=403, detail="Only owner can delete this event")

    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@router.post("/{event_id}/share", response_model=ShareResponse)
def share_event(event_id: int, share: ShareEvent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.query(Event).filter_by(id=event_id, owner_id=user.id).first()
    if not event:
        raise HTTPException(status_code=403, detail="Only owner can share the event")

    existing = db.query(EventShare).filter_by(event_id=event_id, user_id=share.user_id).first()
    if existing:
        existing.permission = share.permission
    else:
        shared = EventShare(event_id=event_id, user_id=share.user_id, permission=share.permission)
        db.add(shared)

    db.commit()
    return db.query(EventShare).filter_by(event_id=event_id, user_id=share.user_id).first()

@router.get("/{event_id}/permissions", response_model=List[PermissionOut])
def get_permissions(event_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.query(Event).filter_by(id=event_id, owner_id=user.id).first()
    if not event:
        raise HTTPException(status_code=403, detail="Only owner can view permissions")

    shares = db.query(EventShare).filter_by(event_id=event_id).all()
    return shares


# update permissions
@router.put("/{event_id}/permissions/{user_id}", response_model=ShareResponse)
def update_permission(event_id: int, user_id: int, share: ShareEvent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot change own permissions")

    event = db.query(Event).filter_by(id=event_id, owner_id=user.id).first()
    if not event:
        raise HTTPException(status_code=403, detail="Only owner can update permissions")

    shared = db.query(EventShare).filter_by(event_id=event_id, user_id=user_id).first()
    if not shared:
        raise HTTPException(status_code=404, detail="User not found in share list")

    shared.permission = share.permission
    db.commit()
    return shared

@router.delete("/{event_id}/permissions/{user_id}")
def remove_access(event_id: int, user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    event = db.query(Event).filter_by(id=event_id, owner_id=user.id).first()
    if not event:
        raise HTTPException(status_code=403, detail="Only owner can revoke access")

    shared = db.query(EventShare).filter_by(event_id=event_id, user_id=user_id).first()
    if not shared:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(shared)
    db.commit()
    return {"message": "Access removed successfully"}