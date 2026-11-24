# RAG Agricultura

Backend de la aplicación agrícola con FastAPI, PostgreSQL, Ollama, Chroma y un modelo YOLO.

## Requisitos

- Git
- Docker Engine y Docker Compose (plugin `docker compose`)
- Una base de datos PostgreSQL accesible desde el backend y con conexión SSL
- Acceso a Ollama. El proyecto configura el servicio Ollama en Compose; la respuesta RAG usa `nomic-embed-text` para embeddings y `gpt-oss:120b-cloud` para generar respuestas.

> **Importante antes de iniciar:** el `requirements.txt` actual incluye una primera línea (`pip requirements`) que no es un comentario ni un paquete instalable. Cámbiala por un comentario o elimínala. Además, `app.py` importa `resend`; confirma que esa dependencia esté instalada (añade `resend` a `requirements.txt` si hace falta) antes de construir la imagen. Si el build muestra otro módulo faltante, instala y agrega la dependencia indicada al mismo archivo.

## Ejecución con Docker Compose

1. **Clona el repositorio y entra en su directorio:**

   ```bash
   git clone https://github.com/joimar755/Rag_Agricultura.git
   cd Rag_Agricultura
   ```

2. **Configura las variables de entorno.** Crea un archivo `.env` en la raíz del proyecto (al mismo nivel que `docker-compose.yml`):

   ```dotenv
   DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST:5432/NOMBRE_BD?sslmode=require
   OLLAMA_HOST=http://ollama:11434
   ```

   Sustituye los valores de PostgreSQL por los de una base de datos real. La URL debe ser accesible desde el contenedor. No subas `.env` ni credenciales al repositorio.

3. **Construye y levanta los servicios:**

   ```bash
   docker compose up --build
   ```

   El primer build puede tardar porque instala dependencias de Python y YOLO. Compose inicia la API y Ollama; el servicio de base de datos no está incluido en `docker-compose.yml`, así que debes proporcionar PostgreSQL por separado.

4. **Descarga el modelo de embeddings** en el contenedor de Ollama (necesario para la preparación del índice RAG):

   ```bash
   docker compose exec ollama ollama pull nomic-embed-text
   ```

   La primera inicialización del backend carga `manual_agricola.pdf` y puede crear el índice local de Chroma. El directorio persistente se monta en `./data/chroma_db`.

5. **Verifica que la API esté arriba** abriendo <http://localhost:8000/docs>. La documentación interactiva de FastAPI permite probar las rutas disponibles.

6. **Detén los contenedores** cuando termines:

   ```bash
   docker compose down
   ```

   Para conservar el índice de Ollama, no añadas `-v`; ese comando eliminaría los volúmenes nombrados.

## Ejecución local (sin contenedor para la API)

1. Completa los pasos 1 y 2 anteriores, usando `OLLAMA_HOST=http://localhost:11434` en `.env`.
2. Inicia Ollama en tu equipo y asegúrate de que tenga disponible `nomic-embed-text`. El modelo de generación configurado es `gpt-oss:120b-cloud`; verifica el acceso y la autenticación requeridos por Ollama para usar modelos cloud.
3. Crea y activa un entorno virtual, instala las dependencias y arranca el servidor:

   ```bash
   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install resend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

   Si agregaste `resend` a `requirements.txt`, puedes omitir el `pip install resend` separado. Si falla la instalación por la primera línea de `requirements.txt`, corrígela como se explica en la nota de requisitos.

4. Abre <http://localhost:8000/docs> para probar la API.

## Notas de configuración

- `DATABASE_URL` es obligatoria: la aplicación crea las tablas al iniciar y `database.py` configura SSL (`sslmode=require`).
- `OLLAMA_HOST` debe apuntar al nombre del servicio dentro de Docker (`http://ollama:11434`) o a Ollama en el host (`http://localhost:11434`) cuando la API corre localmente.
- `app.py` carga `modelo_crop_recommendation.joblib` y `best.pt` desde la raíz, y el módulo RAG carga `manual_agricola.pdf`. Mantén esos archivos disponibles en el directorio de trabajo.
- El archivo Compose no configura un servicio PostgreSQL ni descarga automáticamente los modelos de Ollama.
- Revisa y rota las credenciales de servicios que hayan sido incluidas directamente en archivos versionados; configúralas mediante variables de entorno y no publiques secretos.
