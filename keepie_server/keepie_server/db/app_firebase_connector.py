import firebase_admin
from firebase_admin import credentials
from firebase_admin import db



class FirebaseConnector:
    __instance = None

    def __new__(cls):
        if FirebaseConnector.__instance is None:
            FirebaseConnector.__instance = object.__new__(cls)
            FirebaseConnector.__instance.__initialized = False
        return FirebaseConnector.__instance

    def __init__(self):
        if FirebaseConnector.__instance.__initialized: return
        FirebaseConnector.__instance.__initialized = True
        cred = credentials.Certificate('keepie-cb5ec-firebase-adminsdk-u5fis-b995b43031.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://keepie-cb5ec-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        self.root_accounts = db.reference('/').child("ACCOUNTS")
        self.root_chats = db.reference('/').child("CHATS")

    def get_user_chats(self, user_phone):
        return self.root_accounts.child(user_phone).child("chats").get()

    def get_chat(self, chat_id):
        return self.root_chats.child(chat_id).get()


FirebaseConnector().get_user_chats("+972502324023")