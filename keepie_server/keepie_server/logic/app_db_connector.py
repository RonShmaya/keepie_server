import firebase_admin
import time
import threading
from firebase_admin import credentials
from firebase_admin import db
from keepie_server.keepie_server.db.mydb import  RequestsDbHandler


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
        # # Get a reference to the root node of the database
        # root_ref = db.reference('/')
        #
        # # Read data from the database
        # data = root_ref.get()
        # print(data)
    def start(self):
        print(threading.current_thread().name)

FirebaseConnector()