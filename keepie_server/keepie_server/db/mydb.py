import pymongo
from pymongo.errors import DuplicateKeyError
from abc import ABC, abstractmethod
from fastapi import HTTPException
from http import HTTPStatus
from keepie_server.keepie_server.my_tools.my_jsons_api import User, ChangeAbleUser, TrackingReq, UsersList
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
                return 200, func(*args, **kw)
            except DuplicateKeyError as exp:
                print("DuplicateKeyError")
                print(str(exp))
                return HTTPStatus.FOUND, "Already Created..."
            except HTTPException as exp:
                print("HTTPException")
                print(exp.status_code)
                return exp.status_code, str(exp)
            except Exception as exp:
                print(type(exp))
                print(str(exp))
                return HTTPStatus.BAD_REQUEST, str(exp)

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
    def insert_user(self, user: User):
        self.exec.insert(Collections.USERS, user, user.phone)

    @ActDec()
    def update_user(self, user: User):
        self.exec.update_by_id(Collections.USERS, user.phone, user)

    @ActDec()
    def get_user(self, id: str):
        result_dict = self.exec.get_by_id(Collections.USERS, id)
        if not result_dict:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User didn't Founded")
        return User(name=result_dict["name"],
                    is_child=result_dict["is_child"],
                    phone=result_dict["phone"],
                    image=result_dict.get("image", None)
                    )

    @ActDec()
    def get_users_lists(self, users_lst):
        track_lst = list(self.exec.get_by_query( Collections.USERS, {"_id": {"$in": users_lst.phones}}))
        track_lst = list(map(self.exec.remove_id_from_dct, track_lst))
        return list(map(lambda dct: User(**dct), track_lst))

    @ActDec()
    def insert_tracking(self, track_req):
        self.exec.insert(Collections.TRACK, track_req, self.make_tracking_id(track_req.phone_child,track_req.phone_adult))

    @ActDec()
    def update_tracking(self, track_req: TrackingReq):
        self.exec.update_by_id(Collections.TRACK, self.make_tracking_id(track_req.phone_child,track_req.phone_adult), track_req)

    @ActDec()
    def get_trackings(self, id, is_child):
        track_lst = list(self.exec.get_by_query( Collections.TRACK, {"phone_child": id} if is_child else {"phone_adult": id}))
        track_lst = list(map(self.exec.remove_id_from_dct, track_lst))
        return list(map(lambda dct: TrackingReq(**dct), track_lst))

    @ActDec()
    def delete_tracking(self, child_phone,adult_phone):
        self.exec.delete_by_query(Collections.TRACK,  {"_id": self.make_tracking_id(child_phone,adult_phone)})

    def make_tracking_id(self,phone1:str,phone2:str):
        return phone1+phone2 if phone1 < phone2 else phone2+phone1

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

        result = self.collections_dict.get(coll_type).update_one(myquery, newvalues)
        if result.matched_count == 0:
            raise HTTPException(HTTPStatus.NOT_FOUND,"NOT FOUND")
        return result

    def get_by_id(self, coll_type, id: str):
        myquery = {"_id": id}
        return self.collections_dict.get(coll_type).find_one(myquery)

    def delete_by_query(self, coll_type, query):
        return self.collections_dict.get(coll_type).delete_one(query)

    def remove_id_from_dct(self,item):
        item.pop("_id", None)
        return item

    def get_by_query(self, coll_type, query):
        return self.collections_dict.get(coll_type).find(query)

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

    #RequestsDbHandler().update_user(ChangeAbleUser(phone="+97254441hh1120", name="name changedf"))
    #RequestsDbHandler().insert_user(User(name="lets go",phone="+972542262095",is_child=True))
    #RequestsDbHandler().get_user("+97254441112ff0")
    #RequestsDbHandler().insert_tracking(TrackingReq(phone_child="phone1",phone_adult="+2",approved=True,denied=False))
    #print(RequestsDbHandler().get_trackings("phone1",True))
    print(RequestsDbHandler().get_users_lists(UsersList(phones=["13245","+972542262095","+972544411120"])))
    #print(UsersList(phones=["13245","+972542262095","+972544411120"]).phones)

