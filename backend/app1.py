from flask import Flask, render_template, Response, request
import cv2
from flask_cors import CORS

import numpy as np
from datetime import datetime
import traceback
import logging
import os
from ultralytics import YOLO # add this line

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
CORS(app)

# Load your pre-trained model
modelFile = "models/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "models/deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
default_rgb = (255,255,255)

latest_cropped_face = None

def gen_frames():
    vid = cv2.VideoCapture(0)
    while True:
        ret, frame = vid.read()
        if not ret:
            break  # If no frame is captured, exit the loop

        face = detector(frame)

        if face is not None:
            ret, buffer = cv2.imencode('.jpg', face)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def detector(img):
    global latest_cropped_face  
    height, width = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, 
                                 (300, 300), (104.0, 117.0, 123.0))
    net.setInput(blob)
    faces = net.forward()

    largest_area = 0
    largest_face_box = None

    for i in range(faces.shape[2]):
        confidence = faces[0, 0, i, 2]
        if confidence > 0.5:  
            box = faces[0, 0, i, 3:7] * np.array([width, height, width, height])
            (x, y, x1, y1) = box.astype("int")
            area = (x1 - x) * (y1 - y)
            if area > largest_area:
                largest_area = area
                largest_face_box = (x, y, x1, y1)

    # If a face was detected, crop it and store in the global variable
    if largest_face_box is not None:
        (x, y, x1, y1) = largest_face_box
        cropped_face = img[y:y1, x:x1]
        latest_cropped_face = cropped_face
        # cv2.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 2)
        cv2.rectangle(img, (x, y), (x1, y1), default_rgb, 4)
        cv2.putText(img, "FACE", (x, y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 1.3, default_rgb, 2, cv2.LINE_AA)
    else:
        latest_cropped_face = None

    return img

@app.route('/video')
def frame_gen():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/latest_face')
def latest_face():
    global latest_cropped_face
    try:
        if latest_cropped_face is not None:
            ret, buffer = cv2.imencode('.jpg', latest_cropped_face)
            return Response(buffer.tobytes(), mimetype='image/jpeg')
        else:
            logging.info("No face detected yet.")
            return Response("No face detected yet.", status=404)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.debug(traceback.format_exc())  
        return Response("An internal server error occurred.", status=500)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)