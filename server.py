from flask import Flask, jsonify
from flask_cors import CORS
import random, time

app = Flask(__name__)
CORS(app)

# SIMULATED SENSOR NODES (Representing 10 separate cables)
NODES = [
    {"id":"Cable-1", "lat":13.0827, "lng":80.2707, "path": [[13.081, 80.269], [13.084, 80.272]]},
    {"id":"Cable-2", "lat":13.0418, "lng":80.2341, "path": [[13.040, 80.232], [13.043, 80.236]]},
    {"id":"Cable-3", "lat":13.0033, "lng":80.2555, "path": [[13.001, 80.253], [13.005, 80.258]]},
    {"id":"Cable-4", "lat":12.9815, "lng":80.2180, "path": [[12.980, 80.216], [12.983, 80.220]]},
    {"id":"Cable-5", "lat":13.0850, "lng":80.2101, "path": [[13.083, 80.208], [13.087, 80.212]]},
    {"id":"Cable-6", "lat":13.0335, "lng":80.2675, "path": [[13.031, 80.265], [13.036, 80.270]]},
    {"id":"Cable-7", "lat":13.0067, "lng":80.2206, "path": [[13.004, 80.218], [13.009, 80.223]]},
    {"id":"Cable-8", "lat":12.9229, "lng":80.1163, "path": [[12.920, 80.114], [12.925, 80.119]]},
    {"id":"Cable-9", "lat":12.9151, "lng":80.2300, "path": [[12.913, 80.228], [12.917, 80.232]]},
    {"id":"Cable-10", "lat":12.9675, "lng":80.1491, "path": [[12.965, 80.147], [12.970, 80.151]]}
]

@app.route("/data")
def multi_node_data():
    output = []

    for n in NODES:
        vibration = random.randint(100, 950)
        accel = random.randint(0, 20)
        gyroscope = random.randint(0, 180) # degrees per second
        photodiode = random.randint(0, 100) # light intensity %
        
        # Bending logic: high gyro indicating twisting and drop in light indicating physical stress
        is_bending = gyroscope > 120 and photodiode < 40 

        if vibration > 800 or accel > 15 or is_bending:
            status = "DANGER"
        elif vibration > 600 or gyroscope > 80 or photodiode < 70:
            status = "WARNING"
        else:
            status = "SAFE"
            
        predictive_status = "High risk of fiber rupture at this node." if is_bending else ("Potential physical stress accumulating." if status == "WARNING" else "Fiber integrity is normal.")

        output.append({
            "node_id": n["id"],
            "lat": n["lat"],
            "lng": n["lng"],
            "path": n["path"],
            "vibration": vibration,
            "accel": accel,
            "gyroscope": gyroscope,
            "photodiode": photodiode,
            "is_bending": is_bending,
            "predictive_status": predictive_status,
            "status": status,
            "time": time.strftime("%H:%M:%S")
        })

    return jsonify(output)

app.run(host="0.0.0.0", port=5000)