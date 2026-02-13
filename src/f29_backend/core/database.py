# Conección.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 

# URL de conexión a MySQL
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/gestorf29?charset=utf8mb4"

# Crear engine (UNA SOLA VEZ)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Verifica que la conexión esté viva
    pool_recycle=3600,         # Recicla conexiones cada hora
    echo=True                  # Muestra SQL en consola (cambiar a False en producción)
)

# Session factory (UNA SOLA VEZ)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()