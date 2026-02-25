from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario
from f29_backend.infrastructure.persistence.models.cliente import Cliente
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository
from f29_backend.infrastructure.persistence.repository.resumenF29Repository import ResumenF29Repository
from f29_backend.api.schemas.resumenF29Schema import (
    ResumenF29Create, ResumenF29Update, ResumenF29Response,
    ResumenF29ListItem, CambiarEstadoRequest, DashboardResumenResponse,
    ResumenF29DetalleResponse
)

router = APIRouter(prefix="/api/resumenes", tags=["resumenes-f29"])


def _verificar_acceso_cliente(cliente: Cliente, current_user: Usuario):
    """Helper para verificar permisos sobre un cliente"""
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    if current_user.rol == RolUsuario.CONTADOR:
        if cliente.asignado_a_usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")


@router.get("/dashboard", response_model=DashboardResumenResponse)
def obtener_datos_dashboard(
    mes: int = None,
    anio: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Datos para el dashboard del contador:
    - Resúmenes F29 hechos en el mes
    - Clientes sin resumen F29 en el mes
    Por defecto usa el mes y año actuales.
    """
    hoy = date.today()
    mes = mes or hoy.month
    anio = anio or hoy.year

    repo = ResumenF29Repository(db)

    resumenes = repo.find_by_usuario_y_mes(current_user.id, anio, mes)
    pendientes = repo.find_clientes_sin_resumen_en_mes(current_user.id, anio, mes)

    resumenes_items = [
        ResumenF29ListItem(
            id=r.id,
            cliente_id=r.cliente_id,
            rut_cliente=r.cliente.rut,
            razon_social_cliente=r.cliente.razon_social,
            periodo=r.periodo,
            estado=r.estado,
            iva_a_pagar=r.iva_a_pagar,
            created_at=r.created_at
        )
        for r in resumenes
    ]

    return {
        "mes": mes,
        "anio": anio,
        "resumenes_hechos": resumenes_items,
        "clientes_pendientes": pendientes,
        "total_hechos": len(resumenes_items),
        "total_pendientes": len(pendientes)
    }


@router.get("/cliente/{cliente_id}", response_model=list[ResumenF29ListItem])
def listar_resumenes_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos los resúmenes F29 de un cliente, ordenados por período desc"""
    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    repo = ResumenF29Repository(db)
    resumenes = repo.find_by_cliente(cliente_id)

    return [
        ResumenF29ListItem(
            id=r.id,
            cliente_id=r.cliente_id,
            rut_cliente=r.cliente.rut,
            razon_social_cliente=r.cliente.razon_social,
            periodo=r.periodo,
            estado=r.estado,
            iva_a_pagar=r.iva_a_pagar,
            created_at=r.created_at
        )
        for r in resumenes
    ]


@router.get("/{resumen_id}", response_model=ResumenF29DetalleResponse)
def obtener_resumen_por_id(
    resumen_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve un resumen F29 completo por ID, incluyendo detalles_json.
    Usado por VistaResumenF29 cuando se navega desde el dashboard.
    """
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    return resumen


@router.post("", response_model=ResumenF29Response, status_code=status.HTTP_201_CREATED)
def crear_resumen(
    resumen_data: ResumenF29Create,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un nuevo resumen F29 para un cliente"""
    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen_data.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    repo = ResumenF29Repository(db)

    existente = repo.find_by_cliente_periodo(resumen_data.cliente_id, resumen_data.periodo)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un resumen F29 para este cliente en el período {resumen_data.periodo}"
        )

    campos = resumen_data.model_dump(exclude={'cliente_id', 'periodo'})
    return repo.create(
        cliente_id=resumen_data.cliente_id,
        periodo=resumen_data.periodo,
        creado_por_usuario_id=current_user.id,
        **{k: v for k, v in campos.items() if v is not None}
    )


@router.put("/{resumen_id}", response_model=ResumenF29Response)
def actualizar_resumen(
    resumen_id: int,
    resumen_data: ResumenF29Update,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza datos de un resumen F29"""
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    campos = {k: v for k, v in resumen_data.model_dump().items() if v is not None}
    return repo.update(resumen_id, **campos)


@router.put("/{resumen_id}/estado", response_model=ResumenF29Response)
def cambiar_estado(
    resumen_id: int,
    estado_data: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cambia el estado de un resumen F29"""
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    return repo.cambiar_estado(resumen_id, estado_data.estado)


@router.delete("/{resumen_id}", status_code=status.HTTP_200_OK)
def eliminar_resumen(
    resumen_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina un resumen F29.
    Solo se pueden eliminar resúmenes en estado BORRADOR.
    """
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    from f29_backend.infrastructure.persistence.models.resumenF29Modelo import EstadoF29
    if resumen.estado != EstadoF29.BORRADOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden eliminar resúmenes en estado borrador"
        )

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    repo.delete(resumen_id)
    return {"message": "Resumen eliminado exitosamente"}