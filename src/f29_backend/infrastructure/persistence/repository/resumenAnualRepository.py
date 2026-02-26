# infrastructure/persistence/repository/resumenAnualRepository.py

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from f29_backend.infrastructure.persistence.models.resumenAnual import ResumenAnual, EstadoResumenAnual
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import ResumenF29


class ResumenAnualRepository:
    def __init__(self, db: Session):
        self.db = db

    # ────────────────────────────────────────────────
    # Get by cliente + año (ya perfecto, solo agrego .options() si necesitas eager loading)
    # ────────────────────────────────────────────────
    def get_by_cliente_and_año(self, cliente_id: int, año: str) -> Optional[ResumenAnual]:
        stmt = select(ResumenAnual).where(
            and_(
                ResumenAnual.cliente_id == cliente_id,
                ResumenAnual.año == año,
            )
        )
        # Opcional: eager load relaciones si las usas frecuentemente
        # .options(joinedload(ResumenAnual.cliente), joinedload(ResumenAnual.creado_por))
        return self.db.scalars(stmt).first()

    # ────────────────────────────────────────────────
    # Create (perfecto, solo agrego validación básica de año)
    # ────────────────────────────────────────────────
    def create(
        self,
        cliente_id: int,
        año: str,
        creado_por_usuario_id: int,
        detalles_json: dict,
        periodos_incluidos_json: List[str],
        estado: EstadoResumenAnual = EstadoResumenAnual.BORRADOR,
    ) -> ResumenAnual:
        if len(año) != 4 or not año.isdigit():
            raise ValueError("El año debe ser un string de 4 dígitos numéricos")

        nuevo = ResumenAnual(
            cliente_id=cliente_id,
            año=año,
            estado=estado,
            creado_por_usuario_id=creado_por_usuario_id,
            detalles_json=detalles_json or {},           # evita None
            periodos_incluidos_json=periodos_incluidos_json or [],
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    # ────────────────────────────────────────────────
    # Update (muy bueno, solo agrego flush opcional y chequeo de existencia)
    # ────────────────────────────────────────────────
    def update(
        self,
        resumen: ResumenAnual,
        detalles_json: Optional[dict] = None,
        periodos_incluidos_json: Optional[List[str]] = None,
        estado: Optional[EstadoResumenAnual] = None,
    ) -> ResumenAnual:
        if resumen is None:
            raise ValueError("El resumen no existe")

        if detalles_json is not None:
            resumen.detalles_json = detalles_json
        if periodos_incluidos_json is not None:
            resumen.periodos_incluidos_json = periodos_incluidos_json
        if estado is not None:
            resumen.estado = estado

        self.db.commit()
        self.db.refresh(resumen)
        return resumen

    # Delete (perfecto)
    def delete(self, resumen: ResumenAnual) -> None:
        if resumen:
            self.db.delete(resumen)
            self.db.commit()

    # ────────────────────────────────────────────────
    # Helpers útiles (muy bien pensados)
    # ────────────────────────────────────────────────

    def get_all_f29_del_año(self, cliente_id: int, año: str) -> List[ResumenF29]:
        stmt = (
            select(ResumenF29)
            .where(
                and_(
                    ResumenF29.cliente_id == cliente_id,
                    ResumenF29.periodo.like(f"{año}-%"),
                )
            )
            .order_by(ResumenF29.periodo.asc())   # asc explícito para claridad
        )
        return self.db.scalars(stmt).all()

    def get_periodos_de_f29s(self, f29s: List[ResumenF29]) -> List[str]:
        return [f.periodo for f in f29s if f.periodo]  # filtro por si algún periodo es None (improbable)

    def contar_f29s_del_año(self, cliente_id: int, año: str) -> int:
        stmt = select(func.count(ResumenF29.id)).where(
            and_(
                ResumenF29.cliente_id == cliente_id,
                ResumenF29.periodo.like(f"{año}-%"),
            )
        )
        return self.db.scalar(stmt) or 0   # más eficiente que len() + all()

    # ────────────────────────────────────────────────
    # Métodos adicionales recomendados para el router y dashboard
    # ────────────────────────────────────────────────

    def get_by_id(self, anual_id: int) -> Optional[ResumenAnual]:
        stmt = select(ResumenAnual).where(ResumenAnual.id == anual_id)
        return self.db.scalars(stmt).first()

    def get_all_by_cliente(self, cliente_id: int) -> List[ResumenAnual]:
        stmt = (
            select(ResumenAnual)
            .where(ResumenAnual.cliente_id == cliente_id)
            .order_by(ResumenAnual.año.desc())
        )
        return self.db.scalars(stmt).all()

    def existe_para_cliente_y_año(self, cliente_id: int, año: str) -> bool:
        stmt = select(func.count(ResumenAnual.id)).where(
            and_(
                ResumenAnual.cliente_id == cliente_id,
                ResumenAnual.año == año,
            )
        )
        return (self.db.scalar(stmt) or 0) > 0