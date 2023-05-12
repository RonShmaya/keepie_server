from fastapi import FastAPI,Query,Path,Body,HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
from keepie_server.keepie_server.my_tools.my_jsons_api import User, ChangeAbleUser, TrackingReq, ConnectionsStatus
from keepie_server.keepie_server.logic.api_handler import ApiHandler
import re


USER_TAG = "USER_TAG"
USER_CONNECTION = "USER_CONNECTION"
CHATS_TAG = "CHATS_TAG"

#TODO: test if possible to send body with None

class myApi(FastAPI):
    def __init__(self):
        super().__init__()

my_api = myApi()

@my_api.post("/user", status_code=200, tags=[USER_TAG])
def create_user(user:User=Body(..., title="User details")):
    """
    # Create User
    """
    result, info = ApiHandler().insert_user(user)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}

@my_api.put("/user", status_code=200, tags=[USER_TAG])
def update_user(user:ChangeAbleUser=Body(..., title="User new details")):
    """
    # Update User
    """
    result, info = ApiHandler().update_user(user)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}


@my_api.get("/user/{id}", status_code=200, tags=[USER_TAG])
def get_user(id=Path(...,title="user id (phone number)")):
    """
    # Update User
    """
    result, info = ApiHandler().get_user(id)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}


@my_api.post("/tracking", status_code=200, tags=[USER_CONNECTION])
def create_tracking_request(track_req:TrackingReq=Body(..., title="Tracking Request")):
    """
    # Create Tracking Request
    """
    result, info = ApiHandler().insert_tracking(track_req)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}

@my_api.put("/tracking", status_code=200, tags=[USER_CONNECTION])
def update_tracking_request(track_req:TrackingReq=Body(..., title="Tracking Request")):
    """
    # Update Tracking Request
    """
    result, info = ApiHandler().update_tracking(track_req)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}

@my_api.get("/tracking", status_code=200, tags=[USER_CONNECTION])
def get_tracking_request(track_req:TrackingReq=Body(..., title="Tracking Request")):
    """
    # Update Tracking Request
    """
    result, info = ApiHandler().update_tracking(track_req)
    if not result:
        raise HTTPException(status_code=400, detail=info)

    return {}


docs_file = my_api.openapi()
docs_file["info"]["title"] = "Keepie"
docs_file["info"]["version"] = "0.0.1"

