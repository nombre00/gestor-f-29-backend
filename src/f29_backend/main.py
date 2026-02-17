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



# Instalaciones que faltan en el requirements:
    # pip install bcrypt==4.2.1 
    # pip install pydantic[email]



# gestorf29-backend/src/f29_backend

# Para moverme a la carptea raiz:     $env:PYTHONPATH="src" 

# Con este comando le decimos al backend en que puerto correr.
# Para correr por terminal:   uvicorn src.f29_backend.main:app --reload --port 8000

# Para crear el entorno virtual:            python -m venv .venv
# Para correr el entorno virtual:           .\.venv\Scripts\Activate.ps1


# Bibliotecas.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# Routers.
from f29_backend.api.routers import vistaGestorF29Router  
from f29_backend.api.routers import vistaResumenF29Router
from f29_backend.api.routers import usuariosRouter
from f29_backend.api.routers import invitacionesRouter
from f29_backend.api.routers import authRouter
# Persistencia.
from f29_backend.core.database import engine, get_db, Base
from f29_backend.infrastructure.persistence.models import Empresa, Usuario, Cliente, resumenF29Modelo

# Crear app
app = FastAPI(
    title="API Gestor F29 - SII",
    description="Backend para procesar y generar resúmenes Formulario 29",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers 
app.include_router(vistaGestorF29Router.router) 
app.include_router(vistaResumenF29Router.router)
app.include_router(usuariosRouter.router)
app.include_router(invitacionesRouter.router)
app.include_router(authRouter.router)

# Root
@app.get("/")
async def root():
    return {"message": "API Gestor F29 - SII está corriendo"}

# Crear tablas al iniciar
@app.on_event("startup")
def startup_event():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente")

# Health check (opcional pero útil)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

