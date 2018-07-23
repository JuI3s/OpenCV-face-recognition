class Update:

	#Telling face_recognition to update the database with newly detected faces.
	#Update in recent 5 frames (default value)
	#Each person in face_label has an indicator that specifies how many times he 
	#has been caught on current frames.

	#Parameters 
	#self: instantiated from the Update class
	#face_label: Array type. A list of the paths for each person, e.g. person_one/
	def __init__(self, face_label): 

		#Declaring an empty incidence array whose length is the length of face_label,
		#or the number of faces added to the database under the current user
		#Each element in the array is an indicator (int) that represents how many 
		#times the corresponding person has been detected in the recent frames

		self.ls = []
		for i in range(len(face_label)):
			self.ls.append(0)
		#Number of the most current frames to keep track of. Default set to 5.
		self.num_frames = 5
		#Declaring a number of such incidence arrays as specified by num_frames
		for i in range(self.num_frames): 
			setattr(self, 'frame' + str(i), list(self.ls))

	def __repr__(self):

		#Method used for convenience in development
		#Print out each frame
		for i in range(self.num_frames):
			print('frame' + str(i) + ': ')
			print(getattr(self, 'frame' + str(i)))

	def clear_current_frame(self):
		#Preparing for a new frame by setting all indicators to 0
		current_frame = getattr(self, 'frame' + str(self.num_frames - 1))
		for i in range(len(current_frame)): 
			current_frame[i] = 0

	def shift_frames(self): 
		#Shift the frames so that the object only keeps track of the most recent ones
		for i in range(self.num_frames - 1):
			setattr(self, 'frame' + str(i), list(getattr(self, 'frame' + str(i + 1))) )

	def add_identified(self, pred):
		#Parameters: pred. A numerical score indicating the accuracy of the prediction
		#Get the latest frame
		current_frame = getattr(self, 'frame' + str(self.num_frames - 1))
		#If a newly identified person, his indicator increments by 1
		#Incrementing from the previous frame since the current frame has been cleared 
		current_frame[pred] = getattr(self, 'frame' + str(self.num_frames - 2))[pred] + 1

	def is_first_access(self, pred):
		#Parameters: pred. A numerical score indicating the accuracy of the prediction
		#Only running when a face is identified
		#Return: First_access, boolean, true if first access for the corresponding person
		current_frame = getattr(self, 'frame' + str(self.num_frames - 1))

		first_access = True
		if  current_frame[pred] == 0:
			first_access = False
		for i in range(self.num_frames - 1):
			if getattr(self, 'frame' + str(i))[pred] > 0:
				#If in previous recent frames the samer person is also identified
				first_access = False
		return first_access

	def is_last_access(self):
		#Return a list of faces whose last access was recorded, i.e. they are no longer
		#detected
		current_frame = getattr(self, 'frame' + str(self.num_frames - 1))
		last_access_list = []
		#Array type. Storing the indice of all whose last access was recorded 

		for i in range(len(current_frame)):
			if current_frame[i] == 0: 
			#If in the most recent frame a person is not identified, then check if he or she 
			#appears in previous recent frames 
				last_access = True 
				if self.frame0[i] == 0:
					#It may not be the last access time for the person if he does not appear 
					#in the first frame
					last_access = False
				for j in range(1, self.num_frames):
					if getattr(self, 'frame' + str(j))[i] != 0:
					#If in previous recent frames the person appears 
						last_access = False
				if last_access == True:
					last_access_list.append(i)

		return last_access_list 