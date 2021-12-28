import pyrebase
import re
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

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
email = 'tariq@gmail.com'
auth.send_password_reset_email(email)
# link = auth.generate_password_reset_link(email)
# # Construct password reset email from a template embedding the link, and send
# # using a custom SMTP server.
# send_custom_email(email, link)
# data=db.child('Bio_researcher').child('aa').child('Chinee apple').get()
# blogs = db.child("Bio_researcher").child("aa").child("blogs").get()
# blogs = db.child("Bio_researcher").child('umeed').child("blogs").get()
# if db.child("Bio_researcher").child('umeed').child("blogs").get().val():
#     print("user exists")
# else:
#     print("user does not exist")

data = db.child("Library").child("blogs").get()
values = data.val()
useremail = 'waseemahmadcomsats@gmail.com'
password = 'ali123'
# if(auth.sign_in_with_email_and_password(useremail,password)):
#     print('yes')
# print(data)
# print(values)
# text = input("Enter the value")
# target = []
# for i in data.each():
#     blogs = i.val() 
#     if re.search(text,i.val()['title']):
#         print(i.val()['title'])
#         target.append([i.val(),i.key()])
#     print(i.key())
# print(len(target))
# # print(target[0][1])
# for i in target:
#     print("key :",i[1])
#     print("title :",i[0]['title'])

       
    # data = db.child("Library").child("blogs").child(i.key()+"").order_by_child("title").equal_to("thisi").get()
#     print(data.val())
# data = db.child("Library").child("blogs").order_by_child("-MnyJ1etWZdastqN1o5n").child("title").equal_to("this is the title of this post").get() 
# print(data.key())
    # va = i.val()
    # print(blogs['title'])