# Conección.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a MySQL
# Cambia 'tu_usuario', 'tu_contraseña', 'localhost' y 'f29_gestor' según tu setup
# Ejemplo con XAMPP/MAMP/local: root sin password → mysql+mysqlconnector://root:@localhost/f29_gestor
DATABASE_URL = "mysql+mysqlconnector://tu_usuario:tu_contraseña@localhost:3306/f29_gestor"

# Crea el motor de conexión
engine = create_engine(DATABASE_URL)

# Crea una fábrica de sesiones (para transacciones con la DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta es la clase Base que todos tus modelos heredan
Base = declarative_base()


# Dependencia para inyectar la sesión DB en los endpoints (muy útil en FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()