from flask import Flask,session
import pyrebase
config={
    "apiKey": "AIzaSyC08NejXipr0HoLAV10f3QHm4-6SQvsYI0",
    "authDomain": "flask-test-e4c30.firebaseapp.com",
    "databaseURL": "https://flask-test-e4c30-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "flask-test-e4c30",
    "storageBucket": "flask-test-e4c30.appspot.com",
    "messagingSenderId": "747159859988",
    "appId": "1:747159859988:web:f036a164597af31efe4801",
    "measurementId": "G-4KB1H32JDY"
};

app = Flask(__name__)

firebase = pyrebase.initialize_app(config)


db = firebase.database()
auth = firebase.auth()
app.config['UPLOAD_FOLDER'] = 'Farmica_app\\static\\image'
from Farmica_app import routes