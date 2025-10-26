from fastapi import FastAPI
from data_generator import generar_datos_vitales
from models import DatosVitales

app = FastAPI(title="Servicio de Datos Vitales", version="1.0")

@app.get("/vitals/latest", response_model=DatosVitales)
def obtener_datos_vitales():
    """Devuelve los últimos signos vitales simulados"""
    return generar_datos_vitales()

@app.get("/")
def raiz():
    return {"mensaje": "Servicio de datos vitales activo ✅"}
