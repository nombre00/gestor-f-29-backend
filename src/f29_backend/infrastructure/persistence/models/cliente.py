# Clientes de la empresas, asociados a un usuario, son las cuentas cuyos datos procesa el software.

# Bibliotecas.
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
# Módulos.
from f29_backend.core.database import Base


class Cliente(Base):
    __tablename__ = 'cliente'  # Nombre de la tabla.
    
    # Columnas.
    # Column() indica que es una columna de la tabla, los parámetros son restricciones.
    id = Column(Integer, primary_key=True, autoincrement=True)  # LLave primaria.
    empresa_id = Column(
        Integer,
        ForeignKey('empresa.id', ondelete='CASCADE'),  # Primer argumento: tabla de la llave, segundo argumento: que hace cuando lo borran.
        nullable=False,
        index=True  # genera un índice. 
    )
    asignado_a_usuario_id = Column(
        Integer,
        ForeignKey('usuario.id', ondelete='RESTRICT'),
        nullable=False,
        index=True  # genera un índice.
    )
    # Dato nuevo.
    nro_cliente = Column(String(50), nullable=True)
    
    # Datos del cliente (PYME).
    rut = Column(String(12), nullable=False, index=True)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    giro = Column(String(255), nullable=True)
    actividad_economica = Column(String(255), nullable=True)
    
    # Dirección.
    direccion = Column(String(500), nullable=True)
    comuna = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    
    # Contacto.
    contacto_nombre = Column(String(255), nullable=True)
    contacto_email = Column(String(255), nullable=True)
    contacto_telefono = Column(String(20), nullable=True)
    
    # Estado.
    activo = Column(Boolean, default=True, nullable=False)  # Para validaciones en acciones futuras.
    
    # Timestamps para registro de creación y modificaciones.
    # func. = permite usar funciones SQL dentro de python.
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones
    # relationship: genera algo similar a un puntero que simplifica queries, en el caso de abajo generamos un puntero con la empresa de la que cliente es cliente.
    empresa = relationship("Empresa", back_populates="clientes", foreign_keys=[empresa_id])
    asignado_a_usuario = relationship(  # Un cliente tiene un usuario, un usuario tiene muchos clientes.
        "Usuario",
        back_populates="clientes_asignados",
        foreign_keys=[asignado_a_usuario_id]
    )
    
    # Constraint: RUT único por empresa. 
    __table_args__ = (
        # UniqueConstraint: obliga que los valores de las columnas ingresadas como parámetros no puedan repetirse, en este caso una empresa no puede tener 2 clientes con el mismo rut.
        UniqueConstraint('empresa_id', 'rut', name='unique_rut_empresa'),
        # Index: crea un índice para búsquedas rápidas.
        Index('idx_empresa_activo', 'empresa_id', 'activo'),
    )
    
    def __repr__(self):  # Un print.
        return f"<Cliente(id={self.id}, rut={self.rut}, razon_social={self.razon_social})>"