import os
import datetime as dt
import cv2
import Tkinter


# Getting screen resolution
root = Tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

# Getting current time for imageName
now = dt.datetime.now()
imageName = str(now.date()) + "_" + str(now.time().replace(microsecond=0)) + '.jpg'

# Setting paths
mainPhotosDirectoryPath = '/home/pi/Desktop/Camera/Photos/'
directoryToPhotosWithFacesPath = '/home/pi/Desktop/Camera/FacesDetected/'
imagePath = mainPhotosDirectoryPath + imageName
cascPath = "./haarcascade_frontalface_default.xml"

# Creating destination catalog if doesn't exist
if not os.path.exists(mainPhotosDirectoryPath):
    os.makedirs(mainPhotosDirectoryPath)

if not os.path.exists(directoryToPhotosWithFacesPath):
    os.makedirs(directoryToPhotosWithFacesPath)

# Taking photo
os.system('raspistill -o ' + imagePath)

# Getting cascade and image
faceCascade = cv2.CascadeClassifier(cascPath)
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detecting faces on image
faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30)
)

# Printing number of detected faces
print("Found {0} faces!".format(len(faces)))

# Flaging faces by rectangles on image and saving tagged image
for(x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

if (len(faces) > 0):
    cv2.imwrite(directoryToPhotosWithFacesPath + imageName, image)

# Showing resized image with faces marked
resized_image = cv2.resize(image, (width, height))
cv2.imshow("Faces found", resized_image)
cv2.waitKey(0)
