import time
import threading
import random
from datetime import datetime
from queue import Queue
from keepie_server.keepie_server.db.mydb import RequestsDbHandler
from keepie_server.keepie_server.db.app_firebase_connector import FirebaseConnector
from keepie_server.keepie_server.my_tools.my_jsons_api import ChatStatus

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
        self.chat_status = None

    def set_chat_status(self, chat_status):
        self.chat_status = chat_status

    def get_chat_status(self):
        return self.chat_status

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
        return f"DataChat chat_id = {self.chat_id}, messages = {self.messages} , chat status {self.chat_status}"


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
    __instance = None

    def __new__(cls):
        if DataProcessor.__instance is None:
            DataProcessor.__instance = object.__new__(cls)
            DataProcessor.__instance.__initialized = False
        return DataProcessor.__instance

    def __init__(self):
        if DataProcessor.__instance.__initialized: return
        DataProcessor.__instance.__initialized = True
        self.proc_queue_data = Queue()
        self.full_proc_lock = threading.Lock()

    def decorate_runs_processing_in_the_loop(self, processing_func, exec_balance_time, is_exec_first, exec_times):
        """
        :param processing_func: the processing function
        :param exec_balance_time: the balance between the exec times In seconds!
        :param is_exec_first: sleep first or run first
        :param exec_times: -1 for always other is exec time to exec
        :return: None
        """

        times_run = 0

        if is_exec_first:
            processing_func()
            times_run+=1

        while exec_times < 0 or times_run < exec_times:
            time.sleep(exec_balance_time)
            times_run+=1
            processing_func()


    def start_full_processing(self):
        self.full_proc_lock.acquire()
        try:
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
            is_over = self.__data_is_over([childs_chats_dct])
            if is_over:
                return

            # get Chat status and remove tested messages
            childs_chats_dct = self.__remove_tested_messages(childs_chats_dct)
            is_over = self.__data_is_over([childs_chats_dct])
            if is_over:
                return
            print_all(childs_chats_dct)
            self.proc_queue_data.put(childs_chats_dct)
            self.__add_grades(childs_chats_dct)
            self.__send_and_save(childs_chats_dct, 50)

        finally:
            self.full_proc_lock.release()


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

    def __remove_tested_messages(self, childs_chats_dct):
        for child , chats in childs_chats_dct.items():
            for chat in chats:
                chat_status = RequestsDbHandler().get_chat(chat.chat_id)
                if chat_status is not None:
                    chat.set_chat_status(chat_status)
                    index = 0
                    for msg in chat.messages:
                        if msg.time_milli > chat_status.last_msg_test_milli:
                            index+=1
                        else:
                            break
                    if index >= 0:
                        chat.messages = chat.messages[0:index]

        # remove chat without msgs & childs without chats
        return dict(filter(lambda child_chat: len(list(filter(lambda chat: len(chat.messages) != 0 ,child_chat[1]))) != 0 ,childs_chats_dct.items()))

    def __add_grades(self, childs_chats_dct):
        for child, chats in childs_chats_dct.items():
            for chat in chats:
                if chat.get_chat_status() is None:
                    chat.set_chat_status(
                        ChatStatus(chat_id=chat.chat_id,
                                   child_phone= child.phone,
                                   other_phone= chat.messages[0].receiver if chat.messages[0].sender == child.phone else chat.messages[0].sender,
                                   grade = random.randint(0,15),
                                   last_msg_test_milli = chat.messages[0].time_milli,
                                   last_notification = time.time()))
                    RequestsDbHandler().insert_chat(chat.get_chat_status())
                else:
                    chat.get_chat_status().grade = random.randint(0,100)

    def __send_and_save(self, childs_chats_dct, max_grade):
        for child, chats in childs_chats_dct.items():
            for chat in chats:
                chat_status = chat.get_chat_status()
                if chat_status.grade > max_grade:
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    FirebaseConnector().exec_notification("Violante Chat",
                                                          f"{formatted_datetime} {chat_status.child_phone} get Violante messages from {chat_status.other_phone}",
                                                          chat_status.child_phone[1:len(chat_status.child_phone)])
                #chat_status.last_msg_test_milli = chat.messages[0].time_milli #TODO: will not check pre messages
                RequestsDbHandler().update_chat(chat_status)

def print_all(childs_chats_dct):
    for child, chats in childs_chats_dct.items():
        print(str(child))
        for chat in chats:
            print(chat)
            for msg in chat.messages:
                print(msg)

if __name__ == "__main__":
    DataProcessor().start_full_processing()
    chat_id: str
    child_phone: str
    other_phone: str
    grade: int
    last_msg_test_milli: int
    last_notification: int