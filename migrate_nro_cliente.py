from sqlalchemy import text
from f29_backend.core.database import engine

def agregar_columna_nro_cliente():
    with engine.connect() as conn:
        # Verifica si la columna ya existe antes de agregarla
        resultado = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = DATABASE()
              AND table_name = 'cliente' 
              AND column_name = 'nro_cliente'
        """))
        
        existe = resultado.scalar() > 0
        
        if existe:
            print("La columna 'nro_cliente' ya existe, no se hizo nada.")
        else:
            conn.execute(text("""
                ALTER TABLE cliente 
                ADD COLUMN nro_cliente VARCHAR(50) NULL
            """))
            conn.commit()
            print("Columna 'nro_cliente' agregada exitosamente.")

if __name__ == "__main__":
    agregar_columna_nro_cliente()