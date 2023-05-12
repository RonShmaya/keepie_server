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


class ConnectionsStatus(BaseModel):
    connection_id: str
    phone_child: str
    phone_adult: str
    is_connect: bool


class TrackingReq(BaseModel):
    track_id: str
    phone_child: str
    phone_adult: str
    approved: bool
    denied: bool


