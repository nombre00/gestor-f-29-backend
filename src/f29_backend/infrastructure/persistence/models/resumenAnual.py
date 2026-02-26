# clase que guarda la suma de los f29s hechos durante un año para un cliente.

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum, func, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
import enum

from f29_backend.core.database import Base


class EstadoResumenAnual(str, enum.Enum):
    BORRADOR = "borrador"
    REVISADO = "revisado"
    # Puedes agregar FINALIZADO u otros si lo necesitas más adelante


class ResumenAnual(Base):
    __tablename__ = "resumen_anual"

    id = Column(Integer, primary_key=True, autoincrement=True)

    cliente_id = Column(Integer,ForeignKey("cliente.id", ondelete="CASCADE"),nullable=False,index=True,)

    año = Column(String(4), nullable=False, index=True)

    estado = Column(Enum(EstadoResumenAnual),default=EstadoResumenAnual.BORRADOR,nullable=False,)

    creado_por_usuario_id = Column(Integer,ForeignKey("usuario.id", ondelete="RESTRICT"),nullable=False,)

    created_at = Column(TIMESTAMP,server_default=func.current_timestamp(),nullable=False,)

    updated_at = Column(TIMESTAMP,server_default=func.current_timestamp(),onupdate=func.current_timestamp(),nullable=False,)

    # ────────────────────────────────────────────────
    # Lista de periodos usados para generar este anual
    # Ej: ["2025-01", "2025-02", ..., "2025-06"]
    # Opcionalmente: [{"periodo": "2025-01", "f29_id": 145}, ...]
    # ────────────────────────────────────────────────
    periodos_incluidos_json = Column(JSON, nullable=True, default=list)

    # ────────────────────────────────────────────────
    # Contenido completo del resumen acumulado
    # → MISMA ESTRUCTURA que ResumenF29 para reutilizar todo lo posible
    # (encabezado, ventas_total, compras_total, IVAPP, remanente, ppm, TT, etc.)
    # ────────────────────────────────────────────────
    detalles_json = Column(JSON, nullable=True)

    # Restricción de unicidad
    __table_args__ = (
        UniqueConstraint("cliente_id", "año", name="unique_cliente_año"),
    )

    # Relaciones para facilitar consultas
    cliente = relationship("Cliente", backref="resumenes_anuales")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_usuario_id])