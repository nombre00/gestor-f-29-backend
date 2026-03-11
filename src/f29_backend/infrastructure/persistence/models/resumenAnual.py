# clase que guarda la suma de los f29s hechos durante un año para un cliente.

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Enum, func, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
import enum

from f29_backend.core.database import Base


# Estados, funcionan como flags.
class EstadoResumenAnual(str, enum.Enum):
    BORRADOR = "borrador"
    REVISADO = "revisado"


class ResumenAnual(Base):
    __tablename__ = "resumen_anual"   # nombre de la tabla.

    # id del resumen, autogenerada.
    id = Column(Integer, primary_key=True, autoincrement=True)

    # id del cliente.
    cliente_id = Column(Integer,ForeignKey("cliente.id", ondelete="CASCADE"),nullable=False,index=True,)

    # Año del resumenAnual.
    año = Column(String(4), nullable=False, index=True)

    # Estado.
    estado = Column(Enum(EstadoResumenAnual),default=EstadoResumenAnual.BORRADOR,nullable=False,)

    # Usuario que lo creó.
    creado_por_usuario_id = Column(Integer,ForeignKey("usuario.id", ondelete="RESTRICT"),nullable=False,)

    # Cuando fue creado.
    created_at = Column(TIMESTAMP,server_default=func.current_timestamp(),nullable=False,)

    # Cuando fue modificado.
    updated_at = Column(TIMESTAMP,server_default=func.current_timestamp(),onupdate=func.current_timestamp(),nullable=False,)

    # Lista de periodos usados para generar este resumenAnual.
    periodos_incluidos_json = Column(JSON, nullable=True, default=list)

    # Contenido completo del resumen acumulado.
    detalles_json = Column(JSON, nullable=True)

    # Restricción de unicidad.
    __table_args__ = (
        UniqueConstraint("cliente_id", "año", name="unique_cliente_año"),
    )

    # Relaciones para facilitar consultas
    cliente = relationship("Cliente", backref="resumenes_anuales")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_usuario_id])