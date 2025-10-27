from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

import os
SERVICE2_URL = os.getenv("NAME2_SERVICE_URL", "http://service2-service:8003/historial")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    try:
        response = requests.get(SERVICE2_URL)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Error al conectar con Service2: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
