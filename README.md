passos para copiar esta cosa

cachyos
# 1. Instalar dependencias del sistema
sudo pacman -S docker docker-compose python mariadb-libs

# 2. Habilitar Docker
sudo systemctl enable --now docker

# 3. Clonar el repo
git clone https://github.com/N0Namesir/ProyectoPerro.git
cd ProyectoPerro

# 4. Levantar MariaDB
sudo docker compose up -d

# 5. Crear venv e instalar dependencias
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Crear las tablas
python setup_db.py

# 7. Correr la app
python main.py


ubuntu

# 1. Instalar dependencias del sistema
sudo apt update
sudo apt install docker.io docker-compose python3 python3-pip python3-venv libmariadb-dev

# 2. Habilitar Docker
sudo systemctl enable --now docker

# 3. Clonar el repo
git clone https://github.com/N0Namesir/ProyectoPerro.git
cd ProyectoPerro

# 4. Levantar MariaDB
sudo docker compose up -d

# 5. Crear venv e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Crear las tablas
python3 setup_db.py

# 7. Correr la app
python3 main.py