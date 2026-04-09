🐾 Centro de Adopción - Guía de Instalación con Docker

Este proyecto utiliza Docker para garantizar que el entorno de desarrollo sea idéntico en cualquier máquina. Al usar contenedores, eliminamos la necesidad de configurar entornos virtuales (venv) o instalar dependencias de Python directamente en tu sistema operativo.

🚀 Requisitos Previos

Asegúrate de tener instalados Docker y Docker Compose en tu sistema operativo (probado en Ubuntu y CachyOS):

# 1. Actualizar el sistema e instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# 2. Configurar permisos (Opcional: permite ejecutar docker sin 'sudo')
sudo usermod -aG docker $USER
# Nota: Debes cerrar sesión y volver a entrar para que este cambio surja efecto.


🛠️ Pasos para Iniciar el Proyecto

Sigue estos pasos para levantar la aplicación desde cero:

1. Clonar el repositorio

git clone <URL_DEL_REPOSITORIO>
cd CentroAdopcion


2. Construir y Levantar los Contenedores

Este comando descargará la imagen de MariaDB, construirá tu imagen personalizada de Python e iniciará ambos servicios en segundo plano.

docker-compose up --build -d


3. Inicializar la Base de Datos

Una vez que los contenedores estén en estado "Up", ejecuta el script para crear las tablas y registros iniciales dentro del contenedor de la aplicación:

docker exec -it centroadopcion-app-1 python setup_db.py


🖥️ Acceso a la Aplicación

Una vez completados los pasos anteriores, abre tu navegador y entra a:
👉 http://localhost:5000

📊 Comandos Útiles de Mantenimiento

Acción                                          Comando



Ver logs en tiempo real             docker logs -f centroadopcion-app-1



Reiniciar la aplicación              docker-compose restart app



Ver estado de servicios                      docker ps



Detener contenedores                    docker-compose stop



Borrar todo (incluyendo datos)          docker-compose down -v



📝 Notas de Desarrollo

Persistencia de Datos: Los datos de MariaDB se almacenan en un volumen de Docker llamado db_data. Esto significa que aunque detengas o borres los contenedores, tus datos de adopción se mantendrán guardados.

Sincronización de Código: Hemos configurado un volumen que vincula tu carpeta local con /app dentro del contenedor. Si Flask está en modo Debug, la mayoría de los cambios que guardes en tus archivos .py o .html se verán reflejados al instante sin reiniciar el contenedor.

Variables de Entorno: Las credenciales de la base de datos están centralizadas en el archivo docker-compose.yml.
Preview de la app


![Captura de pantalla](imagenes/1ca.png)
![Captura de pantalla](imagenes/2ca.png)
![Captura de pantalla](imagenes/3ca.png)
![Captura de pantalla](imagenes/4ca.png)
![Captura de pantalla](imagenes/5ca.png)
![Captura de pantalla](imagenes/6ca.png)
![Captura de pantalla](imagenes/7ca.png)
![Captura de pantalla](imagenes/8ca.png)