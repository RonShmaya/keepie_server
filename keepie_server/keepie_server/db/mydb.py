import pymongo
from abc import ABC, abstractmethod
from keepie_server.keepie_server.my_tools.my_jsons_api import User, ChangeAbleUser, TrackingReq
from typing import Tuple, Dict, List
from pydantic import BaseModel
from enum import Enum

URI = "mongodb+srv://ronshmaya6:ronshmaya5@keepie.dx1wtej.mongodb.net/?retryWrites=true&w=majority"


class Collections(Enum):
    USERS = 1
    TRACK = 2
    CONNECTION = 3


class ActDec():
    def __init__(self):
        pass

    def __call__(self, func):

        def wrapper(*args, **kw):
            try:
                return True, func(*args, **kw)
            except Exception as exp:
                print(str(exp))
                return False, str(exp)

        return wrapper


class RequestsDbHandler:
    __instance = None

    def __new__(cls):
        if RequestsDbHandler.__instance is None:
            RequestsDbHandler.__instance = object.__new__(cls)
            RequestsDbHandler.__instance.__initialized = False
        return RequestsDbHandler.__instance

    def __init__(self, uri=None):
        if RequestsDbHandler.__instance.__initialized: return
        RequestsDbHandler.__instance.__initialized = True
        self.exec = ExecutorMongoDB()

    @ActDec()
    def insert_user(self, user: User) -> Tuple:
        self.exec.insert(Collections.USERS, user, user.phone)


    @ActDec()
    def get_user(self, id: str) -> Tuple:
        result_dict = self.exec.get_by_id(Collections.USERS, id)
        if not result_dict:
            raise Exception("User didn't Founded")
        return User(name=result_dict["name"],
                    is_child=result_dict["is_child"],
                    phone=result_dict["phone"],
                    image=result_dict.get("image", None)
                    )

    @ActDec()
    def insert_tracking(self, track_req) -> Tuple:
        self.exec.insert(Collections.TRACK, track_req, track_req.track_id)

    @ActDec()
    def update_tracking(self, track_req: TrackingReq) -> Tuple:
        self.exec.update_by_id(Collections.TRACK, track_req.track_id, track_req)

    # @ActDec()
    # def get_tracking(self, id: str) -> Tuple:
    #     result_dict = self.exec.get_by_id(Collections.TRACK, id)
    #     if not result_dict:
    #         raise Exception("Tracking didn't Founded")
    #     return User(name=result_dict["name"],
    #                 is_child=result_dict["is_child"],
    #                 phone=result_dict["phone"],
    #                 image=result_dict.get("image", None)
    #                 )


class ExecutorMongoDB:
    __instance = None

    def __new__(cls):
        if ExecutorMongoDB.__instance is None:
            ExecutorMongoDB.__instance = object.__new__(cls)
            ExecutorMongoDB.__instance.__initialized = False
        return ExecutorMongoDB.__instance

    def __init__(self, uri=None):
        if ExecutorMongoDB.__instance.__initialized: return
        ExecutorMongoDB.__instance.__initialized = True
        self.uri = uri if uri else URI
        self.client = pymongo.MongoClient(self.uri)
        self.db_name = "Keepie"
        self.coll_user_name = "user"
        self.coll_track_name = "track"
        self.coll_connection_name = "connections"
        self.users_coll = self.client[self.db_name][self.coll_user_name]
        self.track_coll = self.client[self.db_name][self.coll_track_name]
        self.connection_coll = self.client[self.db_name][self.coll_connection_name]
        self.collections_dict = {
            Collections.USERS: self.users_coll,
            Collections.TRACK: self.track_coll,
            Collections.CONNECTION: self.connection_coll,
        }

    def parse_base_model_to_dict(self, model: BaseModel, id=None):
        dct = model.dict()
        if id:
            dct["_id"] = id
        return dct

    def insert(self, coll_type, obj, id=None):
        return self.collections_dict.get(coll_type).insert_one(self.parse_base_model_to_dict(obj, id=id))

    def update_by_id(self, coll_type, id: str, update_model) -> Tuple:
        update_able_dct = self.parse_base_model_to_dict(update_model, id=id)
        update_able_dct = dict(filter(lambda kv: kv[1] != None, update_able_dct.items()))
        myquery = {"_id": id}
        newvalues = {"$set": update_able_dct}

        return self.collections_dict.get(coll_type).update_one(myquery, newvalues)

    def get_by_id(self, coll_type, id: str):
        myquery = {"_id": id}
        return self.collections_dict.get(coll_type).find_one(myquery)

    def get_db_lists(self):
        return self.client.list_database_names()

    def is_db_exists(self, db_name):
        return db_name in self.client.list_database_names()

    def get_collections_lists(self, db_name):
        return self.client[db_name].list_database_names()

    def is_collection_exists(self, db_name, collection_name):
        return collection_name in self.get_collections_lists(db_name)


if __name__ == "__main__":
    # print(CommMongoDB().get_db_lists())
    # user = User(name="fff", is_child=False, phone="453543")
    # cl = ExecutorMongoDB().create_user(user)
    # print(cl)
    # print(cl.get_db_lists())
    # cli = cl.client
    # col = cli["sample_supplies"]["new"]
    # user = User(name = "aaa", is_child=False, phone="5999")
    # col.insert_one(cl.parse_base_model_to_dict(user,user.phone))

    RequestsDbHandler().update_user(ChangeAbleUser(phone="abcdsefg", name="name changed"))
    # RequestsDbHandler().insert_user(User(name="lets go",phone="abcdsefg",is_child=True))
