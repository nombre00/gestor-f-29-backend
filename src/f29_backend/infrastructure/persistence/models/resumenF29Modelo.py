# Modelo de mapeo para tablas SQL.


from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey, TIMESTAMP, Enum, func, UniqueConstraint
from sqlalchemy.orm import relationship
import enum
# Módulos.
from f29_backend.core.database import Base


class EstadoF29(str, enum.Enum):
    BORRADOR = "borrador"
    REVISADO = "revisado"
    ENVIADO = "enviado"
    PAGADO = "pagado"

class ResumenF29(Base):
    __tablename__ = 'resumen_f29'
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(
        Integer,
        ForeignKey('cliente.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    periodo = Column(Date, nullable=False)  # Primer día del mes: 2025-01-01
    
    # Datos del F29 (campos básicos por ahora)
    debito_fiscal = Column(DECIMAL(15, 2), default=0)
    credito_fiscal = Column(DECIMAL(15, 2), default=0)
    remanente_mes_anterior = Column(DECIMAL(15, 2), default=0)
    iva_a_pagar = Column(DECIMAL(15, 2), default=0)
    
    total_ventas_netas = Column(DECIMAL(15, 2), default=0)
    total_compras_netas = Column(DECIMAL(15, 2), default=0)
    total_iva_ventas = Column(DECIMAL(15, 2), default=0)
    total_iva_compras = Column(DECIMAL(15, 2), default=0)
    
    # Metadatos
    estado = Column(Enum(EstadoF29), default=EstadoF29.BORRADOR, nullable=False)
    fecha_envio_sii = Column(Date, nullable=True)
    numero_folio = Column(String(50), nullable=True)
    
    # Archivos
    archivo_compras = Column(String(255), nullable=True)
    archivo_ventas = Column(String(255), nullable=True)
    archivo_remuneraciones = Column(String(255), nullable=True)
    archivo_honorarios = Column(String(255), nullable=True)
    
    # Auditoría
    creado_por_usuario_id = Column(
        Integer,
        ForeignKey('usuario.id', ondelete='RESTRICT'),
        nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    
    # Relaciones
    cliente = relationship("Cliente", backref="resumenes_f29")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_usuario_id])
    
    # Constraint: Un F29 por cliente por periodo
    __table_args__ = (
        UniqueConstraint('cliente_id', 'periodo', name='unique_cliente_periodo'),
    )
    
    def __repr__(self):
        return f"<ResumenF29(id={self.id}, cliente_id={self.cliente_id}, periodo={self.periodo})>"