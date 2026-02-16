# Invitación del admin al usuario nuevo.

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
import secrets
from datetime import datetime, timedelta

# Módulos
from f29_backend.core.database import Base


class Invitacion(Base):
    __tablename__ = 'invitacion'
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    empresa_id = Column(
        Integer,
        ForeignKey('empresa.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    email = Column(String(255), nullable=False, index=True)
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    nombre = Column(String(255), nullable=True)
    apellido = Column(String(255), nullable=True)
    
    rol = Column(String(50), default='contador', nullable=False)
    
    # Usuario que envió la invitación
    invitado_por_usuario_id = Column(
        Integer,
        ForeignKey('usuario.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Estado de la invitación
    usado = Column(Boolean, default=False, nullable=False)
    
    # Fecha de expiración (7 días por defecto)
    expires_at = Column(TIMESTAMP, nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="invitaciones")
    invitado_por = relationship("Usuario", foreign_keys=[invitado_por_usuario_id])
    
    # Métodos
    @staticmethod
    def generar_token():
        """Genera un token único y seguro para la invitación"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def calcular_expiracion(dias=7):
        """Calcula la fecha de expiración (por defecto 7 días)"""
        return datetime.utcnow() + timedelta(days=dias)
    
    def esta_expirada(self):
        """Verifica si la invitación ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<Invitacion(id={self.id}, email={self.email}, usado={self.usado})>"