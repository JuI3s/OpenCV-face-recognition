#Initialise the main web forms to be used in the project 

# import web form modules
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

# form the database model import the User and Face table 
from app.models import User, Face

#from the login module import the current user feature 
from flask_login import current_user 

#import the regular expression module
import re 

def check_valid_name(name):
    reg = re.compile(r"[a-zA-Z ,'.-]+")
    # regular expression to match any full name 
    m = reg.match(name) 
    if m == None:
        # The name format match is not valid if the match m is None or
        return False
    else:
        start, stop = m.span()
        if stop - start != len(name):
            # ff stop - start != len(name) then the regex is only matched to part of the string, hence not a valid name
            return False
    return True 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    #The passworkd needs to be entered twice and compared such that they are the same before registration is allowed to complete
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')
        if check_valid_name(username.data) == False: 
            raise ValidationError('Username not in the correct format')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddFaceForm(FlaskForm):
    face = StringField("Name of the person", validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_face(self, face):
        faces = Face.query.filter_by(user = current_user)
        if check_valid_name(face.data) == False: 
            raise ValidationError('Name of the face not in the correct format.')
        for each in faces: 
            if each.name.lower() == face.data.lower():
                raise ValidationError('A person has already been added with the same name.') 

class EnableFaceLogin(FlaskForm):
    enable = BooleanField("Enable login with facerecognition", validators=[DataRequired()])
    submit = SubmitField('Confirm')