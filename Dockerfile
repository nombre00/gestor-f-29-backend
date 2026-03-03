# ==============================================================================
# GESTOR F29 - Dockerfile
# ==============================================================================

# ------------------------------------------------------------------------------
# Imagen base: Python 3.10 oficial, variante "slim"
# "slim" es una versión reducida de Debian, sin herramientas innecesarias.
# Pesa mucho menos que la imagen completa y es suficiente para correr FastAPI.
# ------------------------------------------------------------------------------
FROM python:3.10-slim

# ------------------------------------------------------------------------------
# Directorio de trabajo dentro del contenedor.
# Todos los comandos siguientes se ejecutan desde esta ruta.
# ------------------------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------------------------
# Variables de entorno para Python:
#   PYTHONDONTWRITEBYTECODE=1  → No genera archivos .pyc (bytecode cacheado).
#                                Innecesarios dentro de un contenedor.
#   PYTHONUNBUFFERED=1         → Los print() y logs aparecen en tiempo real
#                                en la terminal de Docker, sin buffer.
# ------------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Le indica a Python que busque módulos también dentro de /app/src
ENV PYTHONPATH=/app/src

# ------------------------------------------------------------------------------
# Instalar dependencias del sistema operativo.
# El backend usa PyMySQL (puro Python) así que no necesita el cliente MySQL.
# Solo instalamos gcc por si alguna dependencia de pip necesita compilar algo.
# El flag --no-install-recommends evita instalar paquetes sugeridos innecesarios.
# El "rm -rf /var/lib/apt/lists/*" limpia la caché de apt para reducir el tamaño
# final de la imagen.
# ------------------------------------------------------------------------------
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# Copiar primero SOLO el requirements.txt, antes que el resto del código.
# Esto aprovecha el sistema de caché de Docker: si el requirements.txt no
# cambió, Docker reutiliza la capa de instalación de dependencias en vez de
# reinstalar todo desde cero cada vez que cambias una línea de código.
# ------------------------------------------------------------------------------
COPY requirements.txt .

# ------------------------------------------------------------------------------
# Instalar las dependencias de Python.
# --no-cache-dir: no guarda la caché de pip dentro de la imagen (ahorra espacio).
# --upgrade pip: asegura que pip esté actualizado antes de instalar.
# ------------------------------------------------------------------------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Copiar el resto del código fuente al contenedor.
# El .dockerignore (que crearemos después) controla qué archivos se excluyen
# de esta copia.
# ------------------------------------------------------------------------------
COPY . .

# ------------------------------------------------------------------------------
# Puerto que expone el contenedor.
# Es solo documentación para Docker, no abre el puerto por sí solo.
# El mapeo real se define en docker-compose.yml.
# ------------------------------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------------------------------
# Comando que ejecuta el contenedor al iniciarse.
# Usamos uvicorn directamente en vez de "python main.py" porque es más estable
# en producción.
#   --host 0.0.0.0   → Escucha en todas las interfaces de red del contenedor,
#                       necesario para que Docker pueda enrutar el tráfico.
#   --port 8000      → Puerto donde corre la app.
#   src.f29_backend.main:app → Ruta al objeto FastAPI dentro del proyecto.
# Sin --reload, porque en producción no queremos que el servidor se reinicie
# automáticamente al detectar cambios en archivos.
# ------------------------------------------------------------------------------
CMD ["uvicorn", "src.f29_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
