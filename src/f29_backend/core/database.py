# Conección.

# Bibliotecas.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
# Módulos.
from f29_backend.core.settings import settings

# Asignamos la url a una variable.
DATABASE_URL = settings.DATABASE_URL.get_secret_value()

# Crear engine: el comtor que se comunica con la base de datos.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Verifica que la conexión esté viva
    pool_recycle=3600,         # Recicla conexiones cada hora
    echo=True                  # Muestra SQL en consola (cambiar a False en producción)
)

# Session factory (UNA SOLA VEZ)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()  # Le dice a mySQL que genere una tabla.

# Dependency para FastAPI
def get_db():
    db = SessionLocal()  # La conección.
    try:
        yield db  # yield: enterga a medida que lleguen datos.
    finally:
        db.close()