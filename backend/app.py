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
#modelFile = "models/res10_300x300_ssd_iter_140000.caffemodel"
#configFile = "models/deploy.prototxt.txt"
#net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

current_dir = os.getcwd()
face_model = YOLO(current_dir+'/models/scratch_ee4208.pt')
# face_model = YOLO(current_dir+'/models/bests.pt')
default_rgb = (255,255,255)
threshold = 0.2

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
    results = face_model(img, verbose=False)[0]
    faceList = results.boxes.data.tolist()
    
    # Initialize variables to keep track of the largest face
    largest_area = 0
    largest_face = None
    largest_face_coords = None

    if faceList:
        for result in faceList:
            x1, y1, x2, y2, score, class_id = result
            if score > threshold:
                face_area = (x2 - x1) * (y2 - y1)
                if face_area > largest_area:
                    largest_area = face_area
                    largest_face = img[int(y1):int(y2), int(x1):int(x2)]
                    largest_face_coords = (int(x1), int(y1), int(x2), int(y2), score, class_id)
        
        if largest_face is not None:
            latest_cropped_face = largest_face
            x1, y1, x2, y2, score, class_id = largest_face_coords
            img = cv2.rectangle(img, (x1, y1), (x2, y2), default_rgb, 4)
            img = cv2.putText(img, results.names[int(class_id)].upper(), (x1, y1 - 10),
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