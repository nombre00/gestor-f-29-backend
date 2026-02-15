# Trabajador de la empresa, usuario del software.

# Bibliotecas.
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
# Módulos.
from f29_backend.core.database import Base


# Enum para roles
class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    CONTADOR = "contador"
    ASISTENTE = "asistente"

class Usuario(Base):
    __tablename__ = 'usuario'
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(
        Integer, 
        ForeignKey('empresa.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=True)
    rol = Column(
        Enum(RolUsuario),
        default=RolUsuario.CONTADOR,
        nullable=False
    )
    activo = Column(Boolean, default=True, nullable=False)
    ultimo_acceso = Column(TIMESTAMP, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones.
    # Relación Many-to-One con Empresa
    empresa = relationship("Empresa", back_populates="usuarios")
    # Relación One-to-Many con Cliente (clientes asignados)
    clientes_asignados = relationship(
        "Cliente",
        back_populates="asignado_a_usuario",
        foreign_keys="Cliente.asignado_a_usuario_id"
    )
    
    # Métodos.
    # Print simple.
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, rol={self.rol})>"
    
    