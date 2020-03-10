from flask import Flask, request, jsonify
from utilities import *
import cv2
import base64
from io import BytesIO
from PIL import Image
import face_recognition
import cv2
from gtts import gTTS
import numpy as np
import pymongo
import json

app = Flask(__name__)


@app.route("/")
def index():
    data = {}
    data["message"] = "Hello, Asmaa!"
    return jsonify(data)

@app.route("/photo", methods=["POST"])
def index2():
    read = json.loads(request.get_json())
    img = read['img']
    img = decode(img)

    save = read['save']
    if save:
        save_face(img, read['name'])
        return "", 204
    else:
        new_img, names = get_faces(img)
        sound_bytes = read_names(names)
        cv2.imwrite('img.jpg', new_img)

        new_img_encoded = encode(new_img)
        data = {}
        data['img'] = str(new_img_encoded)
        data['sound'] = str(sound_bytes)
        data['names'] = names

        return jsonify(data)
