# Punto de entrada del código.

# Recordatorios.
# Api: endpoints, incluye las carpetas schemas y la carpeta routers (controllers).
    # Schemas: clases de input y output de la api, valida datos, protege datos internos, genera documentación (por lo que entiendo).
    # routers: rutas REST, lo que conecta con el front.
# application: lógica de negocio, incluye la carpeta services (orquestación, se llama funciones de otras partes).
# core: necesidades comunes, incluye los archivos database, security y settings.
    # database: es la conección con la base de datos en mySQL. 
    # security: incluye la gestion del token de validación del usuario.
    # settings: constantes que ocupan otros módulos, importa datos del archivo .env.
# Domain/entities: modelos del negocio, clases tipicas de java.
# Infrastructure: incluye adaptadores (parsers y writers) y presistencia: models (modelos de las tablas) y repository (accesadores)


# Flujo típico de trabajo: Flujo típico: Frontend envía schema → Controller valida → Service usa domain para lógica → Repository mapea a model y guarda → Retorna schema.



# Instalaciones que faltan en el requirements:
    # pip install bcrypt==4.2.1 
    # pip install pydantic[email]
    # pip install resend
    # pip install bs4 
    # pip install lxml



# gestorf29-backend/src/f29_backend    - para cuando necesites copiar y pegar
# Comandos útiles.
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
from f29_backend.api.routers import authRouter
from f29_backend.api.routers import clienteRouter
from f29_backend.api.routers import empresaRouter
from f29_backend.api.routers import invitacionesRouter
from f29_backend.api.routers import resumenAnualRouter
from f29_backend.api.routers import resumenF29Router
from f29_backend.api.routers import usuariosRouter
from f29_backend.api.routers import vistaGestorF29Router  
from f29_backend.api.routers import vistaResumenF29Router
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
# Medida de seguridad, restringe acceso a fuentes que no sean del mismo dominio que la aplicación.
# Lista de orígenes permitidos si el despliegue es on premise y localhost (lista en desarrollo).
origins = [
    "http://localhost:3000",       # React create-react-app típico
    "http://localhost:5173",       # Vite (el más común hoy en día)
    "http://127.0.0.1:3000",       # a veces el navegador usa 127.0.0.1 en vez de localhost
    "http://127.0.0.1:5173",
    "http://localhost:5174",       # por si usas otro puerto en algún momento
]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,  # En producción
    allow_origins=["*"],      # En desarrollo.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers 
app.include_router(authRouter.router)
app.include_router(clienteRouter.router)
app.include_router(empresaRouter.router)
app.include_router(invitacionesRouter.router)
app.include_router(resumenAnualRouter.router)
app.include_router(resumenF29Router.router)
app.include_router(usuariosRouter.router)
app.include_router(vistaGestorF29Router.router) 
app.include_router(vistaResumenF29Router.router)




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

