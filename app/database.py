import config

# ─── LECTURA ────────────────────────────────────────────────────────────────

def get_available_dogs():
    """Retorna todos los perros que aún no han sido adoptados."""
    conn = config.get_db_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, breed, photo FROM Dog WHERE adopted = FALSE")
    dogs = cur.fetchall()
    conn.close()
    return dogs

def get_all_dogs():
    """Retorna todos los perros (para el panel de admin)."""
    conn = config.get_db_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, breed, adopted, photo FROM Dog ORDER BY id DESC")
    dogs = cur.fetchall()
    conn.close()
    return dogs

def get_dog_by_id(dog_id):
    """Retorna un perro por su ID, o None si no existe."""
    conn = config.get_db_connection()
    if not conn: return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, breed, adopted, photo FROM Dog WHERE id = ?", (dog_id,))
    dog = cur.fetchone()
    conn.close()
    return dog

def get_all_adoptions():
    conn = config.get_db_connection()
    if not conn: return []
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, p.lastName, p.id_card, a.address, d.name, d.breed
        FROM Person p
        JOIN Adopter a ON p.id = a.person_id
        JOIN Dog d ON d.id = a.dog_id
        ORDER BY p.id DESC
    """)
    adoptions = cur.fetchall()
    conn.close()
    return adoptions

# ─── ESCRITURA ───────────────────────────────────────────────────────────────

def register_adoption_transactional(dog_id, adopter_name, adopter_lastname, address, id_card):
    """
    Ejecuta la adopción como una transacción atómica de 3 pasos:
      1. INSERT Person
      2. INSERT Adopter (hereda de Person)
      3. UPDATE Dog → adopted = TRUE
    Si cualquier paso falla, se revierte todo con rollback.
    """
    conn = config.get_db_connection()
    if not conn: return False

    cur = conn.cursor()
    try:
        conn.autocommit = False

        cur.execute(
            "INSERT INTO Person (name, lastName, id_card) VALUES (?, ?, ?)",
            (adopter_name, adopter_lastname, id_card)
        )
        person_id = cur.lastrowid

        cur.execute(
            "INSERT INTO Adopter (person_id, address, dog_id) VALUES (?, ?, ?)",
            (person_id, address, dog_id)
        )

        cur.execute(
            "UPDATE Dog SET adopted = TRUE WHERE id = ?",
            (dog_id,)
        )

        conn.commit()
        return True

    except Exception as e:
        print(f"[ERROR] Transacción de adopción fallida: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_dog(name, age, breed):
    """Inserta un nuevo perro en el catálogo."""
    conn = config.get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Dog (name, age, breed) VALUES (?, ?, ?)",
            (name, int(age), breed)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo agregar el perro: {e}")
        return False
    finally:
        conn.close()

def delete_dog(dog_id):
    """
    Elimina un perro solo si NO ha sido adoptado.
    Retorna True si se eliminó, False si ya estaba adoptado o hubo error.
    """
    conn = config.get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute("SELECT adopted FROM Dog WHERE id = ?", (dog_id,))
        row = cur.fetchone()
        if not row or row[0]:
            return False

        cur.execute("DELETE FROM Dog WHERE id = ?", (dog_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar el perro: {e}")
        return False
    finally:
        conn.close()

def update_dog_photo(dog_id, filename):
    """
    Actualiza el campo photo de un perro.
    Pasa filename=None para borrar la foto.
    """
    conn = config.get_db_connection()
    if not conn: return False
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE Dog SET photo = ? WHERE id = ?",
            (filename, dog_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar la foto del perro: {e}")
        return False
    finally:
        conn.close()