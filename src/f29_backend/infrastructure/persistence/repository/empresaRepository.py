# Accesador de la clase Empresa.


# Bibliotecas.
from sqlalchemy.orm import Session
from typing import List, Optional
# Módulos.
from f29_backend.infrastructure.persistence.models import Empresa

class EmpresaRepository:
    # Constructor que genera la conección.
    def __init__(self, db: Session):
        self.db = db
    
    # Crear una empresa.
    def create(self, rut: str, razon_social: str, nombre_comercial: str = None, email: str = None, telefono: str = None) -> Empresa:
        empresa = Empresa(
            rut=rut,
            razon_social=razon_social,
            nombre_comercial=nombre_comercial,
            email=email,
            telefono=telefono,
            activa=True
        )
        self.db.add(empresa)
        self.db.commit()
        self.db.refresh(empresa)
        return empresa
    

    # Búsquedas unitarias.
    # Buscar por id.
    def find_by_id(self, empresa_id: int) -> Optional[Empresa]:
        return self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    # Buscar por rut.
    def find_by_rut(self, rut: str) -> Optional[Empresa]:
        return self.db.query(Empresa).filter(Empresa.rut == rut).first()
    

    # Listar.
    # Lista todas las empresas.
    def find_all(self, skip: int = 0, limit: int = 100, solo_activas: bool = True) -> List[Empresa]:
        query = self.db.query(Empresa)
        if solo_activas:
            query = query.filter(Empresa.activa == True)
        return query.offset(skip).limit(limit).all()
    

    # Actualizaciones.
    # Actualizar.
    def update(self, empresa_id: int, **kwargs) -> Optional[Empresa]:
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return None
        for key, value in kwargs.items():
            if hasattr(empresa, key):
                setattr(empresa, key, value)
        self.db.commit()
        self.db.refresh(empresa)
        return empresa
    
    # Desactivar.
    def deactivate(self, empresa_id: int) -> bool:
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return False
        empresa.activa = False
        self.db.commit()
        return True
    

    # Borrar.
    def delete_permanently(self, empresa_id: int) -> bool:
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return False
        self.db.delete(empresa)
        self.db.commit()
        return True