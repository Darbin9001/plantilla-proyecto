from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

SERVICE2_URL = "http://127.0.0.1:8002/historial"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/data/<cedula>")
def get_data(cedula):
    """Obtiene el historial de salud por cédula"""
    import requests
    try:
        response = requests.get(f"{SERVICE2_URL}/{cedula}")
        if response.status_code == 200:
            return jsonify(response.json())
        elif response.status_code == 404:
            return jsonify({"error": "No se encontró historial para esta cédula"}), 404
        else:
            return jsonify({"error": f"Error al conectar con Service2: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)