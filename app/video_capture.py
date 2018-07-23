#Camera library

import cv2
import face_recognition

class VideoCamera():

	def __init__(self):
		#Initialising a cv2 VideoCapture object
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		#Drop the camera object when it is no longer needed
		self.video.release()

	def get_frame(self, in_grayscale=False):
		#Class method: return frames (numpy array type) for video streaming
		#Make sure that the camera is opened before running the module
		if not self.video.isOpened():
			return RuntimeError('Could not start the camera.')
		#Return tuple type values. '_' is true is the frame is received. Frame is the actauly frame (numpy array) received from the camera 
		_, frame = self.video.read()

		#If in_grayscale set True, then the frames  returned are converted to grayscale
		if in_grayscale:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		return frame

	def get_imenco(self):
		#Return the JPEG encoding the frames 
		if not self.video.isOpened():
			raise RuntimeError('Could not start the camera.')

		_, frame = self.video.read()
		
		#Rendering live stream in motion JPEG format 
		#cv2 imencode method returns two values 1) Boolean true if received and 2) Buffer of the encoding 
		# The buffer is converted into binary form to be sent as a signal for web rendering 

		return cv2.imencode('.jpg', frame)[1].tobytes()

	def show_frame(self, seconds, in_grayscale=False):
		#show frame by displaying a numpy array
		_, frame = self.video.read()
		if in_grayscale:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		cv2.imshow('Frame', frame)
		#Seconds refer to the time to wait for
		#Waitkey return None either after the set seconds have passed or a key is pressed
		#If a key is pressed, the value of the key pressed is returned
		key_pressed = cv2.waitKey(seconds)

		return key_pressed & 0xFF

if __name__ == '__main__':
	#For testing displaying images only only
	VC = VideoCamera()
	while True: 
		KEY = VC.show_frame(1, False)
		if KEY == 27:
			#27 is the value for 'esc'
			break
	VC.show_frame(1)
