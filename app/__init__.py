#Initialise key processes in the project

#Import the flask framework 
from flask import Flask
#import the sqlalchemy database modle
from flask_sqlalchemy import SQLAlchemy
#import the database migration feature
from flask_migrate import Migrate
#import the login manager for handling user login 
from flask_login import LoginManager
#from the configuration file import the Config object
from config import Config
import sys

#Configure the path to import modules from
sys.path.insert(1, '.')

#Initialise the flask application object 
app = Flask(__name__)

#Configuring the flask application from the Config class in config.py 
app.config.from_object(Config)

#Initialising the sqlalchemy database object
db = SQLAlchemy(app)

#initialising sqlalchemy database migration 
migrate = Migrate(app, db)

#Initialising flask application login manager object
login = LoginManager(app)

#Setting the login vide. The user is redirected to the page set automatically if the current user is not authenticated, i.e. if the user is not logged in
login.login_view = 'login'

#import routes.py and models.py and complete the initialisation processes 
#Only able to import the two modules after the above configurations are complete 

#import the files "routes" and "models"
import routes, models