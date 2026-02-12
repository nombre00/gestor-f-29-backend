# Punto de entrada del código.

# Recordatorios.
# Version 1:
# Models: clases que se mapean a la base de datos.
# Repositories: accesadores.
# Services: lógica de negocios.
# Controller: endpoints.
# Domain/Entities: clases de java típicas.
# Schemas: clases de input y output de la api, valida datos, protege datos internos, genera documentación (por lo que entiendo).

# Flujo típico de trabajo: Flujo típico: Frontend envía schema → Controller valida → Service usa domain para lógica → Repository mapea a model y guarda → Retorna schema.


# Version 2:
# Api: endpoints, incluye las carpetas schemas y la carpeta routers (controllers).
# application: lógica de negocio, incluye la carpeta services (orquestación, se llama funciones de otras partes).
# Domain/entities: modelos del negocio, clases tipicas de java.
# Infrastructure: incluye adaptadores (parsers y writers) y presistencia: archivo conección y carpetas: models y repository




# Para correr por terminal:   uvicorn src.f29_backend.main:app --reload --port 5000



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa tus routers
from f29_backend.api.routers import gestorF29Router  
from f29_backend.api.routers import vistaResumenF29Router

# Crea la aplicación FastAPI
app = FastAPI(
    title="API Gestor F29 - SII",
    description="Backend para procesar y generar resúmenes Formulario 29",
    version="0.1.0",
    docs_url="/docs",           # Swagger UI en /docs
    redoc_url="/redoc",         # ReDoc en /redoc
)

# Opcional pero muy recomendado: permitir CORS si el frontend es web o desde otro dominio
# (por ahora no es estrictamente necesario con Tkinter, pero no hace daño y es buena práctica)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En producción: ["http://localhost:3000", "https://tu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye los routers (endpoints)
app.include_router(gestorF29Router.router) 
app.include_router(vistaResumenF29Router.router)

# Opcional: raíz para verificar que el servidor está vivo
@app.get("/")
async def root():
    return {"message": "API Gestor F29 - SII está corriendo"}