from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Intentar cargar .env desde la raíz del proyecto (una carpeta arriba de `services`)
here = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(here, os.pardir))
dotenv_path = os.path.join(project_root, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback: intentar cargar desde el cwd
    load_dotenv()

# Leer variables de entorno
# Si no hay MONGO_URI, conectamos al localhost por defecto
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME")

try:
    client = MongoClient(MONGO_URI)

    if DB_NAME:
        # Usar la DB especificada por la variable de entorno
        db = client[DB_NAME]
    else:
        # Intentar obtener la base de datos por defecto del URI (si existe)
        db = client.get_default_database()
        if db is None:
            # No hay DB configurada; no intentar indexar con None
            print("⚠️ DB_NAME no configurada y URI no contiene una base de datos por defecto. db será None.")

    if db is not None:
        print("✅ Conectado a MongoDB correctamente crack")
    else:
        print("⚠️ No hay conexión activa con MongoDB (db is None)")

except Exception as e:
    print("❌ Error al conectar con MongoDB:", e)
    db = None
