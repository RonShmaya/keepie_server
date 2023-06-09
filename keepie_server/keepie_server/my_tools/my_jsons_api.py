from pydantic import BaseModel 
from typing import Optional, Dict, List
from enum import Enum


class User(BaseModel):
    name: str
    is_child: bool
    image: Optional[str] = None
    phone: str


class ChangeAbleUser(BaseModel):
    name: Optional[str] = None
    is_child: Optional[bool] = None
    image: Optional[str] = None
    phone: str


class UsersList(BaseModel):
    phones: List[str]


class TrackingReq(BaseModel):
    phone_child: str
    phone_adult: str
    approved: bool
    denied: bool

class ChatStatus(BaseModel):
    chat_id: str
    child_phone: str
    other_phone: str
    grade: int
    last_msg_test_milli: int
    last_notification: int



