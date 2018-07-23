from importlib import import_module
from flask import render_template, flash, redirect, url_for, request, Response 
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db #from __init__.py import moduels named app, db
from app.models import db, User
from app.forms import LoginForm, RegistrationForm, AddFaceForm
from app.models import User, Face, Access
from face_recognition import live_recognition, classifier_training, live_add_face, video_stream
from face_recognition import FaceLogin
import os
import string 
import threading
import time
import cv2
from cv2 import face

#In the file, @app.route('path/<optional parameters>') is a web dectorator, meaning that the function defined and wrapped within it will 
#only get executed when the corresponding link is directed to the url specified by 'path'
# @login_required means that the function it wraps will only get executed when the current user is logged in 
# render_template is a FLASK statement to render HTML templates on the web page 
# url_for('url') directs the current web page to the url specified by 'url'

facelogin = FaceLogin()
Config = import_module('app.config').Config
TRAINING_DATA = Config.TRAINING_DATA

def check_new_face_name_valid(path):
    #Check that the uniquessness condition for face paths is validated
    #before adding a new face
    isValid = True
    faces = Face.query.filter_by(user = current_user).all()
    for face in faces:
        if face.path == path:
            isValid = False 
    return isValid

def check_face_login_condition(users): 
    for user in users:
        #Check that the path exists
        if os.path.exists(user.login_path) != True: 
            user.login_enabled = False
            user.login_path = ""
            users.remove(user)
        #Check there are a set number of pictures in each directory
        elif len(os.listdir(user.login_path)) == 0:
            user.login_enabled = False
            user.login_path = ""
            users.remove(user)
    return users

def name_to_path(name): 

    #Generate a name path for a new user
    #The path contains only lower case letters joined by "_"
    #Example output: Test User --> test_user/

    to_array = name.lower().split()
    path = to_array[0]
    to_array.pop(0)
    for each in to_array:
        path = path + '_' + each
    path = path + '/'
    return path

def path_to_name(path):

    #Take in a file string in the format test_user/
    #Output Test User

    to_array = name.split('_')
    name - to_array[0].capitalize()
    to_array.pop(0)
    for each in to_array:
        name = name + " " + each.capitalize()
    return name

#Clear all the training images in a directory and delete the directory
def clear_directory(face):

    folder = TRAINING_DATA + name_to_path(current.username) + face.path
    files = [each for each in os.listdir(folder)]
    for each in files:
        os.remove(os.path.join(folder, each))
    os.rmdir(folder)

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("New user created correctly.")
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route('/recognition')
@login_required
def recognition():
    mode = 'recognition'
    path = 'None'
    #mode = 'addface'   #this doesn't work
    #path = 'app/training_data/user/test'

    if current_user.is_anonymous:
        return redirect(url_for('index'))
    # No path set if in recognition mode. 
    return render_template('video.html', mode=mode, path=path, FaceLogin = 'None')

@app.route('/videostream')
def videostream(): 
    mode = 'video'
    path = 'None'
    return render_template('video.html', mode=mode, path = path, facelogin = 'None')

@app.route('/face_login_page/<facelogin>')
def face_login_page(facelogin):
    mode = 'facelogin'
    path = "None"
    return render_template('video.html', mode=mode, path=path, facelogin = facelogin)

@app.route('/face_login_data')
def face_login_data(): 
    users = User.query.filter_by(login_enabled = True).all()
    users = check_face_login_condition(users)
    if users == []:
        flash("Face recognition has not been enabled for any user.")
        return redirect('index')
    facelogin.users = users

    #Assigning to facelogin attributes to prepare for training the classifier
    for i, user in enumerate(users): 
        facelogin.face_label.append(user.login_path)
        for image in os.listdir(user.login_path):
            facelogin.images.append(cv2.imread(user.login_path + '/' + image, 0))
            facelogin.labels.append(i)

    print facelogin.face_label 
    print len(facelogin.images)
    return redirect(url_for('face_login_page', facelogin = facelogin))

@app.route('/login_face')
def login_face():
    if len(User.query.filter_by(login_enabled = True).all()) == 0:
        flash("Face login not enabled for the user. Please go to the setting to enable face login.")
    else: 
        if facelogin.login == True:
            login_user(facelogin.user)
            #Clear the face login user as the last user has been logged in
            facelogin.login = ""
        else:
            flash("Face login criterion not met.")
    return redirect(url_for('index'))

@app.route('/add_face', methods = ['GET', 'POST'])
@login_required
def add_face(): 
    if current_user.is_anonymous:
        return redirect(url_for('index.html'))
    
    form = AddFaceForm()

    if form.validate_on_submit():
        mode = 'addface'

        user_name = current_user.username
        face_name = form.face.data

        user_name_path = name_to_path(user_name)
        face_name_path = name_to_path(face_name)

        if check_new_face_name_valid(face_name_path) != True:
            flash("A person with the same name has already been added for the user.")
            flash("Please try with a different name.")
            return redirect(url_for('add_face'))
        else:
            #Create a new path of the directory to store training images for the added face
            path = TRAINING_DATA + user_name_path + face_name_path
            print(path)

            face = Face(name=form.face.data, user=current_user, path = face_name_path)
            db.session.add(face)
            db.session.commit()

            if not os.path.exists(path):
                os.makedirs(path)     
            flash('New face added successfully.')
            #Should be displayed after adding the face has been finished

            return render_template('video.html', mode = mode, path = path)

    return render_template('add_face.html', form=form)

@app.route('/video_feed/<mode>/<path:path>', methods=['GET', 'POST'])
def video_feed(mode, path):
    #Clearning up the arguments!
    if mode == "recognition":
        print(current_user)
        print("\n")
        print(type(current_user))
        print("\n")

        path = TRAINING_DATA + name_to_path(current_user.username)
        detector, recogniser, face_label = classifier_training(path, current_user.shape)
        user_id = current_user.id
        return Response(live_recognition(detector, recogniser, face_label, user_id, current_user.shape),
            mimetype='multipart/x-mixed-replace; boundary=frame')
    elif mode == 'videostream':
        return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif mode == 'addface':
        return Response(live_add_face(path, current_user.shape, current_user.num_to_add), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif mode == "facelogin": 
        return Response(facelogin.face_recognition_login(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats', defaults={'name': None})
@app.route('/stats/<name>')
@login_required
def stats(name):
    if name == None:
        single_person = False
        face_list = Face.query.filter_by(user = current_user).all()
        face = []
        access = {}

        for each in face_list:
            face.append(each.name)
            ls = Access.query.filter_by(which_face = each).all()
            temp = [each_access.accesstime for each_access in ls]
            access[each.name] = temp
    else: 
        single_person = True
        #Access the face object
        face_ = Face.query.filter_by(user = current_user, name = name).first()
        face = face_.name
        access_ = Access.query.filter_by(which_face = face_).all()
        access = []
        for each in access_:
            access.append(each.accesstime)

    print "single_person", single_person
    return render_template('stats.html', face = face, access = access, single_person = single_person)

@app.route('/list_face/<mode>')
@login_required
def list_face(mode):
    face_list = Face.query.filter_by(user = current_user).all()
    face = []
    for each in face_list:
        face.append(each.name)

    return render_template('list_face.html', face = face, mode = mode)

@app.route('/setting')
@login_required
def setting():
    return render_template('setting.html', user = current_user)

@app.route('/add_user_face')
def add_user_face():
    user_name = current_user.username
    user_name_path = name_to_path(user_name)
    folder = TRAINING_DATA + user_name_path + user_name_path

    if os.path.exists(folder):
        pass
    else: 
        print "User login with face recognition not activated yet"
    return render_template('add_user_face.html')

@app.route('/enable_face_login')
@login_required
def enable_face_login():
    mode = "addface" 
    if current_user.login_enabled == True:
        flash("Face Recognition Login has already been enabled.")
        return redirect(url_for('index'))
    else:
        name = current_user.username
        user_label = name_to_path(name)
        path = TRAINING_DATA + user_label + user_label

        current_user.login_enabled = True
        current_user.login_path = path
        face = Face(name = current_user.username, path = current_user.login_path, user = current_user)
        db.session.commit()

        #First user_label refers to the user folder 
        #Second user_label refers to an inner directory containing images of the user.
        if not os.path.exists(path):
            os.makedirs(path)
            print("Directory added.")
            return render_template('video.html', mode = mode, path = path)
        else:
            print "Face recognition login enabled."
            return redirect(url_for("index"))

@app.route('/delete_all_faces')
@login_required
def delete_all_faces(): 
    for face in Face.query.filter_by(user = current_user).all():
        for access in Access.query.filter_by(which_face = face).all():
            db.session(access)
        db.session.delete(face)
    db.session.commit()
    flash("Face directory cleared for this user.")
    return render_template('setting.html')

@app.route('/change_shape')
@login_required
def change_shape(): 
    if current_user.shape == 'rectangle': 
        current_user.shape = 'ellipse'
    elif current_user.shape == 'ellipse':
        current_user.shape = 'rectangle'
    else: 
        current_user.shape = 'rectangle'
        flash("The shape attribute for the current user was not valid. It has now been set to the default value: rectangle")
    db.session.commit()
    return render_template('setting.html', user = current_user)

#Asks the user to confirm the decision before removing a face from the database
@app.route('/remove_face_confirmation/<name>')
@login_required
def remove_face_confirmation(name):
    return render_template('remove_face_confirmation.html', name = name)

@app.route('/remove_face/<name>')
@login_required
def remove_face(name):
    #Remove the face object from the database and the corresponding folder that contains training images
    face = Face.query.filter_by(name = name).first() 
    db.session.delete(face)
    db.session.commit() 
    clear_directory(face)
    flash("Face removed correctly.") 
    return redirect(url_for('setting'))