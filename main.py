import base64
import os
import sys

import cv2
import face_recognition
import numpy as np
import pyodbc
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

SERVER = os.getenv('SERVER')
DATABASE = os.getenv('DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=no;'

conn = pyodbc.connect(connectionString)


@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Excepción no controlada: {e}")
    sys.exit(1)

@app.route('/recognize', methods=['POST'])
def recognize_faces():
    data = request.json
    if 'image' not in data or 'id_empleado' not in data:
        return jsonify({'error': 'Faltan parámetros'}), 400

    id_empleado = data['id_empleado']
    try:
        image_data = base64.b64decode(data['image'])
    except Exception:
        return jsonify({'error': 'La imagen no está en formato base64 válido'}), 400
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({'error': 'La imagen proporcionada no es válida'}), 400

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    if len(face_encodings) == 0:
        return jsonify({'result': False}), 200
    if len(face_encodings) > 1:
        return jsonify({'error': 'Se detectó más de un rostro en la imagen'}), 400

    face_encoding = face_encodings[0]

    cursor = conn.cursor()
    cursor.execute("SELECT caraBase64 FROM Cara WHERE idEmpleado = ?", id_empleado)
    rows = cursor.fetchall()
    if not rows:
        return jsonify({'result': False}), 200

    encodings_to_compare = []
    for row in rows:
        try:
            cara_base64 = row[0]
            image_data_db = base64.b64decode(cara_base64)
            nparr_db = np.frombuffer(image_data_db, np.uint8)
            image_db = cv2.imdecode(nparr_db, cv2.IMREAD_COLOR)
            if image_db is None:
                continue
            rgb_image_db = cv2.cvtColor(image_db, cv2.COLOR_BGR2RGB)
            db_face_encodings = face_recognition.face_encodings(rgb_image_db)
            if db_face_encodings:
                encodings_to_compare.append(db_face_encodings[0])
        except Exception:
            continue

    if not encodings_to_compare:
        return jsonify({'result': False}), 200

    matches = face_recognition.compare_faces(encodings_to_compare, face_encoding)
    result = any(matches)
    return jsonify({'result': result}), 200


@app.route('/add_face', methods=['POST'])
def add_face():
    data = request.json
    if 'image' not in data or 'id_empleado' not in data:
        return jsonify({'error': 'Faltan parámetros: image e id_empleado son requeridos'}), 400

    id_empleado = data['id_empleado']
    image_base64 = data['image']

    try:
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({'error': 'La imagen proporcionada no es válida'}), 400

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if len(face_encodings) == 0:
            return jsonify({'error': 'No se detectó ningún rostro en la imagen'}), 400
        if len(face_encodings) > 1:
            return jsonify({'error': 'Se detectó más de un rostro en la imagen'}), 400

        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        _, buffer = cv2.imencode('.jpg', face_image)
        face_image_base64 = base64.b64encode(buffer).decode('utf-8')

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Cara (idEmpleado, caraBase64) VALUES (?, ?)",
            (id_empleado, face_image_base64)
        )
        conn.commit()

        return jsonify({
            'message': 'Cara agregada exitosamente',
            'id_empleado': id_empleado
        }), 201

    except pyodbc.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
