# Router de clientes.


# Bibliotecas.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Módulos.
from f29_backend.core.database import get_db  # La conección.
from f29_backend.core.security import get_current_user, require_role  # Seguridad.
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario  # Moldelo de la base de datos.
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository  # Accesadores de clientes.
from f29_backend.api.schemas.clienteSchema import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse  # Schemas de respuesta REST.


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/api/clientes", tags=["clientes"])


# Lista clientes, sensible al rol de quien consulta.
@router.get("", response_model=ClienteListResponse)
def listar_clientes(db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    # asignamos la conección.
    repo = ClienteRepository(db)
    # Buscamos acorde al rol.
    if current_user.rol == RolUsuario.SUPER  or  current_user.rol == RolUsuario.ADMIN:  # Si es SUPER o ADMIN:
        clientes = repo.find_by_empresa(current_user.empresa_id)  # Buscamos todos los clientes de la empresa.
    elif current_user.rol == RolUsuario.CONTADOR:  # Si es CONTADOR:
        clientes = repo.find_by_usuario(current_user.id)  # Buscamos clientes asociados a ese contador.
    # Revisamos que encontramos.
    if not clientes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontraron clientes.")
    return {"clientes": clientes, "total": len(clientes)}  # Si todo sale bien retornamos los clientes.


# Busca un cliente por id, sensible al rol de quien consulta.
@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ClienteRepository(db)
    # Buscamos acorde al rol.
    if current_user.rol == RolUsuario.SUPER:
        cliente = repo.find_by_id(cliente_id)
    elif current_user.rol == RolUsuario.ADMIN:
        cliente = repo.find_by_id_y_empresa(cliente_id, current_user.empresa_id)  # Puede buscar cualquier cliente de la empresa.
    elif current_user.rol == RolUsuario.CONTADOR:
        cliente = repo.find_by_id_y_usuario(cliente_id, current_user.id)  # Puede buscar clientes asociados a su cuenta.
    # Revisamos la respuesta.
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontró el cliente.")
    return cliente


#### Falta revisarlo y compararlo con la GI.
# Crea un nuevo cliente, sensible al rol de quien realiza la operación.
@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente_data: ClienteCreate,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    repo = ClienteRepository(db)

    # Verificar RUT duplicado en la empresa
    if repo.find_by_rut(current_user.empresa_id, cliente_data.rut):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Ya existe un cliente con el RUT {cliente_data.rut} en esta empresa")
    print("=== DEBUG CURRENT USER ===")
    print(type(current_user))
    print(current_user)  # o current_user.model_dump() si es Pydantic
    print("id:", getattr(current_user, 'id', None))
    print("empresa_id:", getattr(current_user, 'empresa_id', None))
    print("rol:", getattr(current_user, 'rol', None))

    """ # Determinar asignación
    if current_user.rol in [RolUsuario.ADMIN, RolUsuario.SUPER]:
        # asignado_a = cliente_data.asignado_a_usuario_id or current_user.id
        asignado_a = current_user.id
    else:
        asignado_a = current_user.id  # Contador siempre se asigna a sí mismo """
    asignado_a = current_user.id

    # Extraer campos opcionales
    campos_opcionales = cliente_data.model_dump(exclude={'rut', 'razon_social'})

    return repo.create(
        empresa_id=current_user.empresa_id,
        asignado_a_usuario_id=asignado_a,
        rut=cliente_data.rut,
        razon_social=cliente_data.razon_social,
        **{k: v for k, v in campos_opcionales.items() if v is not None}
    )


# Actualiza datos de un cliente.
@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int,cliente_data: ClienteUpdate,db: Session = Depends(get_db),current_user: Usuario = Depends(get_current_user)):
    # Primero nos conectamos a la base de datos.
    repo = ClienteRepository(db)
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        cliente = repo.find_by_id(cliente_id)
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        cliente = repo.find_by_id_y_empresa(cliente_id, current_user.empresa_id)
    elif current_user.rol == RolUsuario.CONTADOR:  # Si es contador buscamos por id y id del contador.
        cliente = repo.find_by_id_y_usuario(cliente_id, current_user.id)
    # Revisamos que encontramos lo que buscamos.
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontró el cliente.")
    # Revisamos que el mail ingresado no se encuentre asociado a otro cliente.
    if cliente_data.contacto_email:
        if  repo.revisar_mail(cliente.id, cliente_data.contacto_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Este email ya está en uso por otro cliente")
    # Preparamos los datos.
    campos = {k: v for k, v in cliente_data.model_dump().items() if v is not None}
    actualizado = repo.update(cliente.id, **campos)  # Ejecutamos el actualizar.

    return actualizado


# Desactiva un cliente.
@router.put("/{cliente_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_cliente(cliente_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))):
    # 1. Primero nos conectamos a la base de datos.
    repo = ClienteRepository(db)
    # Buscamos acorde a permisos.
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        cliente = repo.find_by_id(cliente_id)
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        cliente = repo.find_by_id_y_empresa(cliente_id, current_user.empresa_id)
    # Revisamos que encontramos el cliente.
    if not cliente: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontró el cliente.")
    # Revisamos que el cliente esté activo.
    if not cliente.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El cliente no se encuentra activo.")
    # Desactivamos al cliente.
    repo.deactivate(cliente_id)
    return {"message": "Cliente desactivado exitosamente"}


# Reactiva un cliente.
@router.put("/{cliente_id}/reactivar", status_code=status.HTTP_200_OK)
def reactivar_cliente(cliente_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))):
    # 1. Primero nos conectamos a la base de datos.
    repo = ClienteRepository(db)
    # Buscamos acorde a permisos.
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        cliente = repo.find_by_id(cliente_id)
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        cliente = repo.find_by_id_y_empresa(cliente_id, current_user.empresa_id)
    # Revisamos que encontramos el cliente.
    if not cliente: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se encontró el cliente.")
    # Revisamos que el cliente esté activo.
    if cliente.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El cliente ya se encuentra activo.")
    # Desactivamos al cliente.
    repo.activate(cliente_id)
    return {"message": "Cliente reactivado exitosamente"}



# Reasignar cliente.
@router.put("/{cliente_id}/reasignar", response_model=ClienteResponse)
def reasignar_cliente(cliente_id: int,nuevo_usuario_id: int,db: Session = Depends(get_db),current_user: Usuario = Depends(require_role([RolUsuario.ADMIN, RolUsuario.SUPER]))):
    repo = ClienteRepository(db)
    cliente = repo.find_by_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    # Verificar que el nuevo usuario existe, pertenece a la empresa y es contador.
    nuevo_usuario = db.query(Usuario).filter(Usuario.id == nuevo_usuario_id,Usuario.empresa_id == current_user.empresa_id,Usuario.activo == True).first()

    if not nuevo_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="El usuario destino no existe o no pertenece a esta empresa")

    if nuevo_usuario.rol != RolUsuario.CONTADOR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Solo se puede reasignar a un usuario con rol contador")

    return repo.reasignar(cliente_id, nuevo_usuario_id)