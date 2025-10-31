"""
Script de migración para vincular los registros de signos vitales con pacientes.
Actualiza los documentos en la colección 'signos_vitales' agregando el campo 'paciente_id'.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise RuntimeError("❌ Falta configurar MONGO_URI o DB_NAME en las variables de entorno")

client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

pacientes_collection = db["pacientes"]
signos_collection = db["signos_vitales"]

def migrar_signos():
    signos = list(signos_collection.find({}))
    total = len(signos)
    actualizados = 0
    sin_paciente = 0

    print(f"🔍 Iniciando migración de {total} registros de signos vitales...\n")

    for signo in signos:
        cedula = signo.get("cedula")

        if not cedula:
            print(f"⚠️ Registro sin cédula: {signo.get('_id')}")
            sin_paciente += 1
            continue

        paciente = pacientes_collection.find_one({"cedula": cedula})

        if paciente:
            update_data = {
                "paciente_id": str(paciente["_id"]),
                "nombre": f"{paciente.get('nombre')} {paciente.get('apellido', '')}".strip()
            }

            signos_collection.update_one(
                {"_id": signo["_id"]},
                {"$set": update_data}
            )
            actualizados += 1
            print(f"✅ Vinculado signo vital de cédula {cedula} con paciente {update_data['nombre']}")
        else:
            print(f"⚠️ No se encontró paciente con cédula {cedula}")
            sin_paciente += 1

    print("\n🏁 Migración completada.")
    print(f"✅ Registros actualizados: {actualizados}")
    print(f"⚠️ Registros sin paciente: {sin_paciente}")

if __name__ == "__main__":
    migrar_signos()
