from keepie_server.keepie_server.my_tools.my_jsons_api import  User,ChangeAbleUser, UsersList
from keepie_server.keepie_server.db.mydb import  RequestsDbHandler

# EVERY api function return BOOL,INFO
class ApiHandler:
    __instance = None

    def __new__(cls):
        if ApiHandler.__instance is None:
            ApiHandler.__instance = object.__new__(cls)
            ApiHandler.__instance.__initialized = False
        return ApiHandler.__instance

    def __init__(self):
        if ApiHandler.__instance.__initialized: return
        ApiHandler.__instance.__initialized = True

    def insert_user(self, user:User):
        return RequestsDbHandler().insert_user(user)

    def update_user(self, userNewDetails:ChangeAbleUser):
        return RequestsDbHandler().update_user(userNewDetails)

    def get_user(self, id:str):
        return RequestsDbHandler().get_user(id)

    def get_users_lists(self, usersList: UsersList):
        return RequestsDbHandler().get_users_lists(usersList)

    def insert_tracking(self, track_req):
        return RequestsDbHandler().insert_tracking(track_req)

    def update_tracking(self, track_req):
        return RequestsDbHandler().update_tracking(track_req)

    def get_trackings(self, id, is_child):
        return RequestsDbHandler().get_trackings(id, is_child)

