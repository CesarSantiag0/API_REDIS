from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import redis
import json

app = Flask(__name__)
CORS(app)

# Conexión a Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Mensaje de conexión a Redis
print("Conexión a la base de datos Redis establecida.")

# Ruta de prueba para confirmar que el servidor está en funcionamiento
@app.route("/api/test", methods=['GET'])
def test_connection():
    return "Servidor en funcionamiento y conexión a Redis establecida."

# Obtener datos del sensor y estado de la alarma desde Redis
@app.route("/api/plantitas/update_humidity_temperature", methods=['PATCH'])
def update_sensor_data():
    try:
        data = request.json
        temperature = data.get("temperatura")
        humidity = data.get("humedad")
        motion_detected = data.get("motion_detected")
        
        # Guardar datos en Redis
        redis_client.hset('sensor_data', 'temperatura', temperature)
        redis_client.hset('sensor_data', 'humedad', humidity)
        redis_client.hset('sensor_data', 'motion_detected', motion_detected)
        
        resp = jsonify({"message": "Datos del sensor actualizados correctamente"})
        resp.status_code = 200
    except Exception as e:
        resp = jsonify({"message": f"Error: {e}"})
        resp.status_code = 500
    return resp

# Obtener datos del sensor y estado de la alarma desde Redis
@app.route("/api/plantitas/get_sensor_data", methods=['GET'])
def get_sensor_data():
    try:
        sensor_data = redis_client.hgetall('sensor_data')
        response = jsonify(sensor_data)
        response.status_code = 200
    except Exception as e:
        response = jsonify({"message": f"Error: {e}"})
        response.status_code = 500
    return response

# Obtener el estado de la alarma desde Redis
@app.route("/api/alarma", methods=['GET'])
def get_alarm_status():
    try:
        alarm_status = redis_client.get('estado_alarma')
        if alarm_status is None:
            alarm_status = 0
        response = jsonify({"estado_alarma": int(alarm_status)})
        response.status_code = 200
    except Exception as e:
        response = jsonify({"message": f"Error: {e}"})
        response.status_code = 500
    return response

# Actualizar el estado de la alarma en Redis
@app.route("/api/alarma", methods=['POST'])
def update_alarm_status():
    try:
        data = request.json
        estado_alarma = data.get("estado_alarma", 0)
        
        # Guardar estado de la alarma en Redis
        redis_client.set('estado_alarma', estado_alarma)
        
        resp = jsonify({"message": "Estado de la alarma actualizado correctamente"})
        resp.status_code = 200
    except Exception as e:
        resp = jsonify({"message": f"Error: {e}"})
        resp.status_code = 500
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
