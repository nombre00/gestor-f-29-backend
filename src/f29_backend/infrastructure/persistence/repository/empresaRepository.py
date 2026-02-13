# Accesador de la clase Empresa.


# Bibliotecas.
from sqlalchemy.orm import Session
from typing import List, Optional
# Módulos.
from f29_backend.infrastructure.persistence.models import Empresa

class EmpresaRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, rut: str, razon_social: str, 
               nombre_comercial: str = None, email: str = None,
               telefono: str = None) -> Empresa:
        """Crea una nueva empresa"""
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
    
    def find_by_id(self, empresa_id: int) -> Optional[Empresa]:
        """Busca empresa por ID"""
        return self.db.query(Empresa).filter(Empresa.id == empresa_id).first()
    
    def find_by_rut(self, rut: str) -> Optional[Empresa]:
        """Busca empresa por RUT"""
        return self.db.query(Empresa).filter(Empresa.rut == rut).first()
    
    def find_all(self, skip: int = 0, limit: int = 100, 
                 solo_activas: bool = True) -> List[Empresa]:
        """Lista empresas con paginación"""
        query = self.db.query(Empresa)
        if solo_activas:
            query = query.filter(Empresa.activa == True)
        return query.offset(skip).limit(limit).all()
    
    def update(self, empresa_id: int, **kwargs) -> Optional[Empresa]:
        """Actualiza una empresa"""
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return None
        
        for key, value in kwargs.items():
            if hasattr(empresa, key):
                setattr(empresa, key, value)
        
        self.db.commit()
        self.db.refresh(empresa)
        return empresa
    
    def delete(self, empresa_id: int) -> bool:
        """Soft delete de empresa"""
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return False
        
        empresa.activa = False
        self.db.commit()
        return True
    
    def delete_permanently(self, empresa_id: int) -> bool:
        """Eliminación permanente"""
        empresa = self.find_by_id(empresa_id)
        if not empresa:
            return False
        
        self.db.delete(empresa)
        self.db.commit()
        return True