# Instrucciones para Ejecutar el Sistema FAQ-Bot con PostgreSQL

Este documento proporciona instrucciones paso a paso para descargar, configurar y ejecutar el sistema FAQ-Bot con TF-IDF y PostgreSQL desde cero.

## 1. Requisitos Previos

Asegúrate de tener instalado:

- Python 3.10 o superior
- Git
- PostgreSQL 12 o superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## 2. Descargar el Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ia-faq-bot.git

# Entrar al directorio del proyecto
cd ia-faq-bot
```

## 3. Configurar el Entorno

### Paso 1: Entorno Python

```bash
# Crear un entorno virtual (recomendado)
python3 -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar PostgreSQL

```bash
# Verificar que PostgreSQL esté en ejecución
# En Linux:
sudo systemctl status postgresql
# En Windows: verificar en el Administrador de servicios

# Crear la base de datos (desde la terminal)
sudo -u postgres psql -c "CREATE DATABASE DefensaIA;"

# O conectarse manualmente a PostgreSQL y crear la base de datos
sudo -u postgres psql
CREATE DATABASE "DefensaIA";
\q
```

### Paso 3: Migrar datos y crear tablas

```bash
# Ejecutar el script de migración (crea tablas y migra datos iniciales)
python migrate_to_postgres.py
```

## 4. Entrenar el Índice TF-IDF

Este paso es necesario para crear el modelo de vectorización TF-IDF y los vectores de preguntas:

```bash
python3 train_index.py
```

Deberías ver un mensaje confirmando que el índice se ha creado correctamente.

## 5. Iniciar el Servidor API

```bash
# Iniciar el servidor FastAPI (por defecto en el puerto 8000)
uvicorn api:app --reload

# Si el puerto 8000 está ocupado, puedes especificar otro puerto:
uvicorn api:app --reload --port 8001
```

## 6. Iniciar el Servidor Web

Abre una nueva terminal (manteniendo la anterior ejecutando el servidor API) y ejecuta:

```bash
# Navegar al directorio web
cd web

# Iniciar un servidor web simple
python3 -m http.server 5500
```

## 7. Acceder a la Interfaz Web

Abre tu navegador y visita:

- Para la interfaz de usuario: [http://localhost:5500](http://localhost:5500)
- Para la documentación de la API: [http://localhost:8000/docs](http://localhost:8000/docs) (o el puerto que hayas configurado)

## 8. Uso del Sistema

### Pestaña de Chat
- Escribe tu pregunta en el campo de texto y presiona Enter o haz clic en "Enviar"
- El sistema buscará la respuesta más similar usando TF-IDF y similitud coseno

### Pestaña de Administración
- Ver todas las FAQs existentes
- Añadir nuevas FAQs con el botón "Añadir FAQ"
- Editar FAQs existentes con el botón "Editar"
- Eliminar FAQs con el botón "Eliminar"
- Recargar el índice TF-IDF después de cambios con el botón "Recargar Índice"

## 9. Ajustes de Configuración

Si necesitas modificar la configuración del sistema:

- **Umbral de confianza**: En `api.py`, modifica la constante `CONFIDENCE_THRESHOLD`
- **Puerto de la API**: Cambia el puerto al iniciar uvicorn con `--port XXXX`
- **URL de la API**: Si cambias el puerto, actualiza también `API_BASE` en `web/index.html`

## 10. Solución de Problemas

### Problemas con el servidor API

#### Error: "Address already in use"
Significa que el puerto ya está siendo utilizado. Intenta con un puerto diferente:
```bash
uvicorn api:app --reload --port 8001
```
Y actualiza `API_BASE` en `web/index.html` para que coincida con el nuevo puerto.

#### Error: "No module named X"
Asegúrate de haber instalado todas las dependencias:
```bash
pip install -r requirements.txt
```

### Problemas con PostgreSQL

#### Error: "could not connect to server"
Verifica que PostgreSQL esté en ejecución:
```bash
# En Linux
sudo systemctl status postgresql
# Si está detenido, iniciálo
sudo systemctl start postgresql
```

#### Error: "database DefensaIA does not exist"
La base de datos no ha sido creada. Crea la base de datos:
```bash
sudo -u postgres psql -c "CREATE DATABASE DefensaIA;"
```

#### Error: "relation faq does not exist"
Las tablas no han sido creadas. Ejecuta el script de migración:
```bash
python migrate_to_postgres.py
```

#### Error: "password authentication failed for user postgres"
Verifica las credenciales en los archivos `api.py`, `train_index.py` y `migrate_to_postgres.py`. Por defecto se usa:
- Usuario: `postgres`
- Contraseña: `postgres`

Si necesitas cambiar las credenciales, modifica estos archivos o configura tu usuario PostgreSQL con estas credenciales.

## 11. Detener el Sistema

Para detener los servidores, presiona `Ctrl+C` en cada terminal donde estén ejecutándose.

---

¡Listo! Ahora deberías tener el sistema FAQ-Bot funcionando correctamente. Si tienes alguna pregunta o problema, consulta la documentación adicional en el archivo README.md.
