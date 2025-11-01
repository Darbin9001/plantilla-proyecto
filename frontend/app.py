from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura_aqui'  # Cambiar en producción

SERVICE2_URL = "http://127.0.0.1:8002/historial"
# Si usas Docker Compose: SERVICE2_URL = "http://service2:8002/historial"

# Simulación de base de datos en memoria (reemplazar con DB real)
usuarios_db = {
    '123456789': {
        'cedula': '123456789',
        'nombre': 'Juan Pérez',
        'email': 'juan@example.com',
        'telefono': '3001234567',
        'password': 'paciente123',
        'rol': 'paciente'
    },
    'doc001': {
        'cedula': 'doc001',
        'nombre': 'Dr. María González',
        'email': 'maria@hospital.com',
        'telefono': '3009876543',
        'password': 'medico123',
        'rol': 'medico',
        'especialidad': 'Cardiología'
    }
}

pacientes_db = [
    {'cedula': '123456789', 'nombre': 'Juan Pérez'},
    {'cedula': '987654321', 'nombre': 'Ana Martínez'},
    {'cedula': '555666777', 'nombre': 'Carlos López'}
]

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar rol
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login_page'))
            if session['user'].get('rol') != role:
                return jsonify({"error": "Acceso denegado"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============= RUTAS DE AUTENTICACIÓN =============

@app.route("/")
def home():
    """Redirige según el estado de sesión"""
    if 'user' in session:
        rol = session['user'].get('rol')
        if rol == 'paciente':
            return redirect(url_for('paciente_dashboard'))
        elif rol == 'medico':
            return redirect(url_for('medico_dashboard'))
    return redirect(url_for('login_page'))

@app.route("/login")
def login_page():
    """Muestra la página de login"""
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def login():
    """Procesa el login"""
    data = request.get_json()
    cedula = data.get('cedula')
    password = data.get('password')
    
    if not cedula or not password:
        return jsonify({"success": False, "message": "Faltan datos"}), 400
    
    # Verificar credenciales
    usuario = usuarios_db.get(cedula)
    if usuario and usuario['password'] == password:
        # Crear sesión
        session['user'] = {
            'cedula': usuario['cedula'],
            'nombre': usuario['nombre'],
            'rol': usuario['rol'],
            'especialidad': usuario.get('especialidad', '')
        }
        return jsonify({
            "success": True,
            "rol": usuario['rol'],
            "message": "Login exitoso"
        })
    
    return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

@app.route("/registro")
def registro_page():
    """Muestra la página de registro"""
    return render_template("registro.html")

@app.route("/registro", methods=['POST'])
def registro():
    """Procesa el registro de nuevos pacientes"""
    data = request.get_json()
    cedula = data.get('cedula')
    nombre = data.get('nombre')
    email = data.get('email')
    telefono = data.get('telefono')
    password = data.get('password')
    
    if not all([cedula, nombre, email, telefono, password]):
        return jsonify({"success": False, "message": "Faltan datos"}), 400
    
    # Verificar si ya existe
    if cedula in usuarios_db:
        return jsonify({"success": False, "message": "La cédula ya está registrada"}), 400
    
    # Registrar nuevo usuario
    usuarios_db[cedula] = {
        'cedula': cedula,
        'nombre': nombre,
        'email': email,
        'telefono': telefono,
        'password': password,
        'rol': 'paciente'
    }
    
    # Agregar a lista de pacientes
    pacientes_db.append({'cedula': cedula, 'nombre': nombre})
    
    return jsonify({"success": True, "message": "Registro exitoso"})

@app.route("/logout")
def logout():
    """Cierra la sesión"""
    session.pop('user', None)
    return redirect(url_for('login_page'))

# ============= DASHBOARDS =============

@app.route("/paciente/dashboard")
@role_required('paciente')
def paciente_dashboard():
    """Dashboard para pacientes"""
    user = session['user']
    return render_template("paciente_dashboard.html", user=user)

@app.route("/medico/dashboard")
@role_required('medico')
def medico_dashboard():
    """Dashboard para médicos"""
    user = session['user']
    return render_template("medico_dashboard.html", user=user)

# ============= APIs =============

@app.route("/api/data/<cedula>")
@login_required
def get_data(cedula):
    """Obtiene el historial de salud por cédula"""
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

@app.route("/api/pacientes")
@role_required('medico')
def get_pacientes():
    """Lista todos los pacientes (solo para médicos)"""
    return jsonify(pacientes_db)

# ============= PÁGINAS DE ERROR =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)