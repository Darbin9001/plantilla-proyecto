from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

SERVICE2_URL = "http://127.0.0.1:8002/historial"

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
