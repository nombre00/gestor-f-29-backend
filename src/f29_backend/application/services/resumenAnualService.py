from typing import List, Dict, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from f29_backend.infrastructure.persistence.repository.resumenAnualRepository import ResumenAnualRepository
from f29_backend.infrastructure.persistence.repository.resumenF29Repository import ResumenF29Repository
from f29_backend.domain.entities.resumenF29 import ResumenF29  # entidad dominio
from f29_backend.api.schemas.resumenAnualSchema import (
    ResumenAnualResponse,
    ResumenAnualContenido,
    EstadoResumenAnual,
)
from f29_backend.infrastructure.persistence.models.usuario import Usuario
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository


class ResumenAnualService:
    def __init__(self, db: Session):
        self.db = db
        self.repo_anual = ResumenAnualRepository(db)
        self.repo_f29 = ResumenF29Repository(db)

    def get_or_create_anual(self, cliente_id: int, año: str, usuario_id: int) -> ResumenAnualResponse:
        anual = self.repo_anual.get_by_cliente_and_año(cliente_id, año)
        if not anual:
            anual = self.repo_anual.create(
                cliente_id=cliente_id,
                año=año,
                creado_por_usuario_id=usuario_id,
                detalles_json={},
                periodos_incluidos_json=[],
            )
        return self._to_response(anual)

    def recalcular_anual(self, cliente_id: int, año: str, usuario_id: int) -> ResumenAnualResponse:
        # 1. Traer modelos SQLAlchemy del año ordenados por periodo
        f29s_modelos = self.repo_anual.get_all_f29_del_año(cliente_id, año)
        if not f29s_modelos:
            raise HTTPException(404, "No hay F29 generados para este cliente y año")

        # 2. Deserializar cada modelo a entidad dominio usando detalles_json
        f29s_entidades = []
        for modelo in f29s_modelos:
            if modelo.detalles_json:
                f29s_entidades.append(ResumenF29.from_dict(modelo.detalles_json))

        if not f29s_entidades:
            raise HTTPException(404, "Los F29 encontrados no tienen datos procesados")

        # 3. Generar periodos_incluidos (desde los modelos, que tienen el campo periodo)
        periodos = self.repo_anual.get_periodos_de_f29s(f29s_modelos)

        # 4. Acumular
        acumulado = self._acumular_f29s(f29s_entidades)

        # 5. Actualizar o crear
        anual = self.repo_anual.get_by_cliente_and_año(cliente_id, año)
        if anual:
            anual = self.repo_anual.update(
                resumen=anual,
                detalles_json=acumulado.to_dict(),
                periodos_incluidos_json=periodos,
            )
        else:
            anual = self.repo_anual.create(
                cliente_id=cliente_id,
                año=año,
                creado_por_usuario_id=usuario_id,
                detalles_json=acumulado.to_dict(),
                periodos_incluidos_json=periodos,
            )

        return self._to_response(anual)

    def _acumular_f29s(self, f29s: List[ResumenF29]) -> ResumenF29:
        if not f29s:
            return ResumenF29()

        acum = ResumenF29()

        # 1. Acumular detalle ventas y compras por código
        ventas_acum = {}
        compras_acum = {}

        for f29 in f29s:
            for fila in f29.ventas_detalle:
                tipo = fila['tipo']
                if tipo not in ventas_acum:
                    ventas_acum[tipo] = fila.copy()
                else:
                    for k in ['td', 'exento', 'neto', 'iva', 'total']:
                        ventas_acum[tipo][k] += fila.get(k, 0)

            for fila in f29.compras_detalle:
                tipo = fila['tipo']
                if tipo not in compras_acum:
                    compras_acum[tipo] = fila.copy()
                else:
                    for k in ['td', 'exento', 'neto', 'iva_rec', 'iva_no_rec', 'total']:
                        compras_acum[tipo][k] += fila.get(k, 0)

        codigos_ventas_orden = [110, 34, 46, 33, 39, 48, 56, 61, 45, 43]
        for cod in codigos_ventas_orden:
            if cod in ventas_acum:
                acum.ventas_detalle.append(ventas_acum[cod])
            else:
                acum.ventas_detalle.append(
                    {'tipo': cod, 'td': 0, 'exento': 0, 'neto': 0, 'iva': 0, 'total': 0}
                )

        codigos_compras_orden = [34, 33, 761, 524, 61, 56, 914, 536]
        for cod in codigos_compras_orden:
            if cod in compras_acum:
                acum.compras_detalle.append(compras_acum[cod])
            else:
                acum.compras_detalle.append(
                    {'tipo': cod, 'td': 0, 'exento': 0, 'neto': 0, 'iva_rec': 0, 'iva_no_rec': 0, 'total': 0}
                )

        # 2. Acumular totales y campos simples
        for f29 in f29s:
            for k in ['td', 'exento', 'neto', 'iva', 'total']:
                acum.ventas_total[k] = acum.ventas_total.get(k, 0) + f29.ventas_total.get(k, 0)

            for k in ['td', 'exento', 'neto', 'iva_rec', 'iva_no_rec', 'total']:
                acum.compras_total[k] = acum.compras_total.get(k, 0) + f29.compras_total.get(k, 0)

            acum.IVAPP += f29.IVAPP
            acum.TT += f29.TT
            acum.arriendos_pagados += f29.arriendos_pagados
            acum.gastos_generales_boletas += f29.gastos_generales_boletas

            # Remanente: solo el del último mes
            acum.remanente = f29.remanente

            # ppm, remuneraciones, honorarios: suma de valores numéricos
            for seccion in ['ppm', 'remuneraciones', 'honorarios']:
                sec = getattr(f29, seccion, {})
                if not sec:
                    continue
                target = getattr(acum, seccion)
                if not target:
                    setattr(acum, seccion, sec.copy())
                else:
                    for k, v in sec.items():
                        if isinstance(v, (int, float)):
                            target[k] = target.get(k, 0) + v

        # 3. Encabezado del último mes
        ultimo_f29 = f29s[-1]
        enc = ultimo_f29.encabezado.copy()
        enc['titulo'] = 'RESUMEN ACUMULADO FORMULARIO 29'
        acum.encabezado = enc

        return acum

    def _generar_rango_texto(self, periodos: List[str], año: str) -> str:
        if not periodos:
            return f"Año {año}"
        primer_mes = periodos[0].split("-")[1]
        ultimo_mes = periodos[-1].split("-")[1]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"{meses[int(primer_mes)-1]} - {meses[int(ultimo_mes)-1]} {año}"

    def _to_response(self, anual) -> ResumenAnualResponse:
        periodos = anual.periodos_incluidos_json or []
        meses_count = len(periodos)
        contenido = ResumenAnualContenido(**anual.detalles_json) if anual.detalles_json else ResumenAnualContenido()

        return ResumenAnualResponse(
            id=anual.id,
            cliente_id=anual.cliente_id,
            año=anual.año,
            estado=anual.estado,
            creado_por_usuario_id=anual.creado_por_usuario_id,
            created_at=anual.created_at,
            updated_at=anual.updated_at,
            periodos_incluidos=periodos,
            contenido=contenido,
            meses_incluidos_count=meses_count,
            rango_texto=self._generar_rango_texto(periodos, anual.año),
        )

    def get_dashboard_anual(self, current_user: Usuario, anio: str) -> Dict:
        if not hasattr(current_user, 'empresa_id') or not current_user.empresa_id:
            raise ValueError("Usuario sin empresa asignada")

        repo_cliente = ClienteRepository(self.db)
        clientes = repo_cliente.find_by_empresa(
            empresa_id=current_user.empresa_id,
            solo_activos=True,
            skip=0,
            limit=1000,
        )

        resultado = []
        for cliente in clientes:
            anual = self.repo_anual.get_by_cliente_and_año(cliente.id, anio)
            f29s = self.repo_anual.get_all_f29_del_año(cliente.id, anio)
            total_f29 = len(f29s)
            meses_incluidos = len(anual.periodos_incluidos_json) if anual else 0
            f29_pendientes = total_f29 - meses_incluidos if anual else total_f29

            resultado.append({
                "id": cliente.id,
                "nombre": cliente.razon_social,
                "rut": cliente.rut,
                "resumen_anual": {
                    "existe": bool(anual),
                    "estado": anual.estado.value if anual else None,
                    "meses_incluidos": meses_incluidos,
                    "f29_pendientes": max(0, f29_pendientes),
                }
            })

        return {
            "clientes": resultado,
            "total_clientes": len(clientes),
            "total_generados": sum(1 for c in resultado if c["resumen_anual"]["existe"]),
            "total_pendientes": sum(1 for c in resultado if not c["resumen_anual"]["existe"]),
        }