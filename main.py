import sys
import os

# Agregar la carpeta 'app/' al path para que los imports de database/models resuelvan
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from routes.routes import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)