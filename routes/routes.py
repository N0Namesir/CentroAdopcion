import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import database
import models

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# ─── CONFIGURACIÓN DE UPLOADS ─────────────────────────────────────────────────

UPLOAD_FOLDER   = os.path.join(app.static_folder, 'uploads', 'dogs')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_photo_filename(dog_id, original_filename):
    """
    Genera un nombre de archivo seguro y único para cada perro.
    Formato: {dog_id}_{nombre_seguro}.{ext}
    Ejemplo: 3_luna.jpg
    """
    ext = original_filename.rsplit('.', 1)[1].lower()
    base = secure_filename(original_filename.rsplit('.', 1)[0]) or 'foto'
    return f"{dog_id}_{base}.{ext}"

def delete_photo_file(filename):
    """Elimina el archivo físico de disco si existe."""
    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            os.remove(path)


# ─── RUTAS PÚBLICAS ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    dogs_data = database.get_available_dogs()
    # get_available_dogs devuelve: id, name, age, breed, photo
    available_dogs = [models.Dog(r[0], r[1], r[2], r[3], photo=r[4]) for r in dogs_data]
    return render_template('catalogo.html', dogs=available_dogs)


@app.route('/adoptar/<int:dog_id>')
def form_adopcion(dog_id):
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404
    if dog_data[4]:  # adopted == True
        return render_template('error.html', mensaje="Este perrito ya fue adoptado. ¡Qué buena noticia!"), 400
    # get_dog_by_id devuelve: id, name, age, breed, adopted, photo
    dog = models.Dog(dog_data[0], dog_data[1], dog_data[2], dog_data[3], photo=dog_data[5])
    return render_template('confirmacion.html', dog=dog)


@app.route('/confirmar_adopcion', methods=['POST'])
def procesar_adopcion():
    dog_id   = request.form['dog_id']
    name     = request.form['name'].strip()
    lastname = request.form['lastname'].strip()
    address  = request.form['address'].strip()
    id_card  = request.form['id_card'].strip()

    if not all([name, lastname, address, id_card]):
        return render_template('error.html', mensaje="Todos los campos son obligatorios."), 400

    success = database.register_adoption_transactional(dog_id, name, lastname, address, id_card)

    if success:
        dog_data = database.get_dog_by_id(dog_id)
        dog = models.Dog(dog_data[0], dog_data[1], dog_data[2], dog_data[3], photo=dog_data[5])
        return render_template('exito.html', dog=dog, adopter_name=name)
    else:
        return render_template('error.html',
            mensaje="Error al procesar la adopción. Es posible que la cédula ya esté registrada."), 500


# ─── RUTAS DE ADMINISTRACIÓN ─────────────────────────────────────────────────

@app.route('/admin')
def admin():
    all_dogs  = database.get_all_dogs()
    adoptions = database.get_all_adoptions()
    # get_all_dogs devuelve: id, name, age, breed, adopted, photo
    dogs_objs = [models.Dog(r[0], r[1], r[2], r[3], r[4], photo=r[5]) for r in all_dogs]
    return render_template('admin.html', dogs=dogs_objs, adoptions=adoptions)


@app.route('/admin/agregar_perro', methods=['POST'])
def agregar_perro():
    name  = request.form['name'].strip()
    age   = request.form['age'].strip()
    breed = request.form['breed'].strip()

    if not all([name, age, breed]):
        return render_template('error.html', mensaje="Todos los campos del perro son obligatorios."), 400

    success = database.add_dog(name, age, breed)
    if success:
        return redirect(url_for('admin'))
    else:
        return render_template('error.html', mensaje="No se pudo agregar el perro."), 500


@app.route('/admin/eliminar/<int:dog_id>', methods=['POST'])
def eliminar_perro(dog_id):
    # Borrar foto del disco antes de eliminar el registro
    dog_data = database.get_dog_by_id(dog_id)
    if dog_data and dog_data[5]:
        delete_photo_file(dog_data[5])

    success = database.delete_dog(dog_id)
    if success:
        return redirect(url_for('admin'))
    else:
        return render_template('error.html',
            mensaje="No se puede eliminar: el perro no existe o ya fue adoptado."), 400


# ─── RUTAS DE GESTIÓN DE FOTOS ────────────────────────────────────────────────

@app.route('/admin/foto/<int:dog_id>', methods=['POST'])
def actualizar_foto(dog_id):
    """Sube o reemplaza la foto de un perro."""
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404

    file = request.files.get('photo')
    if not file or file.filename == '':
        return render_template('error.html', mensaje="No se seleccionó ninguna imagen."), 400

    if not allowed_file(file.filename):
        return render_template('error.html',
            mensaje="Formato no permitido. Usa JPG, PNG, WEBP o GIF."), 400

    # Eliminar foto anterior si existe
    old_photo = dog_data[5]
    if old_photo:
        delete_photo_file(old_photo)

    # Guardar nueva foto
    filename = build_photo_filename(dog_id, file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    database.update_dog_photo(dog_id, filename)
    return redirect(url_for('admin'))


@app.route('/admin/foto/<int:dog_id>/quitar', methods=['POST'])
def quitar_foto(dog_id):
    """Elimina la foto de un perro (disco + DB)."""
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404

    old_photo = dog_data[5]
    if old_photo:
        delete_photo_file(old_photo)
        database.update_dog_photo(dog_id, None)

    return redirect(url_for('admin'))