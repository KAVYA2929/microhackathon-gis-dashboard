from flask import Flask, jsonify
from flask_cors import CORS
import random, time

app = Flask(__name__)
CORS(app)

# SIMULATED SENSOR NODES
NODES = [
    {"id":"Node-1", "lat":13.0827, "lng":80.2707},
    {"id":"Node-2", "lat":13.0835, "lng":80.2715},
    {"id":"Node-3", "lat":13.0842, "lng":80.2728},
    {"id":"Node-4", "lat":13.0850, "lng":80.2740}
]

@app.route("/data")
def multi_node_data():
    output = []

    for n in NODES:
        vibration = random.randint(100, 950)
        accel = random.randint(0, 20)

        if vibration > 800 or accel > 15:
            status = "DANGER"
        elif vibration > 600:
            status = "WARNING"
        else:
            status = "SAFE"

        output.append({
            "node_id": n["id"],
            "lat": n["lat"],
            "lng": n["lng"],
            "vibration": vibration,
            "accel": accel,
            "status": status,
            "time": time.strftime("%H:%M:%S")
        })

    return jsonify(output)

app.run(host="0.0.0.0", port=5000)