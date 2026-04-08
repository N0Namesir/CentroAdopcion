# Fix: Problemas de conexión y permisos en contenedores Docker + MariaDB

## 1. Limpiar todo (contenedores, volúmenes, huérfanos)

```bash
sudo docker compose down -v --remove-orphans
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null || true
sudo docker volume prune -f
```

## 2. Liberar el puerto 3306 si está ocupado

```bash
sudo ss -tlnp | grep 3306
sudo systemctl stop mariadb 2>/dev/null || true
```

## 3. Levantar los contenedores limpios

```bash
sudo docker compose up -d --build
```

## 4. Verificar que MariaDB esté lista

```bash
sudo docker compose logs db
# Esperar hasta ver: "ready for connections"
```

## 5. Si el error es "Access denied" — otorgar permisos manualmente

Entrar como root al contenedor de MariaDB:

```bash
sudo docker compose exec db mariadb -u root -p<ROOT_PASSWORD>
```

Dentro del prompt de MariaDB:

```sql
GRANT ALL PRIVILEGES ON <NOMBRE_DB>.* TO '<USUARIO>'@'%';
FLUSH PRIVILEGES;
EXIT;
```

## 6. Si el error es "Can't connect through socket" — forzar TCP

El error ocurre cuando `host=localhost` intenta conectarse por socket unix en vez de red.
Cambia `localhost` por `127.0.0.1` en la configuración de la app.

---

## ¿Por qué pasa el error de "Access denied"?

Docker crea el usuario con permisos **solo sobre la base de datos definida en `MARIADB_DATABASE`**
al momento de crear el volumen por primera vez. Si cambias el nombre de la DB después,
el usuario queda sin permisos sobre la nueva — aunque hagas `down -v`, a veces quedan
volúmenes huérfanos cacheados. El `GRANT` manual del paso 5 lo resuelve.