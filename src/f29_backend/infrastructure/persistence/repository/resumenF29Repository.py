# Accesadores de la clase ResumenF29.

# Bibliotecas.
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date
# Módulos.
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import ResumenF29, EstadoF29
from f29_backend.infrastructure.persistence.models.cliente import Cliente
# Para corregir la busqueda de clientes por usuario a por empresa.
from f29_backend.infrastructure.persistence.models.usuario import Usuario


class ResumenF29Repository:
    # Constructor.
    def __init__(self, db: Session):
        self.db = db

    # Crear.
    def create(self, cliente_id: int, periodo: date,creado_por_usuario_id: int, **kwargs) -> ResumenF29:
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


    # Búsquedas unitarias.
    # Buscar por id.
    def find_by_id(self, resumen_id: int) -> Optional[ResumenF29]:
        return (self.db.query(ResumenF29).options(joinedload(ResumenF29.cliente)).filter(ResumenF29.id == resumen_id).first())
    
    # Buscar por cliente y periodo.
    def find_by_cliente_periodo(self, cliente_id: int, periodo: str) -> Optional[ResumenF29]:
        return (self.db.query(ResumenF29).filter(ResumenF29.cliente_id == cliente_id,ResumenF29.periodo == periodo).first())



    # Búsquedas de listas.
    # Buscar por cliente.
    def find_by_cliente(self, cliente_id: int) -> List[ResumenF29]:
        return (self.db.query(ResumenF29).filter(ResumenF29.cliente_id == cliente_id).order_by(ResumenF29.periodo.desc()).all())

    # Buscar por usuario y periodo.  (usado por el dashboard, tenemos que editar.)
    def find_by_usuario_y_mes(self, usuario_id: int, anio: int, mes: int) -> List[ResumenF29]:
        # Partimos buscando el usuario y lo guardamos.
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        empresa_id = usuario.empresa_id # Guardamos el id de la empresa en una variable
        periodo_str = f"{anio}-{str(mes).zfill(2)}"   # ejemplo: "2026-02"
        return (  # Buscamos los clientes por el id de la empresa, el periodo y que estén activos.
            self.db.query(ResumenF29)  # Nos conectamos a la tabla.
            .join(Cliente, ResumenF29.cliente_id == Cliente.id).options(joinedload(ResumenF29.cliente))  # Join
            .filter(Cliente.empresa_id == empresa_id ,ResumenF29.periodo == periodo_str,Cliente.activo == True)  # Condicion.
            .order_by(ResumenF29.periodo.desc()).all())   # Ordenamos por periodo.

    # Busca clientes sin resumenes hechos este mes.  (usado por el dashboard, tenemos que editar.)
    def find_clientes_sin_resumen_en_mes(self, usuario_id: int, anio: int, mes: int) -> List[Cliente]:
        # Partimos buscando el usuario y lo guardamos.
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        empresa_id = usuario.empresa_id # Guardamos el id de la empresa en una variable
        periodo_str = f"{anio}-{str(mes).zfill(2)}"   # → "2026-02"
        # Subquery: IDs de clientes que YA tienen resumen en ese mes
        clientes_con_resumen = (
            self.db.query(ResumenF29.cliente_id)  # Nos conectamos.
            .join(Cliente, ResumenF29.cliente_id == Cliente.id)  # Join.
            .filter(  # Buscamos por id de la empresa, periodo y estado activo.
                Cliente.empresa_id == empresa_id,ResumenF29.periodo == periodo_str,Cliente.activo == True).subquery())
        # Clientes de la empresa que NO están en esa subquery
        return (
            self.db.query(Cliente)  # Nos conectamos.
            .filter(Cliente.empresa_id == empresa_id,Cliente.activo == True,Cliente.id.notin_(clientes_con_resumen))  # WHERE
            .order_by(Cliente.razon_social).all()) # ordenamos.



    # Actualizaciones.
    # Actualizar.
    def update(self, resumen_id: int, **kwargs) -> Optional[ResumenF29]:
        resumen = self.find_by_id(resumen_id)  # Buscamos por id.
        if not resumen:  # Si no encontramos retornamos None.
            return None
        for key, value in kwargs.items():  # Si encontramos iteramos los argumentos que son una lista de tuples.
            if hasattr(resumen, key):  # Si el resumen encontrado tiene las llave del tuple iterado.
                setattr(resumen, key, value)  # Actualizamos el valor de ese diccionario con el tuple iterado.
        self.db.commit()  # Persistimos.
        self.db.refresh(resumen)  # Refrescamos.
        return resumen

    # Cambiar estado.
    def cambiar_estado(self, resumen_id: int, nuevo_estado: EstadoF29) -> Optional[ResumenF29]:
        resumen = self.find_by_id(resumen_id)  # Buscamos por id.
        if not resumen:  # Si no encontramos retornamos None.
            return None
        resumen.estado = nuevo_estado  # Cambiamos el estado
        self.db.commit()  # Persistimos.
        self.db.refresh(resumen)  # Refrescamos.
        return resumen



    # Borrar.
    def delete(self, resumen_id: int) -> bool:
        resumen = self.find_by_id(resumen_id)  # Buscamos por id.
        if not resumen:  # Si no encontramos retornamos falso.
            return False
        self.db.delete(resumen)  # Si encontramos borramos.
        self.db.commit()  # Persistimos.
        return True  # Retornamos true.



    # Funciones auxiliares.
    # Cuenta los resumenes hechos durante este mes a los clientes de la empresa.   (usado por el dashboard, editar)
    def count_by_usuario_y_mes(self, usuario_id: int, anio: int, mes: int) -> int:
        # Partimos buscando el usuario y lo guardamos.
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        empresa_id = usuario.empresa_id # Guardamos el id de la empresa en una variable
        periodo_str = f"{anio}-{str(mes).zfill(2)}"   # → "2026-02"
        return (
            self.db.query(ResumenF29)  # Nos conectamos.
            .join(Cliente, ResumenF29.cliente_id == Cliente.id)  # JOIN
            .filter(  # Buscamos por empresa, por periodo y estado activo.
                Cliente.empresa_id == empresa_id,ResumenF29.periodo == periodo_str,Cliente.activo == True)
            .count())  # Contar.



