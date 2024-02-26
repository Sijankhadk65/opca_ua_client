import firebase_admin
from firebase_admin import db
from datetime import datetime
import json


class FirebaseDBProvider:
    def __init__(self):
        self.cred = firebase_admin.credentials.Certificate('./key.json')
        self.app = firebase_admin.initialize_app(self.cred,{
            "databaseURL": "https://opc-ua-client-default-rtdb.firebaseio.com/"
        })
        self.db_ref = None

    def upload(self, minutes, temps):
        self.db_ref = db.reference(f"/{datetime.now().strftime('%d-%m-%y-%H_%M_%S_%f')}")
        self.db_ref.set(
            {
              "minutes": minutes,
              "temperatures": temps
            }
        )
