from fastapi import FastAPI,Query,Path,Body,HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
from keepie_server.keepie_server.my_tools.my_jsons_api import User, ChangeAbleUser, TrackingReq, UsersList
from keepie_server.keepie_server.logic.api_handler import ApiHandler
import re


USER_TAG = "USER_TAG"
CONNECTIONS = "CONNECTIONS"
CHATS_TAG = "CHATS_TAG"

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
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return {}

@my_api.put("/user", status_code=200, tags=[USER_TAG])
def update_user(user:ChangeAbleUser = Body(..., title="User new details")):
    """
    # Update User
    """
    result, info = ApiHandler().update_user(user)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return {}


@my_api.get("/user/{id}", status_code=200, tags=[USER_TAG])
def get_user(id:str =Path(...,title="user id (phone number)")):
    """
    # Get User
    """
    result, info = ApiHandler().get_user(id)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return info

@my_api.put("/user/list", status_code=200, tags=[USER_TAG])
def get_users_list(users_ids: UsersList = Body(..., title="Users Ids (phones)")):
    """
    # Get Users List
    """
    print(f"ok {users_ids}")
    result, info = ApiHandler().get_users_lists(users_ids)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return info

@my_api.post("/tracking", status_code=200, tags=[CONNECTIONS])
def create_tracking_request(track_req:TrackingReq=Body(..., title="Tracking Request")):
    """
    # Create Tracking Request
    """
    result, info = ApiHandler().insert_tracking(track_req)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return {}


@my_api.put("/tracking", status_code=200, tags=[CONNECTIONS])
def update_tracking_request(track_req:TrackingReq=Body(..., title="Tracking Request")):
    """
    # Update Tracking Request
    """
    result, info = ApiHandler().update_tracking(track_req)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return {}

@my_api.get("/tracking/{id}/{is_child}", status_code=200, tags=[CONNECTIONS])
def get_trackings_request(id:str = Path(...,title="user id (phone number)"),
                         is_child:bool = Path(...,title="type of user")):
    """
    # Get All Tracking Connections
    """
    result, info = ApiHandler().get_trackings(id, is_child)
    if result != 200:
        raise HTTPException(status_code=result, detail=info)

    return info


docs_file = my_api.openapi()
docs_file["info"]["title"] = "Keepie"
docs_file["info"]["version"] = "0.0.1"

