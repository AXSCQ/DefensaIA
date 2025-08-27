# Instrucciones para Ejecutar el Sistema FAQ-Bot

Este documento proporciona instrucciones paso a paso para descargar, configurar y ejecutar el sistema FAQ-Bot con TF-IDF desde cero.

## 1. Requisitos Previos

Asegúrate de tener instalado:

- Python 3.10 o superior
- Git
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## 2. Descargar el Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ia-faq-bot.git

# Entrar al directorio del proyecto
cd ia-faq-bot
```

## 3. Configurar el Entorno

### Opción A: Entorno Virtual (recomendado)

```bash
# Crear un entorno virtual
python3 -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción B: Instalación Global

```bash
# Instalar dependencias globalmente
pip3 install -r requirements.txt
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

### Error: "Address already in use"
Significa que el puerto ya está siendo utilizado. Intenta con un puerto diferente:
```bash
uvicorn api:app --reload --port 8001
```
Y actualiza `API_BASE` en `web/index.html` para que coincida con el nuevo puerto.

### Error: "No module named X"
Asegúrate de haber instalado todas las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "No se pueden cargar las FAQs"
Verifica que el archivo `data/faqs.json` existe y tiene el formato correcto.

## 11. Detener el Sistema

Para detener los servidores, presiona `Ctrl+C` en cada terminal donde estén ejecutándose.

---

¡Listo! Ahora deberías tener el sistema FAQ-Bot funcionando correctamente. Si tienes alguna pregunta o problema, consulta la documentación adicional en el archivo README.md.
