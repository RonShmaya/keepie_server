from typing import  Dict, List
from keepie_server.keepie_server.db.mydb import RequestsDbHandler
from keepie_server.keepie_server.db.app_firebase_connector import FirebaseConnector

class DataChild:
    def __init__(self,name,phone):
        self.name = name
        self.phone = phone
    def __eq__(self, other):
        self.phone == other.phone

    def __hash__(self):
        return hash(self.phone)

    def __str__(self):
        return f"DataChild name = {self.name}, phone = {self.phone}"


class DataTrack:
    def __init__(self,phone_child,phone_adult):
        self.phone_child = phone_child
        self.phone_adult = phone_adult

    def __eq__(self, other):
        self.phone_child == other.phone_child

    def __str__(self):
        return f"DataTrack phone_child = {self.phone_child}, phone_adult = {self.phone_adult}"


class DataChat:
    def __init__(self,chat_id: str, messages_dct):
        self.chat_id = chat_id
        self.messages = self.parse_messages_dct_to_obj(messages_dct)

    def parse_messages_dct_to_obj(self, messages_dct):
        return list(sorted(
                        map(lambda msg_item: DataMessage(msg_item[0],msg_item[1]),messages_dct.items())
                        ,key=lambda msg: -msg.time_milli
                    )
                )

    def __eq__(self, other):
        self.chat_id == other.chat_id

    def __hash__(self):
        return hash(self.chat_id)

    def __str__(self):
        return f"DataChat chat_id = {self.chat_id}, messages = {self.messages}"

class DataMessage:
    def __init__(self,msg_dct_key, msg_dct_value):
        self.id = msg_dct_key
        self.sender = msg_dct_value["sender"]
        self.receiver = msg_dct_value["receiver"]
        self.time_milli = msg_dct_value["_msg_calender"]["timeInMillis"]
        self.content = msg_dct_value["content"]

    def __eq__(self, other):
        self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"DataMessage id = {self.id}, sender = {self.sender}, receiver = {self.receiver}, time_milli = {self.time_milli}, content = {self.content}"

class DataProcessor:
    def __init__(self):
        pass

    def start_full_processing(self):
        # Pull From MongoDB child and alive tracks
        childs, tracks = self.__get_childs_and_tracks()
        is_over = self.__data_is_over([childs,tracks])
        if is_over:
            return

        # Parsing the data : Json -> Obj
        childs = self.__child_json_lst_to_objects(childs)
        tracks = self.__track_json_lst_to_objects(tracks)

        # Merge between child to his tracks, dump childs without tracks
        childs_track_dct = self.__merge_child_to_tracks_dct(childs, tracks)
        is_over = self.__data_is_over([childs_track_dct])
        if is_over:
            return

        # get & merge child to his chats ids
        childs_chats_ids_dct = self.__get_childs_chats_ids(childs_track_dct.keys())
        is_over = self.__data_is_over([childs_chats_ids_dct])
        if is_over:
            return

        # get & merge child to his chats
        childs_chats_dct = self.__get_child_chats_and_merge(childs_chats_ids_dct)
        for k,v in childs_chats_dct.items():
            print(f" {str(k)} ")
            for i in v:
                for d in i.messages:
                    print(f" {str(d)}  ")

        is_over = self.__data_is_over([childs_chats_dct])
        if is_over:
            return


    def __get_childs_and_tracks(self):
        return RequestsDbHandler().get_all_child_and_track()

    def __data_is_over(self, lst_of_lst):
        for lst in lst_of_lst:
            if lst == None or len(lst) == 0:
                return True
        return False

    def __child_json_lst_to_objects(self, childs):
        return list(map(lambda ch : DataChild(ch.name, ch.phone),childs))

    def __track_json_lst_to_objects(self, tracks):
        return list(map(lambda trk : DataTrack(trk.phone_child, trk.phone_adult),tracks))


    def __merge_child_to_tracks_dct(self, childs, tracks):
        """
        dct = {key = child : value = [Track]}
        """
        merge_dct = {}
        for child in childs:
            merge_dct[child] = list(filter(lambda trk: trk.phone_child == child.phone,tracks))

        return dict(filter(lambda item: len(item[1]) != 0, merge_dct.items()))

    def __get_childs_chats_ids(self, childs):
        """
        dct = {key = child : value = [Chats ids (str)]}
        """
        merge_dct = {}
        for child in childs:
            chats_dct = FirebaseConnector().get_user_chats(child.phone)
            if chats_dct is not None:
                merge_dct[child] = list(map(lambda ch : ch[0], chats_dct.items()))

        return merge_dct

    def __get_child_chats_and_merge(self, childs_chats_ids_dct):
        """
        dct = {key = child : value = [DataChats]}
        """
        merge_dct = {}
        for child, chats_ids_list in childs_chats_ids_dct.items():
            merge_dct[child] = []
            for chat_id in chats_ids_list:
                chat = FirebaseConnector().get_chat(chat_id)
                if chat is not None:
                    try:
                        data_chat = DataChat(chat_id, chat["messages"])
                        merge_dct[child].append(data_chat)
                    except Exception as exp:
                        print(f"error in __get_child_chats_and_merge {exp}")
                        break;

        return dict(filter(lambda item: len(item[1]) != 0, merge_dct.items()))



DataProcessor().start_full_processing()