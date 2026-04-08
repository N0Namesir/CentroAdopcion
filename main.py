import os
import sys
from flask import Flask

# Aseguramos que la carpeta raíz esté en el path para importar 'app' y 'routes'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from routes.routes import routes_bp

app = Flask(__name__)

# Configuración centralizada
app.secret_key = os.environ.get("SECRET_KEY", "adoptapets-dev-secret-2024")
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'dogs')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Creamos la carpeta de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registramos el Blueprint
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)