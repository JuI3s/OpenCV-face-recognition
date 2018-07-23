#performing basic image operations needed for training 

import numpy as np
import cv2

def resize(images, size=(100,100)):
	#Parameters: images, list of numpy array type, input images to be resized
	#size: tuple type, default = (100, 100), dimension of the picture to be scaled to
	#the images need to be normalised to a specific size before training.
	#image_norm: array of normalised images. 

	images_norm = []
	for image in images:
		#image.shape returns three variables (number of rows, columns and colour channel) 
		#if the colour channel is not gray scale.
		#Otherwise only the first two properties are returned. 
		#training is done in gray_scale images for shorter periods and more distinguished facial features.

		#If the image is not in grayscale then the length of image.shape is 3 as there is an extra attribute 
		#specifying the colour channel 

		is_color = len(image.shape) == 3
		if is_color:
			#images are usually stored in BGR colour channel in opencv
			#Converting the images to grayscale 
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		#INTER_AREA and INTER_LINEAR are preferrable methods for shrinking/dilating images, repectively.
		if image.shape < size:
			image_norm = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
		else:
			image_norm = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
		images_norm.append(image_norm)

	return images_norm

def normalise_intensity(images):
	#Parameters: images, list of numpy array type, input images on which normalise_intensity is to be performed 
	#Input images need to be in grayscale and are converted to grayscale if in other colour channels 
	#increase the contrast in histogram intensities for better training performace
	#Return value: images_norm, array type, list of

	images_norm = []
	for image in images:
		#if the colour channel is not grey3
		is_color = len(image.shape) == 3
		if is_color:
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		#Attach the modified image on which histogram normalisation has been performed 
		images_norm.append(cv2.equalizeHist(image))
	return images_norm

def cut_rectangle(image, face_coord):
	#Parameters: images, numpy array type, input image on which rectangle-shaped regions of detected faces are to be extracted
	#face_coord: numpy array type, containing positional (coordinates) information about the detected face
	#Return value: a list of rectangle-shaped iamges of the detected face areas

	images_rectangle = []

	#face_coord is an opencv object that contains the vertex coordinates of the rectangle around the face detected. 
	#(x, y, w, h) contains information about the top left coordinates (x,y), width and height
	for (x, y, w, h) in face_coord:
		images_rectangle.append(image[y: y + h, x: x + w])
	return images_rectangle

def cut_ellipse(image, face_coord):
	#Parameters: images, numpy array type, input image on which ellipse-shaped regions of detected faces are to be extracted
	#face_coord: numpy array type, containing positional (coordinates) information about the detected face
	#Return value: a list of ellipse-shaped iamges of the detected face areas	images_ellipse = []

	images_ellipse = []

	for (x, y, w, h) in face_coord:
		centre = (int(x + w / 2), int(y + h / 2))
		axis_major = int(h / 2)
		axis_minor = int(w / 2)
		#return an array of zeros with the same dimension and type of the original array.
		mask = np.zeros_like(image)
		#mask = cv2.ellipse(mask, (113, 155), (23, 15), 0.0, 0.0, 360.0, (255, 255, 255), -1)
		mask = cv2.ellipse(mask, centre, (axis_major, axis_minor), 0.0, 0.0, 360.0, (255, 255, 255), -1)
		image_ellipse = np.bitwise_and(image, mask)
		images_ellipse.append(image_ellipse[y: y + h, x: x + w])

	return images_ellipse

def draw_face_rectangle(image, face_coord):
	#Parameters: images, numpy array type, input image is a frame in the video stream 
	#on which rectangles are to be drawn around the detected faces 
	#face_coord: numpy array type, containing positional (coordinates) information about the detected face
	#Return value: an image on which rectangles are drawn around regions of the detected faces

	for (x, y, w, h) in face_coord:
		#draw rectangles around the faces detected
		#rectangle() parameters: image, RGB colour, line thickness.
		cv2.rectangle(image, (x, y), (x + w, y + h), (206, 0, 209), 2)
	return image

def draw_face_ellipse(image, faces_coord):
	#Parameters: images, numpy array type, input image is a frame in the video stream 
	#on which ellipses are to be drawn around the detected faces 
	#face_coord: numpy array type, containing positional (coordinates) information about the detected face
	#Return value: an image on which ellipses are drawn around regions of the detected faces

	for (x, y, w, h) in faces_coord:
		#attributes about the ellipse
		centre = (x + w / 2, y + h / 2)
		axis_major = h / 2
		axis_minor = w / 2		
		#draw ellipses around the faces detected
		cv2.ellipse(image, center = centre, axes=(axis_major, axis_minor), angle=0, startAngle=0, endAngle=360, color=(206, 0, 209), thickness=2)
	return image