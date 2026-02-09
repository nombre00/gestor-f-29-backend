# Modelo de mapeo para tablas SQL.

from sqlalchemy import Column, Integer, String, JSON
from f29_backend.core.database import Base


class ResumenF29DB(Base):
    __tablename__ = "resumenes_f29"

    id = Column(Integer, primary_key=True, autoincrement=True)
    periodo = Column(String(7), nullable=False, unique=True, index=True)  # clave natural: 2026-02
    ivapp = Column(Integer, default=0)
    remanente = Column(Integer, default=0)
    remanenteMesAnterior = Column(Integer, default=0)
    tt = Column(Integer, default=0)

    # Campos complejos → JSON (SQLAlchemy los serializa automáticamente)
    encabezado = Column(JSON, nullable=False, default=dict)
    ventas_detalle = Column(JSON, nullable=False, default=list)
    ventas_total = Column(JSON, nullable=False, default=dict)
    compras_detalle = Column(JSON, nullable=False, default=list)
    compras_total = Column(JSON, nullable=False, default=dict)
    remuneraciones = Column(JSON, nullable=False, default=dict)
    honorarios = Column(JSON, nullable=False, default=dict)
    ppm = Column(JSON, nullable=False, default=dict)