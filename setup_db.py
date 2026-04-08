"""
setup_db.py — Inicializa la base de datos con las tablas y datos de prueba.
Ejecutar para reiniciar la base de datos y aplicar cambios en la estructura:

    python setup_db.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import config

SQL_STATEMENTS = [
    # --- 1. ELIMINAR TABLAS ANTIGUAS (Orden inverso a la creación por las FK) ---
    "DROP TABLE IF EXISTS Adopter;",
    "DROP TABLE IF EXISTS Dog;",
    "DROP TABLE IF EXISTS Person;",

    # --- 2. CREAR TABLAS NUEVAS ---
    """
    CREATE TABLE Person (
        id         INT AUTO_INCREMENT PRIMARY KEY,
        name       VARCHAR(100),
        lastName   VARCHAR(100),
        age        INT,
        dateOfBirth DATE,
        id_card    VARCHAR(20) UNIQUE,
        cel        BIGINT,
        email      VARCHAR(100)
    )
    """,
    """
    CREATE TABLE Dog (
        id      INT AUTO_INCREMENT PRIMARY KEY,
        name    VARCHAR(50),
        age     INT,
        adopted BOOLEAN DEFAULT FALSE,
        breed   VARCHAR(50),
        photo   VARCHAR(255)
    )
    """,
    # FIX: se agregó dog_id (con FK a Dog) que faltaba en la definición original
    """
    CREATE TABLE Adopter (
        person_id INT PRIMARY KEY,
        address   VARCHAR(200),
        dog_id    INT NOT NULL,
        FOREIGN KEY (person_id) REFERENCES Person(id),
        FOREIGN KEY (dog_id) REFERENCES Dog(id)
    )
    """,
    
    # --- 3. INSERTAR DATOS DE PRUEBA ---
    """
    INSERT IGNORE INTO Dog (id, name, age, breed) VALUES
        (1, 'Firulais', 3, 'Labrador'),
        (2, 'Rex',      5, 'Pastor Alemán'),
        (3, 'Luna',     2, 'Husky')
    """
]

def run():
    conn = config.get_db_connection()
    if not conn:
        print("[ERROR] No se pudo conectar. Revisa tu configuración en app/config.py")
        sys.exit(1)

    cur = conn.cursor()
    for sql in SQL_STATEMENTS:
        try:
            cur.execute(sql)
        except Exception as e:
            print(f"[WARN] Error ejecutando sentencia: {e}")

    conn.commit()
    conn.close()
    print("[OK] Base de datos reiniciada e inicializada correctamente.")

if __name__ == '__main__':
    run()