# Router de empresas.


# Bibliotecas.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Módulos.
from f29_backend.core.database import get_db  # Conección.
from f29_backend.core.security import get_current_user, require_role  # Seguridad.
from f29_backend.infrastructure.persistence.models.usuario import RolUsuario  # Moldelo de la base de datos.
from f29_backend.infrastructure.persistence.repository.empresaRepository import EmpresaRepository  # Accesadores.
from f29_backend.api.schemas.empresaSchema import EmpresaCreate, EmpresaUpdate, EmpresaResponse, EmpresaListResponse  # Esquema de respuestas REST.


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/api/empresas", tags=["empresas"])



# Buscar.
# Lista todas las empresas, función exclusiva del rol SUPER.
@router.get("", response_model=EmpresaListResponse)
def listar_empresas(db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    empresas = repo.find_all()  # Buscamos todo de esa tabla.
    if not empresas:  # Si no retorna datos.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron empresas.")
    return {"empresas": empresas, "total": len(empresas)}  # Si todo bien, retornamos.


# Buscar empresa por id, función exclusiva del rol SUPER.
@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    empresa = repo.find_by_id(empresa_id)  # Buscamosla empresa.
    if not empresa:  # Si no retorna datos.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    return empresa  # Si todo bien, retornamos.



# Crear empresa, función exclusiva del rol SUPER.
@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def crear_empresa(empresa_data: EmpresaCreate, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    if repo.find_by_rut(empresa_data.rut): # Resivamos que no exista una empresa ingresada con el mismo rut.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe una empresa con el RUT {empresa_data.rut}.")
    return repo.create(  # Si todo bien, creamos la nueva empresa.
        rut=empresa_data.rut,
        razon_social=empresa_data.razon_social,
        nombre_comercial=empresa_data.nombre_comercial,
        email=empresa_data.email,
        telefono=empresa_data.telefono
    )


# Actualizar empresa, función exclusiva del rol SUPER.
@router.put("/{empresa_id}", response_model=EmpresaResponse)
def actualizar_empresa(empresa_id: int, empresa_data: EmpresaUpdate, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    empresa = repo.find_by_id(empresa_id)  # Buscamos la empresa.
    if not empresa:  # Si no retorna datos.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    # Acá k = llave, v = valor dentro del formulario IF v is not None
    # campos es el diccionario que recibe los tuples encontrados.
    campos = {k: v for k, v in empresa_data.model_dump().items() if v is not None}  # Si todo bien editamos.
    return repo.update(empresa_id, **campos)  # **campos = varios argumentos.  Si todo bien, editamos.


# Desactivar empresa, función exclusiva del rol SUPER.
@router.put("/{empresa_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    empresa = repo.find_by_id(empresa_id)  # Buscamos.
    if not empresa:  # Si no retorna datos.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    if not empresa.activa:  # Si la empresa no está activa.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La empresa ya se encuentra inactiva.")
    repo.deactivate(empresa_id)  # Si todo bien, desactivamos.
    return {"message": "Empresa desactivada exitosamente"}


# Eliminar empresa permanentemente.
@router.delete("/{empresa_id}", status_code=status.HTTP_200_OK)
def eliminar_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)  # Nos conectamos.
    empresa = repo.find_by_id(empresa_id)  # Buscamos.
    if not empresa:  # Si no retorna datos.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    repo.delete_permanently(empresa_id)  # Si todo bien eliminamos.
    return {"message": "Empresa eliminada exitosamente"}