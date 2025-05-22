import base64
import os

import cv2
import face_recognition
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load known faces once when the server starts
known_face_encodings = []
known_face_names = []


def load_known_faces(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for person_name in os.listdir(directory):
        person_dir = os.path.join(directory, person_name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_dir, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    if face_encodings:
                        known_face_encodings.append(face_encodings[0])
                        known_face_names.append(person_name)


# Load faces on startup
load_known_faces("known_faces")


@app.route('/add_person', methods=['POST'])
def add_person():
    data = request.json
    if 'name' not in data or 'image' not in data:
        return jsonify({'error': 'Faltan parámetros'}), 400

    name = data['name']
    image_data = base64.b64decode(data['image'])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convertir a RGB para face_recognition
    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)
    except Exception as e:
        return jsonify({'error': f'Error procesando la imagen: {str(e)}'}), 500

    if not isinstance(face_encodings, list) or len(face_encodings) == 0:
        return jsonify({'error': 'No se detectó ningún rostro en la imagen'}), 400
    if len(face_encodings) > 1:
        return jsonify({'error': 'Se detectó más de un rostro en la imagen'}), 400

    # Guardar solo la cara detectada en el directorio correspondiente
    person_dir = os.path.join('known_faces', name)
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)
    image_count = len(os.listdir(person_dir))
    # Detectar la ubicación de la cara
    face_locations = face_recognition.face_locations(rgb_image)
    if not face_locations:
        return jsonify({'error': 'No se detectó ningún rostro en la imagen'}), 400
    top, right, bottom, left = face_locations[0]
    face_image = image[top:bottom, left:right]
    image_path = os.path.join(person_dir, f'{image_count + 1}.jpg')
    cv2.imwrite(image_path, face_image)

    # Añadir a las listas en memoria
    known_face_encodings.append(face_encodings[0])
    known_face_names.append(name)

    return jsonify({'message': 'Persona añadida correctamente'})


@app.route('/recognize', methods=['POST'])
def recognize_faces():
    if 'image' not in request.json:
        return jsonify({'error': 'No image provided'}), 400

    # Decode base64 image
    image_data = base64.b64decode(request.json['image'])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert to RGB (face_recognition uses RGB)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Find faces
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    if len(face_encodings) == 0:
        return jsonify({'error': 'No face detected'}), 400
    if len(face_encodings) > 1:
        return jsonify({'error': 'More than one face detected'}), 400

    face_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    name = "Unknown"
    confidence = 0.0

    if True in matches:
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            confidence = 1 - face_distances[best_match_index]

    return jsonify({'name': name, 'confidence': float(confidence)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
