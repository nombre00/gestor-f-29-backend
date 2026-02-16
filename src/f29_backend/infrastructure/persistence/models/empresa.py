# Clientes consumidores del software.

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship
# Módulos.
from f29_backend.core.database import Base


class Empresa(Base):
    __tablename__ = 'empresa'
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String(12), unique=True, nullable=False, index=True)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    activa = Column(Boolean, default=True, nullable=False)
    
    # Timestamps automáticos
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones (One-to-Many)
    usuarios = relationship(
        "Usuario", 
        back_populates="empresa",
        cascade="all, delete-orphan"  # Si eliminamos empresa, eliminamos usuarios.
    )
    clientes = relationship(
        "Cliente",
        back_populates="empresa",
        cascade="all, delete-orphan"  # Si eliminamos empresa eliminamos clientes.
    )
    invitaciones = relationship("Invitacion", 
        back_populates="empresa", 
        cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Empresa(id={self.id}, rut={self.rut}, razon_social={self.razon_social})>"