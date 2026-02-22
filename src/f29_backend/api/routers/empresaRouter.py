# Router de empresas.


# Bibliotecas.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Módulos.
from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user, require_role
from f29_backend.infrastructure.persistence.models.usuario import RolUsuario
from f29_backend.infrastructure.persistence.repository.empresaRepository import EmpresaRepository
from f29_backend.api.schemas.empresaSchema import EmpresaCreate, EmpresaUpdate, EmpresaResponse, EmpresaListResponse


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/api/empresas", tags=["empresas"])


# Lista todas las empresas.
@router.get("", response_model=EmpresaListResponse)
def listar_empresas(db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    empresas = repo.find_all()
    if not empresas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron empresas.")
    return {"empresas": empresas, "total": len(empresas)}


# Buscar empresa por id.
@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    empresa = repo.find_by_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    return empresa


# Crear empresa.
@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def crear_empresa(empresa_data: EmpresaCreate, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    if repo.find_by_rut(empresa_data.rut):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe una empresa con el RUT {empresa_data.rut}.")
    return repo.create(
        rut=empresa_data.rut,
        razon_social=empresa_data.razon_social,
        nombre_comercial=empresa_data.nombre_comercial,
        email=empresa_data.email,
        telefono=empresa_data.telefono
    )


# Actualizar empresa.
@router.put("/{empresa_id}", response_model=EmpresaResponse)
def actualizar_empresa(empresa_id: int, empresa_data: EmpresaUpdate, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    empresa = repo.find_by_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    campos = {k: v for k, v in empresa_data.model_dump().items() if v is not None}
    return repo.update(empresa_id, **campos)


# Desactivar empresa.
@router.put("/{empresa_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    empresa = repo.find_by_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    if not empresa.activa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La empresa ya se encuentra inactiva.")
    repo.delete(empresa_id)
    return {"message": "Empresa desactivada exitosamente"}


# Eliminar empresa permanentemente.
@router.delete("/{empresa_id}", status_code=status.HTTP_200_OK)
def eliminar_empresa(empresa_id: int, db: Session = Depends(get_db), current_user = Depends(require_role([RolUsuario.SUPER]))):
    repo = EmpresaRepository(db)
    empresa = repo.find_by_id(empresa_id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la empresa.")
    repo.delete_permanently(empresa_id)
    return {"message": "Empresa eliminada exitosamente"}