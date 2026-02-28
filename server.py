from flask import Flask, jsonify
from flask_cors import CORS
import random, time, pickle
import pandas as pd
import serial
import threading
import re

app = Flask(__name__)
CORS(app)

last_update_time = 0
current_data = []
history_data = {f"Cable-{i}": [] for i in range(1, 11)}

live_sensor_data = {
    "vibration_1": 0,
    "vibration_2": 0,
    "accel": 0,
    "gyroscope": 0,
    "photodiode": 0
}

def read_serial_data():
    global live_sensor_data
    while True:
        try:
            ser = serial.Serial('COM3', 115200, timeout=1)
            print("Successfully connected to Arduino on COM3 (115200 baud)")
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Ignore empty or pure noise lines
                    if "GyroRaw:" in line or "VibA:" in line:
                        # Extract metrics using regex
                        gyro_m = re.search(r'GyroRaw:([0-9.]+)', line)
                        vib1_m = re.search(r'VibA:([0-9.]+)', line)
                        vib2_m = re.search(r'VibB:([0-9.]+)', line)
                        light_m = re.search(r'Light:([0-9.]+)', line)

                        if gyro_m:
                            live_sensor_data["gyroscope"] = float(gyro_m.group(1))
                        if vib1_m:
                            live_sensor_data["vibration_1"] = float(vib1_m.group(1))
                        if vib2_m:
                            live_sensor_data["vibration_2"] = float(vib2_m.group(1))
                        if light_m:
                            live_sensor_data["photodiode"] = float(light_m.group(1))
        except Exception as e:
            print(f"Failed to connect to Serial Port COM3. Retrying in 3 seconds... ({e})")
            time.sleep(3)

serial_thread = threading.Thread(target=read_serial_data, daemon=True)
serial_thread.start()

# LOAD TRAINED MODELS
try:
    with open('xgboost_fiber_model.pkl', 'rb') as f:
        xgb_model = pickle.load(f)
    with open('linear_regression_fiber_model.pkl', 'rb') as f:
        lr_model = pickle.load(f)
    print("Successfully loaded ML models.")
except Exception as e:
    print(f"Error loading models: {e}")
    xgb_model = None
    lr_model = None

# SIMULATED SENSOR NODES (Representing 10 separate cables)
NODES = [
    {"id":"Cable-1", "lat":12.8231, "lng":80.0444, "path": [[12.822, 80.043], [12.824, 80.046]]}
]

@app.route("/data")
def multi_node_data():
    global last_update_time, current_data, history_data

    current_time = time.time()
    
    output = []
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")

    for n in NODES:
        if n["id"] == "Cable-1":
            # Map the actual hardware data from the COM port to Cable-1
            vibration_1 = live_sensor_data["vibration_1"]
            vibration_2 = live_sensor_data["vibration_2"]
            accel = live_sensor_data["accel"]
            gyroscope = live_sensor_data["gyroscope"]
            photodiode = live_sensor_data["photodiode"]
        else:
            # Use safe dummy data for the rest of the simulated cables
            vibration_1 = 0.0
            vibration_2 = 0.0
            accel = 0.0
            gyroscope = 0.0
            photodiode = 100.0
        
        # Bending logic: high gyro indicating twisting and drop in light indicating physical stress
        is_bending = gyroscope > 120 and photodiode < 40 

        if vibration_1 > 800 or vibration_2 > 800 or accel > 15 or is_bending:
            status = "DANGER"
        elif vibration_1 > 600 or vibration_2 > 600 or gyroscope > 80 or photodiode < 70:
            status = "WARNING"
        else:
            status = "SAFE"
            
        predictive_status = "High risk of fiber rupture at this node." if is_bending else ("Potential physical stress accumulating." if status == "WARNING" else "Fiber integrity is normal.")

        # ML PREDICTION LOGIC
        xgb_pred_text = "N/A"
        lr_pred_value = 0.0
        
        if xgb_model and lr_model:
            # Build dataframe matching trained dataset columns
            input_df = pd.DataFrame({
                'vib_1': [vibration_1],
                'vib_2': [vibration_2],
                'gyro': [gyroscope],
                'photodiode': [photodiode]
            })
            
            # XGBoost Classifier
            xgb_pred = int(xgb_model.predict(input_df)[0])
            if xgb_pred == 0:
                xgb_pred_text = "Safe"
            elif xgb_pred == 1:
                xgb_pred_text = "Warning"
            else:
                xgb_pred_text = "Critical"
                
            # Linear Regression
            lr_pred_value = round(float(lr_model.predict(input_df)[0]), 4)

        reading = {
            "node_id": n["id"],
            "lat": n["lat"],
            "lng": n["lng"],
            "path": n["path"],
            "vibration_1": vibration_1,
            "vibration_2": vibration_2,
            "accel": accel,
            "gyroscope": gyroscope,
            "photodiode": photodiode,
            "is_bending": is_bending,
            "predictive_status": predictive_status,
            "xgb_prediction": xgb_pred_text,
            "lr_prediction": lr_pred_value,
            "status": status,
            "time": formatted_time
        }
        
        output.append(reading)
        
        # Keep only last 100 historical readings to prevent memory bloat
        # Only add to history if time has advanced somewhat, e.g., 1 second, to avoid 200ms history spam
        # Or just append. We'll append, but maybe limit to once a second
        # Wait, avoiding extra vars, I'll just append it directly for now.
        history_data[n["id"]].append(reading)
        if len(history_data[n["id"]]) > 100:
            history_data[n["id"]].pop(0)

    current_data = output
    last_update_time = current_time

    return jsonify(current_data)

@app.route("/history/<node_id>")
def get_node_history(node_id):
    if node_id in history_data:
        return jsonify(history_data[node_id])
    return jsonify({"error": "Node not found"}), 404

app.run(host="0.0.0.0", port=5000)