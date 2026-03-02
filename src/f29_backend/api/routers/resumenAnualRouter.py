# api/routers/resumenAnualRouter.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user
from f29_backend.infrastructure.persistence.models.usuario import Usuario
from f29_backend.application.services.resumenAnualService import ResumenAnualService
from f29_backend.api.schemas.resumenAnualSchema import  ResumenAnualResponse, ResumenAnualListItem
from f29_backend.infrastructure.persistence.repository.resumenAnualRepository import ResumenAnualRepository, EstadoResumenAnual


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/api/f29", tags=["f29"])



# Ruta simple.
# Busca la info del dashboard gestorResumenesAnuales.
@router.get("/resumen-anual/dashboard", response_model=Dict, summary="Dashboard de resúmenes anuales para el usuario actual",)
def dashboard_resumen_anual(anio: str = Query(..., description="Año a consultar (formato YYYY, ej: 2025)"),
    current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db),):
    service = ResumenAnualService(db)  # Nos conectamos.
    try:  # LLamamos al service que hace todo.
        return service.get_dashboard_anual(current_user=current_user, anio=anio)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error al obtener dashboard anual: {str(e)}")
    


# Ruta simple + parámetro dinamico.
# Retorna una lista resumida de todos los resúmenes anuales existentes para un cliente.
# Aun no lo ocupamos, sirve para una futura tabla de un dashboard que indique los resumenes anuales hechos para un cliente.
@router.get("/resumen-anual/por-cliente/{cliente_id}",response_model=List[ResumenAnualListItem],summary="Lista todos los resúmenes anuales de un cliente (para dashboard)",)
def listar_resumenes_anuales_cliente(cliente_id: int,current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db),):
    repo = ResumenAnualRepository(db)  # Nos conectamos.
    anuales = repo.get_all_by_cliente(cliente_id)  # Buscamos los resúmenes.
    # Mapeamos a lista resumida
    items = []  # Lista de resumenesAnuales resumidos.
    for anual in anuales:   # Por resumen en lista.
        periodos = anual.periodos_incluidos_json or []  # Periodos de los f29s incluidos en este resumenAnual.
        items.append(  # agregamos a la lista un esquema de respuesta REST: 
            ResumenAnualListItem(  # Este esquema en particular, sirve para una futura tabla.
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
# Retorna el resumen anual acumulado para el cliente y año indicados, es llamado cuando vamos a la pagina previsualizar resumenAnual.
@router.get("/resumen-anual/{cliente_id}/{anio}",response_model=ResumenAnualResponse,summary="Obtiene o crea el resumen anual de un cliente para un año específico",)
def get_resumen_anual(cliente_id: int,anio: str,current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db),):
    service = ResumenAnualService(db)  # Nos conectamos.
    try:  # LLamamos a la función del service que hace todo.
        anual = service.get_or_create_anual(cliente_id=cliente_id,año=anio,usuario_id=current_user.id)
        return anual
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error al obtener/crear resumen anual: {str(e)}")


# Recalcula un resumen anual, es llamado en el botón recalcular de la pagina previsualizar resumenAnual.
# Cuando revisemos el front, ve si llamas esta función pasándole ResumenAnualRecalcularRequest, sino se saca.
@router.post("/resumen-anual/{cliente_id}/{anio}/recalcular",response_model=ResumenAnualResponse,summary="Recalcula el resumen anual sumando todos los F29 existentes del año",)
def recalcular_resumen_anual(cliente_id: int,anio: str,
    current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db),):

    service = ResumenAnualService(db)  # Nos conectamos.
    try:  # LLamamos a la función del service que hace todo.
        anual_actualizado = service.recalcular_anual(cliente_id=cliente_id,año=anio,usuario_id=current_user.id)
        return anual_actualizado
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error al recalcular resumen anual: {str(e)}")


# Cambiar estado de un resumenAnual.
# Se llama en el dashboard, creo, revisa.
@router.patch("/resumen-anual/estado/{anual_id}",response_model=ResumenAnualResponse,summary="Cambia el estado del resumen anual (borrador → revisado, etc.)",)
def cambiar_estado_resumen_anual(anual_id: int,nuevo_estado: EstadoResumenAnual,current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db),):
    repo = ResumenAnualRepository(db)  # Nos conectamos.
    anual = repo.get_by_id(anual_id)  # buscamos por id.
    if not anual:  # Si no lo encontramos.
        raise HTTPException(status_code=404, detail="Resumen anual no encontrado")
    # Si lo encontramos.
    anual_actualizado = repo.update(anual, estado=nuevo_estado)  # Cambiamos el estado.
    service = ResumenAnualService(db)  # LLamamos al service para formatear la respuesta.
    return service._to_response(anual_actualizado)  # Retornamos la respuesta del resumenAnual actualizado.
















