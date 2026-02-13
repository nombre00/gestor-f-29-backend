# Clientes de la empresas, asociados a un usuario, son las cuentas cuyos datos procesa el software.


from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
# Módulos.
from f29_backend.core.database import Base


class Cliente(Base):
    __tablename__ = 'cliente'
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(
        Integer,
        ForeignKey('empresa.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    asignado_a_usuario_id = Column(
        Integer,
        ForeignKey('usuario.id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    
    # Datos del cliente (PYME)
    rut = Column(String(12), nullable=False, index=True)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    giro = Column(String(255), nullable=True)
    actividad_economica = Column(String(255), nullable=True)
    
    # Dirección
    direccion = Column(String(500), nullable=True)
    comuna = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    
    # Contacto
    contacto_nombre = Column(String(255), nullable=True)
    contacto_email = Column(String(255), nullable=True)
    contacto_telefono = Column(String(20), nullable=True)
    
    # Estado
    activo = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="clientes")
    
    asignado_a_usuario = relationship(
        "Usuario",
        back_populates="clientes_asignados",
        foreign_keys=[asignado_a_usuario_id]
    )
    
    # Constraint: RUT único por empresa
    __table_args__ = (
        UniqueConstraint('empresa_id', 'rut', name='unique_rut_empresa'),
        Index('idx_empresa_activo', 'empresa_id', 'activo'),
    )
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, rut={self.rut}, razon_social={self.razon_social})>"