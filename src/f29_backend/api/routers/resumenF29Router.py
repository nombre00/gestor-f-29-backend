from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date 

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario
from f29_backend.infrastructure.persistence.models.cliente import Cliente
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import EstadoF29
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository
from f29_backend.infrastructure.persistence.repository.resumenF29Repository import ResumenF29Repository
from f29_backend.api.schemas.resumenF29Schema import ResumenF29Create, ResumenF29Update, ResumenF29Response,ResumenF29ListItem, CambiarEstadoRequest, DashboardResumenResponse,ResumenF29DetalleResponse



router = APIRouter(prefix="/api/resumenes", tags=["resumenes-f29"])


# Funcion auxiliar para verificar los permisos sobre un cliente.
def _verificar_acceso_cliente(cliente: Cliente, current_user: Usuario):
    if not cliente:  # Si el cliente no existe
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    if cliente.empresa_id != current_user.empresa_id:  # Si es su cliente
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    if current_user.rol == RolUsuario.CONTADOR:  # Solo rol ADMIN puede borrar un cliente
        if cliente.asignado_a_usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")



# Funcion que busca los datos del dashboard. 
@router.get("/dashboard", response_model=DashboardResumenResponse)
def obtener_datos_dashboard(mes: int = None,anio: int = None,db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)):
    # Buscamos el mes y año actual y los guardamos en varibales, esto para buscar los documentos este mes.
    hoy = date.today()
    mes = mes or hoy.month
    anio = anio or hoy.year

    repo = ResumenF29Repository(db)  # Nos conectamos.

    resumenes = repo.find_by_usuario_y_mes(current_user.id, anio, mes)  # Buscamos los resúmenes del mes
    pendientes = repo.find_clientes_sin_resumen_en_mes(current_user.id, anio, mes)  # Buscamos los clientes sin resúmenes del mes.

    # Generamos el esquema de la respuesta
    resumenes_items = [
        ResumenF29ListItem(
            id=r.id,
            cliente_id=r.cliente_id,
            rut_cliente=r.cliente.rut,
            razon_social_cliente=r.cliente.razon_social,
            nro_cliente=r.cliente.nro_cliente,
            periodo=r.periodo,
            estado=r.estado,
            iva_a_pagar=r.iva_a_pagar,
            created_at=r.created_at
        )
        for r in resumenes
    ]

    # Retornamos la respuesta con el esquema incluido
    return {
        "mes": mes,
        "anio": anio,
        "resumenes_hechos": resumenes_items,
        "clientes_pendientes": pendientes,
        "total_hechos": len(resumenes_items),
        "total_pendientes": len(pendientes)
    }



# Lista todos los resúmenes F29 de un cliente, ordenados por período desc
@router.get("/cliente/{cliente_id}", response_model=list[ResumenF29ListItem])
def listar_resumenes_cliente(cliente_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    cliente_repo = ClienteRepository(db)  # Cargamos el repositorio de clientes.
    cliente = cliente_repo.find_by_id(cliente_id)  # LLamamos a la funcion que revisa por rol
    _verificar_acceso_cliente(cliente, current_user)  # Verificamos permisos.

    repo = ResumenF29Repository(db)  # Cargamos el repositorio de f29s
    resumenes = repo.find_by_cliente(cliente_id)  # LLamamos a la funcion que revisa por rol

    # Retornamos los esquemas iterativamente
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



# Devuelve un resumen F29 completo por ID, incluyendo detalles_json, usado por VistaResumenF29 cuando se navega desde el dashboard
@router.get("/{resumen_id}", response_model=ResumenF29DetalleResponse)
def obtener_resumen_por_id(resumen_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    return resumen



# Crea un nuevo resumen F29 para un cliente
@router.post("", response_model=ResumenF29Response, status_code=status.HTTP_201_CREATED)
def crear_resumen(resumen_data: ResumenF29Create,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
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



# Actualiza datos de un resumen F29
@router.put("/{resumen_id}", response_model=ResumenF29Response)
def actualizar_resumen(resumen_id: int,resumen_data: ResumenF29Update,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ResumenF29Repository(db)
    resumen = repo.find_by_id(resumen_id)

    if not resumen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)
    cliente = cliente_repo.find_by_id(resumen.cliente_id)
    _verificar_acceso_cliente(cliente, current_user)

    campos = {k: v for k, v in resumen_data.model_dump().items() if v is not None}
    return repo.update(resumen_id, **campos)



# Cambia el estado de un resumen F29
@router.put("/{resumen_id}/estado", response_model=ResumenF29Response)
def cambiar_estado(resumen_id: int,estado_data: CambiarEstadoRequest,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ResumenF29Repository(db)  # Cargamos el repositorio de f29s
    resumen = repo.find_by_id(resumen_id)  # Buscamos por id

    if not resumen:  # Si no encontramos el f29
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    cliente_repo = ClienteRepository(db)  # Cargamos el repositorio de clientes
    cliente = cliente_repo.find_by_id(resumen.cliente_id)  # Buscamos por id
    _verificar_acceso_cliente(cliente, current_user)  # Revisamos si tenemos acceso

    return repo.cambiar_estado(resumen_id, estado_data.estado)  # Si todo bien cambiamos el estado.



# Elimina un resumen F29, solo se pueden eliminar resúmenes en estado BORRADOR.
@router.delete("/{resumen_id}", status_code=status.HTTP_200_OK)
def eliminar_resumen(resumen_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ResumenF29Repository(db)  # Cargamos el repositorio de f29s
    resumen = repo.find_by_id(resumen_id)  # Buscamos por id

    if not resumen:  # Si no encontramos el f29
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resumen no encontrado")

    if resumen.estado != EstadoF29.BORRADOR:  # Revisamos el estado del f29, si no es borrador levantamos una exceptión
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden eliminar resúmenes en estado borrador"
        )

    cliente_repo = ClienteRepository(db)  # Cargamos el repositorio de clientes
    cliente = cliente_repo.find_by_id(resumen.cliente_id)  # Buscamos por id
    _verificar_acceso_cliente(cliente, current_user)  # Revisamos si tenemos acceso

    repo.delete(resumen_id)  # Borramos el resumen.
    return {"message": "Resumen eliminado exitosamente"}