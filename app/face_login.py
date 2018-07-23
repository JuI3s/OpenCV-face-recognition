import time
from face_recognition import get_image

#Should work. Just specify the user_label. 

def face_login(user_label, face_label, SHAPE = 'rectangle', DURATION = 60, NUM_TO_TAKE = 10): 
	start = time.time()
	threshold = 95
	detector = FaceDetector('app/frontal_face.xml')
	vid = video_capture.VideoCamera()
	print "Start face recognition login... "
	count = 0
	timer = 0
	while count < NUM_TO_TAKE and time.time() - start < DURATION: 
		frame = vid.get_frame()
		face_coord = detector.detect(frame)
		if len(face_coord):
			frame, face_image = get_image(frame, face_coord, 'rectangle')
			image = face_image[0]
			pred, error = recogniser.predict(image)

			if timer % 3 == 2: 
				#Updating every three frames. 
				if error < threshold and face_label[pred] == user_label: 
					#add the label for the current user.
					count++

		encode = cv2.imencode('.jpg', frame)[1].tobytes()
		yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + encode + b'\r\n')		
		#cv2.imshow('Video feed', frame)
		timer = timer + 1

	print "User logged in."
	#log the current the user in.