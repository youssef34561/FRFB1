import base64
from io import BytesIO
from PIL import Image
import face_recognition
import cv2
from gtts import gTTS
import numpy as np
import pymongo
import skimage.io


myclient = pymongo.MongoClient('mongodb+srv://user9:24683579@cluster0-kam8g.mongodb.net/test?retryWrites=true&w=majority')
mydb = myclient["face_recognition"]


def encode(img):
    encoded_string = base64.b64encode(img)
    return encoded_string


def decode(base64_string):
    image = Image.open(BytesIO(base64.b64decode(base64_string)))
    image = image.convert("RGB")

    return np.array(image)


def save_face(img, name):
    col = mydb['saved_faces']

    id = 0
    for x in col.find():
        id = x['_id']+1

    x = {}
    x['_id'] = id
    x['name'] = name
    x['encoded_image'] = face_recognition.face_encodings(img)[0].tolist()

    col.insert(x)


def get_faces(img):
    # Get stored face encodings
    col = mydb['saved_faces']
    known_face_encodings = []
    known_face_names = []
    for x in col.find():
        known_face_encodings.append(np.asarray(x['encoded_image']))
        known_face_names.append(x['name'])

    face_locations = []
    face_encodings = []
    face_names = []
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses)
    # to RGB color (which face_recognition uses)
    #rgb_small_frame = small_frame[:, :, ::-1]
    # Not needed now since we process RGB images right away

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0])

    # Use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings, face_encodings[0])
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]
    face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(img, (left, bottom + 25), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(img, name, (left + 6, bottom + 19), font, 0.75, (255, 255, 255), 1)

    return img, face_names


def read_names(names):
    mytext = ""
    for i in range(len(names)):
        mytext += names[i] + " "
        if i < len(names)-1:
            mytext += "and "

    myobj = gTTS(text=mytext, lang='en', slow=False)
    myobj.save("output.mp3")
    sound_bytes = open("output.mp3", "rb").read()

    return base64.b64encode(sound_bytes)
