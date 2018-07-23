from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import time 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    login_enabled = db.Column(db.Boolean(), default = False)
    login_path = db.Column(db.String(64), default = "")
    shape = db.Column(db.String(64), default = "rectangle")
    num_to_add = db.Column(db.Integer, default = 20)
    faces = db.relationship('Face', backref='user', lazy='dynamic')
    #lastseen = db.Column(db.DateTime, index = True, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
 
 #loader function required for flask to log in a user.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Face(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index=True )
    path = db.Column(db.String(20))
    access = db.relationship('Access', backref='which_face', lazy='dynamic')
    whichuser = db.Column(db.Integer, db.ForeignKey('user.id'))

class Access(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    accesstime = db.Column(db.String(64), index = True)
    whose = db.Column(db.Integer, db.ForeignKey('face.name'))