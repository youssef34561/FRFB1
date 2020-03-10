from flask import Flask, request, jsonify
import numpy as np
import json
import base64
import skimage.io

app = Flask(__name__)

def decode(base64_string):
    if isinstance(base64_string, bytes):
        base64_string = base64_string.decode("utf-8")

    imgdata = base64.b64decode(base64_string)
    img = skimage.io.imread(imgdata, plugin='imageio')
    return np.array(img)

@app.route("/")
def index():
    data = {}
    data["message"] = "Hello, Asmaa!"
    return jsonify(data)

@app.route("/photo", methods=["POST"])
def index2():
    read = request.get_json()
    if type(read) == str:
        read = json.loads(read)
    img = read['img']
    img2 = decode(img)
    data = {}
    data['shape'] = img2.shape
    
    return jsonify(data)