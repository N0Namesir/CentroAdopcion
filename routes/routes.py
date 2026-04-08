import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

# Importamos desde la carpeta 'app' (main.py se encargará de que sea visible)
from app import database
from app import models

# Creamos el Blueprint en lugar de la App
routes_bp = Blueprint('routes', __name__)

# --- CONFIGURACIÓN DE UTILIDADES ---
# Nota: Ahora usamos current_app para acceder a la config global
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_photo_filename(dog_id, original_filename):
    ext  = original_filename.rsplit('.', 1)[1].lower()
    base = secure_filename(original_filename.rsplit('.', 1)[0]) or 'foto'
    return f"{dog_id}_{base}.{ext}"

def delete_photo_file(filename):
    if filename:
        # Usamos current_app.static_folder para obtener la ruta correcta
        path = os.path.join(current_app.static_folder, 'uploads', 'dogs', filename)
        if os.path.isfile(path):
            os.remove(path)

# ─── RUTAS PÚBLICAS ──────────────────────────────────────────────────────────

@routes_bp.route('/')
def index():
    dogs_data      = database.get_available_dogs()
    available_dogs = [models.Dog(r[0], r[1], r[2], r[3], photo=r[4]) for r in dogs_data]
    return render_template('catalogo.html', dogs=available_dogs)


@routes_bp.route('/adoptar/<int:dog_id>')
def form_adopcion(dog_id):
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404
    if dog_data[4]:
        return render_template('error.html', mensaje="Este perrito ya fue adoptado. ¡Qué buena noticia!"), 400
    dog = models.Dog(dog_data[0], dog_data[1], dog_data[2], dog_data[3], photo=dog_data[5])
    return render_template('confirmacion.html', dog=dog)


@routes_bp.route('/confirmar_adopcion', methods=['POST'])
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

@routes_bp.route('/admin')
def admin():
    all_dogs  = database.get_all_dogs()
    adoptions = database.get_all_adoptions()
    dogs_objs = [models.Dog(r[0], r[1], r[2], r[3], r[4], photo=r[5]) for r in all_dogs]
    return render_template('admin.html', dogs=dogs_objs, adoptions=adoptions)


@routes_bp.route('/admin/agregar_perro', methods=['POST'])
def agregar_perro():
    name  = request.form['name'].strip()
    age   = request.form['age'].strip()
    breed = request.form['breed'].strip()

    if not all([name, age, breed]):
        return render_template('error.html', mensaje="Todos los campos del perro son obligatorios."), 400

    success = database.add_dog(name, age, breed)
    if not success:
        return render_template('error.html', mensaje="No se pudo agregar el perro."), 500

    # Si se adjuntó foto, guardarla
    file = request.files.get('photo')
    if file and file.filename and allowed_file(file.filename):
        # Obtener el ID del perro recién creado (el más reciente)
        all_dogs = database.get_all_dogs()
        if all_dogs:
            new_dog_id = all_dogs[0][0]  # ORDER BY id DESC → primero es el más nuevo
            filename = build_photo_filename(new_dog_id, file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            database.update_dog_photo(new_dog_id, filename)

    flash(f'¡{name} fue agregado al catálogo exitosamente!', 'success')
    return redirect(url_for('routes.admin'))


@routes_bp.route('/admin/eliminar/<int:dog_id>', methods=['POST'])
def eliminar_perro(dog_id):
    dog_data = database.get_dog_by_id(dog_id)
    if dog_data and dog_data[5]:
        delete_photo_file(dog_data[5])

    dog_name = dog_data[1] if dog_data else 'el perro'
    success  = database.delete_dog(dog_id)
    if success:
        flash(f'{dog_name} fue eliminado del catálogo.', 'warning')
        return redirect(url_for('routes.admin'))
    else:
        return render_template('error.html',
            mensaje="No se puede eliminar: el perro no existe o ya fue adoptado."), 400


# ─── RUTAS DE GESTIÓN DE FOTOS ────────────────────────────────────────────────

@routes_bp.route('/admin/foto/<int:dog_id>', methods=['POST'])
def actualizar_foto(dog_id):
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404

    file = request.files.get('photo')
    if not file or file.filename == '':
        return render_template('error.html', mensaje="No se seleccionó ninguna imagen."), 400

    if not allowed_file(file.filename):
        return render_template('error.html', mensaje="Formato no permitido. Usa JPG, PNG, WEBP o GIF."), 400

    old_photo = dog_data[5]
    if old_photo:
        delete_photo_file(old_photo)

    filename = build_photo_filename(dog_id, file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    database.update_dog_photo(dog_id, filename)
    flash(f'Foto de {dog_data[1]} actualizada.', 'success')
    return redirect(url_for('routes.admin'))


@routes_bp.route('/admin/foto/<int:dog_id>/quitar', methods=['POST'])
def quitar_foto(dog_id):
    dog_data = database.get_dog_by_id(dog_id)
    if not dog_data:
        return render_template('error.html', mensaje="Perrito no encontrado."), 404

    old_photo = dog_data[5]
    if old_photo:
        delete_photo_file(old_photo)
        database.update_dog_photo(dog_id, None)
        flash(f'Foto de {dog_data[1]} eliminada.', 'warning')

    return redirect(url_for('routes.admin'))