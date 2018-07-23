import os
basedir = os.path.abspath(os.path.dirname(__file__))
#Base directory path set up for the database

class Config(object):
	#Set up the secret key used for password hashing in Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
    #Set up the url forFlask SQLalchemy database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    #Set sqlalchemy_track_modifications as False. 
    #If the attribute is set true, then a notification is flashed every time changes are made to the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #Set the database path
    DATABASE_PATH = ''
    #Set up the path where the training folers and images are stored 
    TRAINING_DATA = 'app/training_data/'
