# Accesadores de la clase ResumenF29.

# Bibliotecas.
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date
# Módulos.
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import ResumenF29, EstadoF29
from f29_backend.infrastructure.persistence.models.cliente import Cliente


class ResumenF29Repository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, cliente_id: int, periodo: date,
               creado_por_usuario_id: int, **kwargs) -> ResumenF29:
        """Crea un nuevo resumen F29"""
        resumen = ResumenF29(
            cliente_id=cliente_id,
            periodo=periodo,
            creado_por_usuario_id=creado_por_usuario_id,
            estado=EstadoF29.BORRADOR,
            **kwargs
        )
        self.db.add(resumen)
        self.db.commit()
        self.db.refresh(resumen)
        return resumen

    def find_by_id(self, resumen_id: int) -> Optional[ResumenF29]:
        """Busca resumen por ID, cargando el cliente asociado"""
        return (
            self.db.query(ResumenF29)
            .options(joinedload(ResumenF29.cliente))
            .filter(ResumenF29.id == resumen_id)
            .first()
        )

    def find_by_cliente_periodo(self, cliente_id: int, periodo: date) -> Optional[ResumenF29]:
        """Busca el resumen F29 de un cliente para un período específico"""
        return (
            self.db.query(ResumenF29)
            .filter(
                ResumenF29.cliente_id == cliente_id,
                ResumenF29.periodo == periodo
            )
            .first()
        )

    def find_by_cliente(self, cliente_id: int) -> List[ResumenF29]:
        """Lista todos los resúmenes de un cliente, ordenados por período desc"""
        return (
            self.db.query(ResumenF29)
            .filter(ResumenF29.cliente_id == cliente_id)
            .order_by(ResumenF29.periodo.desc())
            .all()
        )

    def find_by_usuario_y_mes(self, usuario_id: int, anio: int, mes: int) -> List[ResumenF29]:
        """
        Lista resúmenes F29 hechos durante un mes por un usuario.
        Usado en el dashboard: 'resúmenes del mes'.
        """
        return (
            self.db.query(ResumenF29)
            .join(Cliente, ResumenF29.cliente_id == Cliente.id)
            .options(joinedload(ResumenF29.cliente))
            .filter(
                Cliente.asignado_a_usuario_id == usuario_id,
                extract('year', ResumenF29.periodo) == anio,
                extract('month', ResumenF29.periodo) == mes,
                Cliente.activo == True
            )
            .order_by(ResumenF29.periodo.desc())
            .all()
        )

    def find_clientes_sin_resumen_en_mes(
        self, usuario_id: int, anio: int, mes: int
    ) -> List[Cliente]:
        """
        Lista clientes del usuario que NO tienen resumen F29 en el mes indicado.
        Usado en el dashboard: 'resúmenes por hacer'.
        """
        # Subquery: IDs de clientes que YA tienen resumen en ese mes
        clientes_con_resumen = (
            self.db.query(ResumenF29.cliente_id)
            .join(Cliente, ResumenF29.cliente_id == Cliente.id)
            .filter(
                Cliente.asignado_a_usuario_id == usuario_id,
                extract('year', ResumenF29.periodo) == anio,
                extract('month', ResumenF29.periodo) == mes,
                Cliente.activo == True
            )
            .subquery()
        )

        # Clientes del usuario que NO están en esa subquery
        return (
            self.db.query(Cliente)
            .filter(
                Cliente.asignado_a_usuario_id == usuario_id,
                Cliente.activo == True,
                Cliente.id.notin_(clientes_con_resumen)
            )
            .order_by(Cliente.razon_social)
            .all()
        )

    def update(self, resumen_id: int, **kwargs) -> Optional[ResumenF29]:
        """Actualiza campos de un resumen"""
        resumen = self.find_by_id(resumen_id)
        if not resumen:
            return None
        for key, value in kwargs.items():
            if hasattr(resumen, key):
                setattr(resumen, key, value)
        self.db.commit()
        self.db.refresh(resumen)
        return resumen

    def cambiar_estado(self, resumen_id: int, nuevo_estado: EstadoF29) -> Optional[ResumenF29]:
        """Cambia el estado de un resumen F29"""
        resumen = self.find_by_id(resumen_id)
        if not resumen:
            return None
        resumen.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(resumen)
        return resumen

    def delete(self, resumen_id: int) -> bool:
        """Elimina un resumen (solo borradores)"""
        resumen = self.find_by_id(resumen_id)
        if not resumen:
            return False
        self.db.delete(resumen)
        self.db.commit()
        return True

    def count_by_usuario_y_mes(self, usuario_id: int, anio: int, mes: int) -> int:
        """Cuenta resúmenes completados en el mes por el usuario"""
        return (
            self.db.query(ResumenF29)
            .join(Cliente, ResumenF29.cliente_id == Cliente.id)
            .filter(
                Cliente.asignado_a_usuario_id == usuario_id,
                extract('year', ResumenF29.periodo) == anio,
                extract('month', ResumenF29.periodo) == mes,
                Cliente.activo == True
            )
            .count()
        )