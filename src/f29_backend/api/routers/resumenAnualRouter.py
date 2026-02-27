# api/routers/resumenAnualRouter.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user
from f29_backend.infrastructure.persistence.models.usuario import Usuario
from f29_backend.application.services.resumenAnualService import ResumenAnualService
from f29_backend.api.schemas.resumenAnualSchema import (
    ResumenAnualResponse,
    ResumenAnualRecalcularRequest,
    ResumenAnualListItem,
)
from f29_backend.infrastructure.persistence.repository.resumenAnualRepository import ResumenAnualRepository, EstadoResumenAnual

router = APIRouter(prefix="/api/f29", tags=["f29"])



# Ruta simple.
@router.get("/resumen-anual/dashboard",
    response_model=Dict,
    summary="Dashboard de resúmenes anuales para el usuario actual",
)
def dashboard_resumen_anual(
    anio: str = Query(..., description="Año a consultar (formato YYYY, ej: 2025)"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Devuelve datos para la página de selección de resúmenes anuales:
    - Lista de clientes con info del resumen anual del año seleccionado
    - Totales para tarjetas (generados / pendientes)
    """
    service = ResumenAnualService(db)
    try:
        return service.get_dashboard_anual(current_user=current_user, anio=anio)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener dashboard anual: {str(e)}"
        )
    

# Ruta simple + parámetro dinamico.
@router.get("/resumen-anual/por-cliente/{cliente_id}",
    response_model=List[ResumenAnualListItem],
    summary="Lista todos los resúmenes anuales de un cliente (para dashboard)",
)
def listar_resumenes_anuales_cliente(
    cliente_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna una lista resumida de todos los resúmenes anuales existentes para un cliente.
    Útil para mostrar en el dashboard del contador o admin.
    """
    # Nota: este endpoint requiere implementar un método en el repository
    # Por ahora lo dejamos como placeholder → puedes copiar/adaptar del repo de F29
    
    repo = ResumenAnualRepository(db)
    # Ejemplo de implementación que faltaría en el repo:
    # def get_all_by_cliente(self, cliente_id: int) -> List[ResumenAnual]:
    #     stmt = select(ResumenAnual).where(ResumenAnual.cliente_id == cliente_id)
    #     return self.db.scalars(stmt).all()
    
    anuales = []  # repo.get_all_by_cliente(cliente_id)
    
    # Mapear a lista resumida
    items = []
    for anual in anuales:
        periodos = anual.periodos_incluidos_json or []
        items.append(
            ResumenAnualListItem(
                id=anual.id,
                cliente_id=anual.cliente_id,
                año=anual.año,
                estado=anual.estado,
                meses_incluidos_count=len(periodos),
                rango_texto=ResumenAnualService(db)._generar_rango_texto(periodos, anual.año),
                created_at=anual.created_at,
                updated_at=anual.updated_at,
            )
        )
    
    return items



# Rutas dinámicas.
@router.get(
    "/resumen-anual/{cliente_id}/{anio}",
    response_model=ResumenAnualResponse,
    summary="Obtiene o crea el resumen anual de un cliente para un año específico",
)
def get_resumen_anual(
    cliente_id: int,
    anio: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna el resumen anual acumulado para el cliente y año indicados.
    Si no existe, lo crea vacío (en estado borrador).
    Solo permite acceso si el usuario tiene relación con el cliente/empresa.
    """
    service = ResumenAnualService(db)
    
    # Aquí podrías agregar validación de permisos:
    # - si current_user es contador → debe tener el cliente asignado
    # - si es admin → debe pertenecer a la empresa del cliente
    # Por ahora lo dejamos simple
    
    try:
        anual = service.get_or_create_anual(
            cliente_id=cliente_id,
            año=anio,
            usuario_id=current_user.id
        )
        return anual
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener/crear resumen anual: {str(e)}"
        )


@router.post(
    "/resumen-anual/{cliente_id}/{anio}/recalcular",
    response_model=ResumenAnualResponse,
    summary="Recalcula el resumen anual sumando todos los F29 existentes del año",
)
def recalcular_resumen_anual(
    cliente_id: int,
    anio: str,
    request: ResumenAnualRecalcularRequest = None,  # por ahora no usa body, pero lo dejamos preparado
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recalcula desde cero el resumen anual para el cliente y año.
    - Busca todos los F29 del período
    - Acumula los valores
    - Actualiza (o crea) el registro en BD
    """
    service = ResumenAnualService(db)
    
    try:
        anual_actualizado = service.recalcular_anual(
            cliente_id=cliente_id,
            año=anio,
            usuario_id=current_user.id
        )
        return anual_actualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recalcular resumen anual: {str(e)}"
        )


# Opcional: cambiar estado (revisado, etc.)
@router.patch(
    "/resumen-anual/estado/{anual_id}",
    response_model=ResumenAnualResponse,
    summary="Cambia el estado del resumen anual (borrador → revisado, etc.)",
)
def cambiar_estado_resumen_anual(
    anual_id: int,
    nuevo_estado: EstadoResumenAnual,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ResumenAnualRepository(db)
    anual = repo.get_by_id(anual_id)  # necesitarías implementar get_by_id en el repo
    
    if not anual:
        raise HTTPException(status_code=404, detail="Resumen anual no encontrado")
    
    # Validación simple de permisos (puedes fortalecerla)
    if anual.creado_por_usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este resumen")
    
    anual_actualizado = repo.update(anual, estado=nuevo_estado)
    service = ResumenAnualService(db)
    return service._to_response(anual_actualizado)
















