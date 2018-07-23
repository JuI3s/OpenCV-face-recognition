import cv2

class FaceDetector(object):

    def __init__(self, xml_path):
        #Initialize a frontal face detector object 
        #xml_path is a .xml file linking to the opencv frontal face detector
        self.classifier = cv2.CascadeClassifier(xml_path)

    def detect(self, image, biggest_only=False):
        #Method to detect faces in an  image 
        #parameters: image, numpy array, the image on which face detection is to be carried out 
        #biggest_only, boolean, if set true then only return the biggest face (one single face) detected
        #Return value: list of numpy array type, each elemnet is a numpy array that contains 
        #the positional (coordinates) information of each detected face

        #if len(image) is 3 then this means that the image is not in grayscale 
        #Convert the image to grayscale (if not already) for face detection
        is_color = len(image) == 3
        if is_color:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image

        #Parameters for detectMultiScale function from opencv library 
        #scale_factor: real type, scale factor by which the image is resized 
        #min_neighbors: int type. The algorithm scans a region repeated to detect faces
        #min_neighbors specifies the minimum tiems a face needs to be detected in a region to count as a detected face
        #min_size: tuple type, dimension of the smallest face that can be detected 
        #flags: opencv objects, for internal processing by the opencv library

        scale_factor = 1.2
        min_neighbors = 5
        min_size = (30, 30)
        flags = cv2.CASCADE_FIND_BIGGEST_OBJECT | \
            cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else \
            cv2.CASCADE_SCALE_IMAGE

        face_coord = self.classifier.detectMultiScale(
            image_gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size,
            flags=flags
        )

        return face_coord   