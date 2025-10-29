from fastapi import FastAPI
import httpx
import asyncio
import datetime
import json
import os

app = FastAPI(title="Servicio 2 - Análisis de Datos de Salud")

SERVICE1_URL = os.getenv("NAME1_SERVICE_URL", "http://127.0.0.1:8001/health-data")
DATA_FILE = "data_history.json"
data_history = []


# --- Cargar historial previo si existe ---
def load_data():
    global data_history
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data_history = json.load(f)
                print(f"✅ Historial cargado ({len(data_history)} registros).")
            except json.JSONDecodeError:
                print("⚠️ Archivo JSON vacío o dañado, iniciando nuevo historial.")
                data_history = []
    else:
        print("📁 No se encontró historial previo, iniciando nuevo archivo.")


# --- Guardar historial en archivo ---
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data_history, f, indent=4, ensure_ascii=False)


# --- Analizar datos recibidos ---
def analyze(data):
    bpm = data.get("ritmo_cardiaco", 0)
    temp = data.get("temperatura", 0)
    alertas = []

    if bpm > 100:
        alertas.append("⚠️ Ritmo cardíaco alto (posible taquicardia)")
    if temp > 38:
        alertas.append("🌡️ Fiebre detectada")

    return alertas if alertas else ["✅ Todo en rangos normales"]


# --- Tarea automática para recolectar datos ---
async def auto_fetch_data():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(SERVICE1_URL)
                if response.status_code == 200:
                    data = response.json()
                    alertas = analyze(data)

                    entry = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "datos": data,
                        "alertas": alertas
                    }
                    data_history.append(entry)

                    # ✅ Mantener solo los últimos 100 en memoria para evitar crecer infinito
                    if len(data_history) > 100:
                        data_history.pop(0)

                    save_data()  # Guarda en archivo
                    print(f"[{entry['timestamp']}] ✅ Datos actualizados:", data)
                else:
                    print(f"⚠️ Error {response.status_code} al consultar el service1.")
        except Exception as e:
            print("❌ Error al obtener datos del service1:", e)

        await asyncio.sleep(10)  # Esperar 10 segundos antes de la siguiente lectura


# --- Al iniciar el servicio ---
@app.on_event("startup")
async def startup_event():
    load_data()
    asyncio.create_task(auto_fetch_data())


# --- Endpoints ---
@app.get("/")
def root():
    return {"message": "Servicio 2 activo y recolectando datos automáticamente"}


@app.get("/analyze")
def get_latest():
    if not data_history:
        return {"mensaje": "Aún no hay datos almacenados"}
    return data_history[-1]


@app.get("/historial")
def get_history():
    # ✅ Devuelve solo los últimos 20 registros
    return data_history[-20:] if len(data_history) > 20 else data_history
