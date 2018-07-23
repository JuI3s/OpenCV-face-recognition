#!/usr/bin/env python

#import tiem libraries for updating access time records
import time
from datetime import datetime

#sys and os libraries used for saving files
import sys
import os

#import cv2 library for face detection and recognition
import numpy
import cv2 
from cv2 import face
#__version__ allows one to check the version of the cv2 library
from cv2 import __version__

#import library files for initialising face detectors, video capture objects, image operation features and access record updating features
from detectors import FaceDetector 
import video_capture
import operations as op
from stats import Update 

#numpy used for handling numpy array type images
import numpy as np

#import_module used for importing a module from another file
from importlib import import_module

#import the flask framework
from flask import Flask

#from app (an isntance of a flask application) import thedatabase model
from app import app, db
from app.models import db, User, Face, Access 

#import flask login features
from flask_login import login_user, logout_user, current_user, login_required
#import flask web rendering features 
from flask import render_template, flash, redirect, url_for, request, Response 

import string 

Config = import_module('app.config').Config
TRAINING_DATA = Config.TRAINING_DATA

def name_to_file(name):
	#Fuction: Convert a name to its corresponding path form
	#Parameters: name, string type, representing the name to convert 
	#Return: file, string type. All the capital letters in name are replaced
	#by lower case letters and spaces replaced by '_'
	#e.g. A user with userna

	to_array = name.split()
	file = to_array[0]
	to_array.pop(0)
	for each in to_array:
		file = file + '_' + each
	file = file + '/'
	return file
	
def print_all_users(path): 
	#Parameter: path, string type, pointing to the directory which stores face directories, 
	#each of which contains training images for race recognition
	try:
		people = [person for person in os.listdir(path)]
	except:
		print("There seems to be no person in the database")
		sys.exit()
	for file in people:
		# .DS_Store exists in folders in OS system which affect the running of the program
		# .DS_Store contains metadata about the folder
		if file == '.DS_Store':
			people.remove(file)

	print('Users in the databaes')

	# print each name in its normal format 

	for file in people:
		print(print_name(file))

def print_name(file):
	#Parameter: file, string type, value returned by the name_to_file function
	#This is basically the reverse of name_to_file 
	#Converts the path to a name. The first letter in a word is converted to 
	#a capitable letter. '_' is replaced by a space character 
	name = ''
	spl = file.split("_")
	for each in spl: 
		name = name + each.capitalize() + " "
	return name

def get_image(frame, face_coord, shape):
	#Get face images from live stream
	#Parameters: frame, numpy array type, an image of a frame in the video stream
	#face_coord, numpy array type, representing the position of the detected face
	#shape, string type, representing how the detected face will be indicated
	#Using image manipulation functions imported from operations.py 
	#Return values: frame, numpy array tpye image, current frame in the video streawm 
	#face_image: numpy type arrays containing all the images of the regions where faces are detected

	if shape == 'rectangle':
		face_image = op.cut_rectangle(frame, face_coord)
		frame = op.draw_face_rectangle(frame, face_coord)
	elif shape == 'ellipse':
		face_image = op.cut_ellipse(frame, face_coord)
		frame = op.draw_face_ellipse(frame, face_coord)
	face_image = op.normalise_intensity(face_image)
	face_image = op.resize(face_image)
	return (frame, face_image)

def live_add_face(path, shape, num_to_add): 
	#Paramerers: path, string type, relative path of the directorty where the trainign images are about to be stored 
	#shape, string type, values taken from 'rectangle' or 'ellipse', how a detected face is going to be highlighted in a frame of the video stream 
	#num_to_add, int, number of training images to be taken for each new face.

	#initialise the frontal face detector
	detector = FaceDetector('app/frontal_face.xml')
	#Initialising the video camera object
	vid = video_capture.VideoCamera()
	#couter: keep track of the number of training images that have been taken 
	counter = 1
	#timer: used to  record the number of seconds passe after the adding face procedure begins 
	#only  take add new training image every ten seconds to avoid adding too many new images in a very short time
	timer = 0
	while counter <= num_to_add: 
		frame = vid.get_frame()
		face_coord = detector.detect(frame)
		if len(face_coord):
			#If there is a face detected
			frame, face_image = get_image(frame, face_coord, shape)
			#frame is the current frame for the video stream 
			#face_image is the image of the region in which the face is detected
			if timer % 10 == 5:
				cv2.imwrite(path + '/' + str(counter) + '.jpg', face_image[0])
				#Save file to directory specified the name of the face to be added
				print("Image save: " + str(counter))
				counter = counter + 1;
				cv2.putText(frame, "Number of pictures taken: " + str(counter), (5, frame.shape[0] - 5),
				cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)		
				#show the user the number of pictures that have been taken
				cv2.imshow("Saved face", face_image[0])
			if counter >= num_to_add: 
				cv2.putText(frame, "Adding new face complete. " + str(counter), (5, frame.shape[0] - 5),
				cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)	

		#create the jpeg encoding of the frame
		encode = cv2.imencode('.jpg', frame)[1].tobytes()
		#Yield the encoding
		#yield means the function is a python generator object.
		#A generator object is taken as an argument in flask Response() to render video streaming 
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')		
		timer = timer + 5

def video_stream():
	#This is a generator object that returns the encodings of frames taken directly from the camera 

	vid = video_capture.VideoCamera()
	while True:
		frame = vid.get_frame()
		encode = cv2.imencode('.jpg', frame)[1].tobytes()
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')		


def classifier_training(PEOPLE_PATH, shape):
	#training an opencv face recognition cklassifier 
	#Parameters: PEOPLE_PATH, string type, path of the directory for the current user that stores all the face foldersteach of which contains training images for a face
	#Shape: same as in referred to in the functios above
	#Return values: face_detector, opencv object, a detector that detects faces in an image 
	#recogniser, opencv object, a recogniser that recognises detected faces 
	#face_label, list type, an array of the labels of all the faces the recogniser that recognise

	try:
		#creating an array people of all the file names in the PEOPLE_PATH directory. 
		#PEOPLE_PATH is a string varialble that is also a path of the directrory where the training images for a user are stored
		people = [person for person in os.listdir(PEOPLE_PATH)]
		#In Mac, by defaul the system creates a file called DS.Store to store metadata. This is not a directory that we can access
		for file in people:

		# .DS_Store exists in folders in OS system which affect the running of the program
		# .DS_Store contains metadata about the folder
			if file == '.DS_Store':
				people.remove(file)
	except:
		#If there is no person directory in the folder, then opencv will raise a runtime error
		print("There seems to be no person in the database")
		sys.exit()
	
	#initialise face detector
	#Type: opencv object that detects faces in a given iamge
	#Return: coordinates of the face if detected

	#Initialising an opencv frontal face detector
	#frontal_face.xml is a xml file provided opencv that links to the frontal face detector in the cv2 library
	face_detector = FaceDetector('app/frontal_face.xml')
	face_detector.__init__

	#initialise face recogniser 
	#Type: open cv object that compares detected faces to the face encodings of the known people in the dataset
	#Return: Prediction (string), accury(double)
	#EigenFaceRecognizer is based on a face detection algorithm provided by opencv 
	#Threshold: minimium number required for faces detected in the neighbour hood.

	recogniser = cv2.face.LBPHFaceRecognizer_create()
	threshold = 105

	#sample from images from the dataset for the classifier training

	#Images: list containg all the training images to be used for face recognition classifier training
	#Each image element has a corresponding label in the labels list
	images = []

	#Labels: list containing all the labels for the images. 
	#Each label indicates which user the image belongs to
	labels = []
	person_label = []

	#face_label: list type, containing all the paths of the people whose faces have been added for the current user
	face_label = []
	for i, person in enumerate(people):
		face_label.append(person)
		for image in os.listdir(PEOPLE_PATH + person):
			images.append(cv2.imread(PEOPLE_PATH + person + '/' + image, 0))
			labels.append(i)
		person_label.append(person)

	try:
		#opencv function to train the recogniser
		#parameters: images, numpy array list type, l
		#labels, list type, storing the labels of the face in each training image, i.e. whose face it belongs to

		recogniser.train(images, np.array(labels))
		print "classifer trained on: ", person_label
	except: 
		#Opencv training requirement
		print("At least two people are needed")
		sys.exit()

	return (face_detector, recogniser, face_label)

def live_recognition(detector, recogniser, face_label, user_id, shape):
	#recognise from video frames 
	#Parameters: detector, same as the returned value detector from the classifier_training function 
	#recogniser, same as the returned value detector from the classifier_training function 
	#face_laberl, same as the returned value detector from the classifier_training function 
	#user_id, int type, ID of the current user 
	#shape, same as shape referred to in the section above 

	#Minium confidence score returned by recogniser.predict that signifies a face has been recognised correctly. 
	threshold = 95
	vid = video_capture.VideoCamera()
	print('\n')
	#Initialise an update object to keep updating the access time information for each face 
	update = Update(face_label)

	#Creating an array to store access time information for each user.
	access_time = []
	for i in range(len(face_label)):
		access_time.append(" ")

	update = Update(face_label)

	while True:
		frame = vid.get_frame()
		frame1 = frame
		#detect all the people in the frame 
		coord = detector.detect(frame, False)
		frame, face_image = get_image(frame, coord, shape)
		for i, image in enumerate(face_image):
			pred, error = recogniser.predict(image)
			#Returning a prediction value that corresponds to the element in the face_label array
			#and an error showing the precision of the prediction
			#Running the code below during the development stage to check thisw works
			#print "Prediction: " +  face_label[pred] + " Error: " + str(round(error)) + " Accuracy threshold: " + str(threshold)
			print_label = print_name(face_label[pred])
			#Returning the name of the person detected. 
			# The element in face_label is part of the directory file storing training images for the person

			if error > threshold: 
				#The face is not recognised. Precision too low.  
				cv2.putText(frame, 'Unknown face', (coord[i][0], coord[i][1]), 
					cv2.FONT_HERSHEY_PLAIN, 1.7, (206, 0, 209), 2,
					cv2.LINE_AA)
			else:
				# Update 
				cv2.putText(frame, print_label,
					(coord[i][0], coord[i][1] - 2),
					cv2.FONT_HERSHEY_PLAIN, 1.7, (206, 0, 209), 2,
					cv2.LINE_AA)
				update.add_identified(pred)
				if update.is_first_access(pred): 
					#First access time is now
					time = datetime.now()
					#Update first access time to database
					first_access = 'First access: ' + time.strftime("%H:%M:%S, %d-%m-%Y") + " "
					access_time[pred] = first_access

			for index in update.is_last_access(): 
				#Returning indice of last accessed faces 
				#update last access time to database

				if access_time[pred] != " ":
					time = datetime.now()

					last_access = ' Last access:' + time.strftime("%H:%M:%S, %d-%m-%Y")
					#For each face for which last access is detected, access_time[pred] should contain the first access time as referred to above
					access_time[pred] = access_time[pred] + last_access
					#get the path of the face for searching the corresponding face object
					path = face_label[pred] + "/"
					#Convert to unicdoe
					path = path.encode("utf-8")

					#get the current user
					user = User.query.filter_by(id = user_id).first()
					#get the face object whose access attribute is to be updated 
					face = Face.query.filter_by(user = user, path = path).first()

					#Update the access attribute and commit the change to database
					access = Access(accesstime = access_time[pred], which_face = face)
					db.session.add(access)
					db.session.commit()
					print "new access added"
					access_time[pred] = " "

			#Refresh the frames as a frame has passed
			update.shift_frames()
			update.clear_current_frame()

			cv2.putText(frame, "Press ESC to to go back to the menu", (5, frame.shape[0] - 5),
				cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)

			#cv2.imshow('frame', frame)
		encode = cv2.imencode('.jpg', frame1)[1].tobytes()
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')			

class FaceLogin(): 
	#A FaceLogin class to handle face recognition login 

	def __init__(self):
		self.login = False  	
		#If set True then log in the user
		self.user = ""
		#Assigned to a User object if face recognition login confirmed for one user 
		self.users = [] 
		#list of users for whom face recognition login has been enabled
		self.images = [] 
		#List of training images for face recognition login
		self.face_label = []
		#list of the paths of the face directories for each user 
		self.labels = []
		#list that contain information about which image in self.images belong to which user
		#Each entry is an int type variable that indicates the index of the user

	def face_recognition_login(self, SHAPE = 'rectangle', DURATION = 30, NUM_TO_TAKE = 5): 
		start = time.time()
		threshold = 95
		user_label = ""
		#user_label, string type, records the face path of the user who has been detected and is considered for login

		users = User.query.filter_by(login_enabled = True).all()
		#get all the users for whom face recognition login has een enabled

		detector = FaceDetector('app/frontal_face.xml')
		recogniser = cv2.face.LBPHFaceRecognizer_create()
		vid = video_capture.VideoCamera()
		recogniser.train(self.images, np.array(self.labels))

		count = 0
		timer = 0
		while count <= NUM_TO_TAKE and time.time() - start < DURATION + 5: 
			#checking for face recognition login if the set number of face pictures required for logging a user have not been detected yet and
			#the amount of time elapsed since the start is less than the required duration 
				
			frame = vid.get_frame()
			face_coord = detector.detect(frame)

			if len(face_coord) and time.time() - start < DURATION:
				#if there is a face detected 

				timer = timer + 1
				frame, face_image = get_image(frame, face_coord, SHAPE)
				image = face_image[0]
				#face_image[0] since we are only logging one user 
				pred, error = recogniser.predict(image)
			
				if timer % 3 == 2: 
					#Updating every three frames in which a face is recognised. 
					if error < threshold: 
						if user_label == "":
							user_label = self.face_label[pred]
						if user_label != self.face_label[pred]:
							count = 0
							user_label = self.face_label[pred]
						#add the label for the current user.
						#If the length of the user label is 0 then add the first picture
						else:
							count = count + 1
							print "detected: ", self.face_label[pred]
							print self.face_label

			hight, width, channel = frame.shape
			cv2.rectangle(frame, (22, 22), (22 + count * 30, 26), (206, 0, 209), 4)
			cv2.rectangle(frame, (20, 20), (20 + NUM_TO_TAKE * 30, 30), (206, 0, 209), 2)
			cv2.putText(frame, "Login check complete: " + str(count) + "/" + str(NUM_TO_TAKE), (5, 60),
				cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)		
			if count >= NUM_TO_TAKE:
				cv2.putText(frame, "Login criterions satisfied." , (5, 120), cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)	
				cv2.putText(frame, "Please click the Login Face button above to login the user" , (5, 140), cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)	
			if time.time() - start >= DURATION: 
				cv2.putText(frame, "Login criterions not satisfied." , (5, 120), cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)	
				cv2.putText(frame, "Time run out. Face recognition login failed." , (5, 160), cv2.FONT_HERSHEY_PLAIN, 1.2, (206, 0, 209), 2, cv2.LINE_AA)	

			encode = cv2.imencode('.jpg', frame)[1].tobytes()
			yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')
		if count > NUM_TO_TAKE:
			self.login = True
			#loading the user to log in 
			self.user = User.query.filter_by(login_path = user_label).first()
		   	print "Facelogin_enabled: ", self.login
		   	print "Login user path: ", self.user