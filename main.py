import base64
import os

import cv2
import face_recognition
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load known faces once when the server starts
known_face_encodings = []
known_face_id_empleados = []


def load_known_faces(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    for id_empleado in os.listdir(directory):
        person_dir = os.path.join(directory, id_empleado)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_dir, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    if face_encodings:
                        known_face_encodings.append(face_encodings[0])
                        known_face_id_empleados.append(id_empleado)


# Load faces on startup
load_known_faces("known_faces")


@app.route('/add_person', methods=['POST'])
def add_person():
    data = request.json
    if 'id_empleado' not in data or 'image' not in data:
        return jsonify({'error': 'Faltan parámetros'}), 400

    id_empleado = data['id_empleado']
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
    person_dir = os.path.join('known_faces', id_empleado)
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
    known_face_id_empleados.append(id_empleado)

    return jsonify({'message': 'Persona añadida correctamente'})


@app.route('/recognize', methods=['POST'])
def recognize_faces():
    data = request.json
    if 'image' not in data or 'id_empleado' not in data:
        return jsonify({'error': 'Faltan parámetros'}), 400

    id_empleado = data['id_empleado']
    image_data = base64.b64decode(data['image'])
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    if len(face_encodings) == 0:
        return jsonify({'result': False}), 200
    if len(face_encodings) > 1:
        return jsonify({'error': 'Se detectó más de un rostro en la imagen'}), 400

    face_encoding = face_encodings[0]
    # Buscar todos los índices donde el nombre coincide con el id_empleado
    indices = [i for i, id_ in enumerate(known_face_id_empleados) if id_ == id_empleado]
    if not indices:
        return jsonify({'result': False}), 200

    # Comparar solo contra los encodings de ese id_empleado
    encodings_to_compare = [known_face_encodings[i] for i in indices]
    matches = face_recognition.compare_faces(encodings_to_compare, face_encoding)
    result = any(matches)
    return jsonify({'result': result}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
