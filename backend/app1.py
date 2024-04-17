from flask import Flask, render_template, Response, request, jsonify
import cv2
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from datetime import datetime
import traceback
import logging
import os
from ultralytics import YOLO 
import base64

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
CORS(app)

# Load your pre-trained model
modelFile = "models/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "models/deploy.prototxt.txt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

# Load the TensorFlow face recognition model
recognition_model = tf.keras.models.load_model('models/face_recog.h5')
default_rgb = (255, 255, 255)
latest_cropped_face = None
class_names = ['Chingkang','Duc','Freddieew','Magaret','Other','Quan','Song','You Zhi']

latest_recognized_name = "Unknown"

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
    global latest_cropped_face, latest_recognized_name
    height, width = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, (300, 300), (104.0, 117.0, 123.0))
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

    if largest_face_box is not None:
        (x, y, x1, y1) = largest_face_box
        cropped_face = img[y:y1, x:x1]
        latest_cropped_face = cropped_face
        recognized_name, predicted_prob = recognize_face(cropped_face)
        latest_recognized_name = recognized_name  # Store the recognized name globally
        cv2.rectangle(img, (x, y), (x1, y1), default_rgb, 4)
        
        display_text = f"{recognized_name}"
        display_text += f", {predicted_prob:.2f}"

        cv2.putText(img, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, default_rgb, 2, cv2.LINE_AA)
    else:
        latest_cropped_face = None
        latest_recognized_name = "Unknown"

    return img

def recognize_face(face_img):
    if face_img is not None:
        face_img = cv2.resize(face_img, (224, 224))  
        face_img = face_img.astype('float32') / 255.0 
        face_img = np.expand_dims(face_img, axis=0)  
        prediction = recognition_model.predict(face_img)
        predicted_class = class_names[np.argmax(prediction)]
        predicted_prob = np.max(prediction)  
        
        return predicted_class, predicted_prob 
    return "Unknown", 0.0  


@app.route('/video')
def frame_gen():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/latest_face')
def latest_face():
    global latest_cropped_face, latest_recognized_name
    try:
        if latest_cropped_face is not None:
            ret, buffer = cv2.imencode('.jpg', latest_cropped_face)
            if ret:
                face_image = base64.b64encode(buffer).decode('utf-8')  # Encode the image to base64
                response = {
                    "image": face_image,
                    "recognized_name": latest_recognized_name
                }
                return jsonify(response)
            else:
                return jsonify({"message": "Image encoding failed", "recognized_name": "Unknown"}), 500
        else:
            return jsonify({"message": "No face detected yet.", "recognized_name": "Unknown"}), 404
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.debug(traceback.format_exc())
        return jsonify({"message": "An internal server error occurred.", "error": str(e)}), 500

# @app.route('/latest_face')
# def latest_face():
#     global latest_cropped_face
#     try:
#         if latest_cropped_face is not None:
#             ret, buffer = cv2.imencode('.jpg', latest_cropped_face)
#             return Response(buffer.tobytes(), mimetype='image/jpeg')
#         else:
#             logging.info("No face detected yet.")
#             return Response("No face detected yet.", status=404)
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")
#         logging.debug(traceback.format_exc())  
#         return Response("An internal server error occurred.", status=500)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)