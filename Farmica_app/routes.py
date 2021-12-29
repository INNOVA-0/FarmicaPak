from Farmica_app import app, db, auth
from flask import render_template, redirect, url_for, request, session, flash
from werkzeug.utils import secure_filename
import os,re

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import random
import string

import numpy as np
from tensorflow import keras

model = keras.models.load_model("weed_classifier.h5")
weeds_list = ['Chinee apple', 'Lantana', 'Negative', 'Parkinsonia', 'Parthenium', 'Prickly acacia', 'Rubber vine',
              'siam weed', 'Snake weed']


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> Bio-Researcher/Botanists Module  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#

# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>>(1) Index page  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/")
@app.route("/index")
def index():
    botanists = len(db.child('Bio_researcher').get().val())
    blogs = len(db.child('Library').child('blogs').get().val())
    return render_template('Bio_researcher/index.html', botanists=(botanists / 10) * 100, blogs=(blogs / 50) * 100)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (2)View all blogs inside of library  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/weed_library/', defaults={'subject': 'Lantana'}, methods=['POST', 'GET'])
@app.route('/weed_library/<subject>', methods=['POST', 'GET'])
def weed_library(subject):
    if request.method == "POST":
        subject = request.form['search']
    weed_classes = []
    print(subject)
    # all classes of weeds
    data = db.child("Library").child('Weed_classes').get()
    for i in data.each():
        weed_classes.append([i.key(), len(i.val())])
        # read all blogs
    searching = 'no'
    blogs = 'empty'
    if db.child("Library").child('Weed_classes').child(subject + "").get().val():
        blogs = db.child("Library").child('Weed_classes').child(subject + "").get()
    else:
        pass

    return render_template('Bio_researcher/weeds_library.html', blogs=blogs, classes=weed_classes,
                           current_class=subject, searching=searching)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>>(3) Output of search operation  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/weed_library_search', methods=['POST', 'GET'])
def weed_library_search():
    if request.method == 'POST':
        search = request.form['search']
        class1 = request.form['curent_class']
        print(search)
        print(class1)
        # all classes of weeds
        weed_classes = []
        data = db.child("Library").child('Weed_classes').get()
        for i in data.each():
            weed_classes.append([i.key(), len(i.val())])
        blogs = 'empty'
        searching = 'yes'
        # if db.child("Library").child('Weed_classes').child(class1+"").get().val():
        #     blogs = db.child("Library").child('Weed_classes').child(class1+"").get()
        # else:
        #     pass
        data = db.child("Library").child("blogs").get()
        values = data.val()
        blogs = []
        for i in data.each():
            if re.search(search, i.val()['title']):
                blogs.append([i.val(), i.key()])
    return render_template('Bio_researcher/weeds_library.html', blogs=blogs, classes=weed_classes, current_class=class1,
                           searching=searching)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (4)BLOG View  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/blog/', defaults={'subject': 'null'})
@app.route('/blog/<subject>')
def blog(subject):
    if subject == 'null':
        return redirect(url_for('index'))
    index1 = subject.index('-')
    key = subject[0:index1]
    key1 = subject[index1:index1 + 20]
    key3 = subject[index1 + 20:]
    data = db.child("Bio_researcher").child(key3).child(key3 + "1").get()
    values = data.val()
    # classes where are blogs for this user
    weed_classes_posted = []
    data = db.child("Library").child('Weed_classes').get()
    for i in data.each():
        db1 = db.child("Library").child('Weed_classes').child(i.key()).get()
        for j in db1.each():
            if j.val()['editor'] == key3:
                print(i.val())
                weed_classes_posted.append([i.key(), len(i.val())])
                break
    blogs = db.child("Library").child('Weed_classes').child(key + "").child(key1).get()
    print(blogs.val())
    return render_template('Bio_researcher/blog.html', user_data=values, classes=weed_classes_posted, blog=blogs)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (5)Contact  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/contact")
def contact():
    return render_template('Bio_researcher/contact.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (6)About  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/farmica_pak_web_about")
def about():
    botanists = len(db.child('Bio_researcher').get().val())
    blogs = len(db.child('Library').child('blogs').get().val())
    return render_template('Bio_researcher/about.html', botanists=(botanists / 10) * 100, blogs=(blogs / 50) * 100)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (7)Login Botanists  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'useremail' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            useremail = request.form['useremail']
            password = request.form['password']
            auth.sign_in_with_email_and_password(useremail, password)
            session['useremail'] = useremail
            return redirect(url_for('weed_library'))
        except:
            flash('Eamil or password is wrong!', 'success')
            return redirect(url_for('login'))
    return render_template('Bio_researcher/login.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (8)SignUp  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if 'useremail' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail']
        password = request.form['password']
        try:
            login = auth.create_user_with_email_and_password(useremail, password)
            user = {
                "username": username,
                "email": useremail,
                "password": password,
                "about": "aboutme"
            }
            index1 = useremail.index('@')
            key = useremail[0:index1]
            db.child('Bio_researcher').child(key).child(key + "1").update(user)
            # auth.send_email_verification(login['id_token'])
            flash(username + ' Added successfully!. Please Login', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email Already Exist!', 'success')

        return render_template('Bio_researcher/signup.html')
    return render_template('Bio_researcher/signup.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (8-2)Reset password  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        useremail = request.form['useremail']
        auth.send_password_reset_email(useremail)
        flash('Password reset mail is sent to your email account!,Please rest!', 'success')
    return render_template('Bio_researcher/reset.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (9)Logout botanists  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/logout')
def logout():
    session.pop('useremail', None)
    return redirect(url_for('index'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (10)View Profile  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/profile/', defaults={'subject': 'Lantana'})
@app.route('/profile/<subject>')
def profile(subject):
    if 'useremail' in session:
        index1 = session['useremail'].index('@')
        key = session['useremail'][0:index1]
        if '@' in subject:
            index2 = subject.index('@')
            key1 = subject[0:index2]
            subject = subject[index2 + 10:]
    else:
        index1 = subject.index('@')
        key = subject[0:index1]
        subject = subject[index1 + 10:]

    weed_classes = []
    # all classes of weeds
    data = db.child("Library").child('Weed_classes').get()
    for i in data.each():
        db1 = db.child("Library").child('Weed_classes').child(i.key()).get()
        for j in db1.each():
            if j.val()['editor'] == key:
                weed_classes.append([i.key(), len(i.val())])
                break

    # get the blogs of this user
    blogs = 'empty'
    data = db.child("Bio_researcher").child(key).child(key + "1").get()
    values = data.val()
    if db.child("Library").child('Weed_classes').child(subject + "").get().val():
        blogs = db.child("Library").child('Weed_classes').child(subject + "").get()
    else:
        pass
    return render_template('Bio_researcher/profile.html', blogs=blogs, user_data=values, classes=weed_classes,
                           user_id=key, subject=subject)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (11)Update Botanists proflie  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/update-researcher", methods=['post', 'get'])
def update_researcher():
    if 'useremail' in session:
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            aboutme = request.form['aboutme']
            index1 = email.index('@')
            key1 = email[0:index1]
            cover_image = request.files['profileimg']
            myfilename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join('Farmica_app\\static\\profile_image', myfilename))
            db.child('Bio_researcher').child(key1 + "").child(key1 + "1").update(
                {"username": username, 'about': aboutme, 'profileimg': myfilename})
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (12)Delete specific blog  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/delete-blog/<key>")
def delete_blog(key):
    # key is combinition of weed class and blog key
    if 'useremail' in session:
        index1 = key.index('-')
        subject = key[0:index1]
        key1 = key[index1:]
        subkey = db.child('Library').child('Weed_classes').child(subject + "").child(key1 + "").get()
        subkey = subkey.val()['blog']
        db.child('Library').child('blogs').child(subkey + "").remove()
        db.child('Library').child('Weed_classes').child(subject + "").child(key1 + "").remove()
    return redirect(url_for('profile'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (13)Add New Blog <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/add_blog", methods=['POST', 'GET'])
def add_blog():
    if 'useremail' in session:
        if request.method == "POST":
            weed_class = request.form.get('weed_class')
            title = request.form['title']
            cover_image = request.files['cover_image']
            date = request.form['date']
            blog_body = request.form['blog_body']
            index1 = session['useremail'].index('@')
            key = session['useremail'][0:index1]
            myfilename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(app.config['UPLOAD_FOLDER'], myfilename))
            blog = {
                "editor": key,
                "title": title,
                "date": date,
                "image": myfilename,
                "blog_body": blog_body
            }
            index1 = session['useremail'].index('@')
            key = session['useremail'][0:index1]
            # generate some integers
            S = 20
            ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
            db.child('Library').child('blogs').child(str('-' + ran)).set(blog)
            blog2 = {
                "editor": key,
                "title": title,
                "date": date,
                "image": myfilename,
                "blog_body": blog_body,
                "blog": str(ran)
            }
            db.child('Library').child('Weed_classes').child(weed_class).push(blog2)
            return redirect(url_for('profile'))

        # all classes of weeds
        weed_classes = []
        data = db.child('Library').child('classes').get()
        for i in data.each():
            weed_classes.append(i.key())

        # the classes where i have upload blogs
        index1 = session['useremail'].index('@')
        key = session['useremail'][0:index1]
        weed_classes_posted = []
        # all classes of weeds
        data = db.child("Library").child('Weed_classes').get()
        for i in data.each():
            db1 = db.child("Library").child('Weed_classes').child(i.key()).get()
            for j in db1.each():
                if j.val()['editor'] == key:
                    weed_classes_posted.append([i.key(), len(i.val())])
                    break
        data = db.child("Bio_researcher").child(key).child(key + "1").get()
        values = data.val()
        print(weed_classes_posted)
        return render_template('Bio_researcher/add_blog.html', user_data=values, classes=weed_classes,
                               blogs_classes=weed_classes_posted, user_id=key)
    return render_template('Bio_researcher/index.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> Show weed class description  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#

@app.route("/weedClass/<weedclass>")
def weed_class(weedclass):
    return render_template('Bio_researcher/weed_class.html', weed=weedclass)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> Weed Classification Model  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.inception_v3 import preprocess_input


@app.route("/classifier", methods=['POST', 'GET'])
def classifier():
    if request.method == 'POST':
        file = request.files['input_img']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpg'))
        image = load_img(app.config['UPLOAD_FOLDER'] + '/' + 'image.jpg', target_size=(299, 299))

        image = img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = preprocess_input(image)
        yhat = model.predict(image)
        if np.max(yhat) < 0.3:
            output = weeds_list[2]
        else:
            output = weeds_list[np.argmax(yhat)]
        description = " nothing"
        links = "not available"
        if db.child('Library').child('classes').child(output).child('description').get().val():
            description = db.child('Library').child('classes').child(output).child('description').get().val()
        if db.child('Library').child('Weed_classes').child(output).get().val():
            links = db.child('Library').child('Weed_classes').child(output).get()
        return render_template('classifier/index.html', filename='image.jpg', desc=description, links=links,
                               weedclass=output)
    return render_template('classifier/index.html', filename="null", desc="null", links="not available")


@app.route('/back_to_classifier')
def back_to_classifier():
    return redirect(url_for('classifier'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#       >>>>>>>>>>>>>> ADMIN PORTION <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (1) admin index page  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin")
@app.route("/admin/index")
def admin_index():
    if 'adminemail' in session:
        list = []
        blogs = db.child("Library").child("blogs").get().val()
        list.append(len(blogs))
        researcher = db.child("Bio_researcher").get().val()
        list.append(len(researcher))
        weeds = db.child("Library").child("classes").get().val()
        list.append(len(weeds))
        admins = db.child("Admin").child('iqbal12').child('sub_admin').get().val()
        list.append(len(admins))
        weeds_classes = db.child('Library').child("classes").get()
        admins = db.child("Admin").child('iqbal12').child('sub_admin').get()
        weeds_list = ['Chinee apple', 'Lantana', 'Parkinsonia', 'Parthenium', 'Prickly acacia', 'Rubber vine',
                      'siam weed', 'Snake weed']
        count_blog = []
        for i in weeds_list:
            if db.child("Library").child('Weed_classes').child(i + "").get().val():
                count_blog.append(len(db.child("Library").child('Weed_classes').child(i + "").get().val()))
            else:
                count_blog.append(0)

        data = {'Task': 'Hours per Day', 'Chinee apple': count_blog[0], 'Lantana': count_blog[1],
                'Parkinsonia': count_blog[2], 'Parthenium': count_blog[3], 'Prickly acacia': count_blog[4],
                'Rubber vine': count_blog[5], 'siam weed': count_blog[6], 'Snake weed': count_blog[7]}
        return render_template('admin/index.html', records=list, weed_classes=weeds_classes, admins=admins, data=data,
                               data1=data)
    return render_template('admin/login.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (2) admin Login  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin/login", methods=['POST', 'GET'])
def admin_login():
    if 'adminemail' in session:
        return redirect(url_for('admin_index'))
    if request.method == 'POST':
        try:
            useremail = request.form['useremail']
            password = request.form['password']
            auth.sign_in_with_email_and_password(useremail, password)
            session['adminemail'] = useremail
            return redirect(url_for('admin_index'))
        except:
            flash('Eamil or password is wrong!', 'success')
            return redirect(url_for('admin_login'))
    return render_template('admin/login.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (3) admin Signup (super role and 1 time)  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin/signup", methods=['POST', 'GET'])
def admin_signup():
    if 'adminemail' in session:
        return redirect(url_for('admin_index'))
    if request.method == 'POST':
        username = request.form['username']
        useremail = request.form['useremail']
        password = request.form['password']
        login = auth.create_user_with_email_and_password(useremail, password)
        user = {
            "username": username,
            "email": useremail,
            "password": password,
            "role": 'super'
        }
        index1 = useremail.index('@')
        key = useremail[0:index1]
        db.child('Admin').child(key).update(user)
        # auth.send_email_verification(login['id_token'])
        flash(username + ' Added successfully!. Please Login', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin/admin_account.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (3) View Profile  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin/profile")
def admin_profile():
    if 'adminemail' in session:
        # email address just name
        index1 = session['adminemail'].index('@')
        key = session['adminemail'][0:index1]
        if db.child("Admin").child(key).get().val():
            data = db.child("Admin").child(key).get()
        else:
            data = db.child("Admin").child("iqbal12").child("sub_admin").child(key).get()
        return render_template('admin/profile.html', profile=data)
    return render_template('admin/profile.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (4) Update Profile  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/profile_update', methods=['POST', 'GET'])
def profile_update():
    if 'adminemail' in session:
        if request.method == 'POST':
            username = request.form['username']
            city = request.form['city']
            country = request.form['country']
            address = request.form['address']
            aboutme = request.form['aboutme']
            index1 = session['adminemail'].index('@')
            key = session['adminemail'][0:index1]
            user = {
                'username': username,
                'city': city,
                'country': country,
                'address': address,
                'aboutme': aboutme

            }
            db.child("Admin").child(key).update(user)
        return redirect(url_for('admin_profile'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (5) add new modrator page  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin/add_new")
def add_admin():
    if 'adminemail' in session:
        index1 = session['adminemail'].index('@')
        key = session['adminemail'][0:index1]
        data = db.child("Admin").child(key).get()
        return render_template('admin/add_admin.html', profile=data)
    return render_template('admin/profile.html')


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (6) add new modrator form submit here  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/New_admin', methods=['POST', 'GET'])
def New_admin():
    if 'adminemail' in session:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            username = request.form['username']
            city = request.form['city']
            country = request.form['country']
            address = request.form['address']
            aboutme = request.form['aboutme']
            auth.create_user_with_email_and_password(email, password)
            index1 = session['adminemail'].index('@')
            key = session['adminemail'][0:index1]
            user = {
                'username': username,
                'city': city,
                'country': country,
                'address': address,
                'aboutme': aboutme,
                'role': 'junior',
                'email': email,
                'password': password
            }
            index2 = email.index('@')
            key2 = email[0:index2]
            db.child("Admin").child(key).child("sub_admin").child(key2).update(user)
        return redirect(url_for('admin_profile'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (7) Logout admin  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route('/admin/logout')
def admin_logout():
    session.pop('adminemail', None)
    return redirect(url_for('admin_index'))


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (8) View all botanists  <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/admin/Botanists")
def Botanist_list():
    if 'adminemail' in session:

        Botanists_data = []
        keys_botanists = []
        x = []
        Botanists = db.child("Bio_researcher").get()
        zip1 = zip(x, Botanists.each())
        classes = db.child('Library').child('Weed_classes').get()
        for k in Botanists.each():
            keys_botanists.append(k.key())
            count = 0
            for i in classes.each():
                first1 = db.child('Library').child('Weed_classes').child(i.key() + "").get()
                for j in first1.each():
                    first2 = db.child('Library').child('Weed_classes').child(i.key() + "").child(j.key() + "").get()
                    values = first2.val()
                    if k.key() == values['editor']:
                        count += 1
            x.append(count)
        print(x)
        v = 0
        for i in zip1:
            Botanists_data.append(
                [keys_botanists[v], list(i[1].val().values())[0]['username'], list(i[1].val().values())[0]['email'],
                 x[v]])
            # print(list(i[1].val().values())[0]['email'])
            v += 1
        for i in Botanists_data:
            print(i)
    return render_template('admin/Botanists.html', botanists=Botanists_data)


# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
#  >>>>>>>>>>>>>> (9) Delete Botanists <<<<<<<<<<<<<<<<<
# **************>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<****************#
@app.route("/delete_botanists/<bts>")
def delete_bts(bts):
    db.child('Bio_researcher').child(bts).remove()


# **********>>>>>>>>>>>>>><<<<<<<<<<**************
#  >>>>>>>>>>>>>>>(10) Show all classes <<<<<<<<<<<<<<<
# **********>>>>>>>>>>>>>><<<<<<<<<<**************
@app.route("/admin/weed_classes")
def weed_classes():
    if 'adminemail' in session:
        weeds = db.child("Library").child("classes").get()
    return render_template('admin/weed_classes.html', weeds=weeds)


# **********>>>>>>>>>>>>>><<<<<<<<<<**************
#  >>>>>>>>>>>>>>> (11) View Weed Classes<<<<<<<<<<<<<<<
# **********>>>>>>>>>>>>>><<<<<<<<<<**************

@app.route("/view_weed/<weed>")
def view_weed(weed):
    if 'adminemail' in session:
        weed_detail = db.child("Library").child("classes").child(weed).get()
        blog_list = "empty"
        if db.child("Library").child("Weed_classes").child(weed).get().val():
            blog_list = db.child("Library").child("Weed_classes").child(weed).get()
        return render_template('admin/weed_details.html', weed_detail=weed_detail, blog_list=blog_list)
    return render_template('admin/login.html')


# **********>>>>>>>>>>>>>><<<<<<<<<<**************
#  >>>>>>>>>>>>>>> (12) update Weed<<<<<<<<<<<<<<<
# **********>>>>>>>>>>>>>><<<<<<<<<<**************

@app.route('/update_weed', methods=['POST', 'GET'])
def update_weed():
    if 'adminemail' in session:
        if request.method == 'POST':
            description = request.form['description']
            class1 = request.form['class']
            class2 = {
                'description': description
            }
            db.child("Library").child("classes").child(class1).update(class2)
        return redirect(url_for('weed_classes'))


# **********>>>>>>>>>>>>>><<<<<<<<<<**************
#  >>>>>>>>>>>>>>> (13) Weed Blogs<<<<<<<<<<<<<<<
# **********>>>>>>>>>>>>>><<<<<<<<<<**************
@app.route("/admin/blogs")
def blogs_list():
    blogs = db.child('Library').child('blogs').get()
    return render_template('admin/blogs.html', blogs=blogs)

