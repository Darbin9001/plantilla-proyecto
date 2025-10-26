from fastapi import FastAPI
import random
from datetime import datetime
from services.data_base_mongo import db
from services.utils import serialize_mongo


app = FastAPI(title="Servicio 1 - Generador de Datos de Salud")

@app.get("/")
def root():
    return {"message": "Servicio 1 activo"}

@app.get("/health-data")
def get_health_data():
    # Generar datos aleatorios simulados
    lectura = {
        "ritmo_cardiaco": random.randint(60, 120),
        "temperatura": round(random.uniform(36, 39), 1),
        "presion": f"{random.randint(100,130)}/{random.randint(70,90)}",
        "oxigeno": random.randint(90, 100),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Guardar en MongoDB si la conexión existe
    if db is not None:
        try:
            db["lecturas"].insert_one(lectura)
            print("📥 Lectura guardada en MongoDB:", lectura)
        except Exception as e:
            print("⚠️ Error guardando en MongoDB:", e)
    else:
        print("⚠️ No hay conexión activa con MongoDB")

    # Serializar campos no JSON-serializables (ObjectId, etc.) antes de devolver
    lectura_serializada = serialize_mongo(lectura)
    return {"status": "ok", "lectura": lectura_serializada}
