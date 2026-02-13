# Accesadores de la clase Cliente.


# Bibliotecas.
from sqlalchemy.orm import Session
from typing import List, Optional
# Módulos.
from f29_backend.infrastructure.persistence.models import Cliente


class ClienteRepository:
    # Abre una conección, inicia la transacción, cada operación es una transacción.
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, empresa_id: int, asignado_a_usuario_id: int,
               rut: str, razon_social: str, **kwargs) -> Cliente:
        """Crea un nuevo cliente"""
        cliente = Cliente(
            empresa_id=empresa_id,
            asignado_a_usuario_id=asignado_a_usuario_id,
            rut=rut,
            razon_social=razon_social,
            activo=True,
            **kwargs
        )
        self.db.add(cliente)  # Agrega.
        self.db.commit()  # Guarda.
        self.db.refresh(cliente)  # Regresca.
        return cliente
    
    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Busca cliente por ID"""
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    def find_by_rut(self, empresa_id: int, rut: str) -> Optional[Cliente]:
        """Busca cliente por RUT en una empresa"""
        return self.db.query(Cliente)\
            .filter(Cliente.empresa_id == empresa_id)\
            .filter(Cliente.rut == rut)\
            .first()
    
    def find_by_empresa(self, empresa_id: int, solo_activos: bool = True,
                       skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Lista clientes de una empresa"""
        query = self.db.query(Cliente).filter(Cliente.empresa_id == empresa_id)
        if solo_activos:
            query = query.filter(Cliente.activo == True)
        return query.offset(skip).limit(limit).all()
    
    def find_by_usuario(self, usuario_id: int, solo_activos: bool = True) -> List[Cliente]:
        """Lista clientes asignados a un contador"""
        query = self.db.query(Cliente).filter(Cliente.asignado_a_usuario_id == usuario_id)
        if solo_activos:
            query = query.filter(Cliente.activo == True)
        return query.all()
    
    def update(self, cliente_id: int, **kwargs) -> Optional[Cliente]:
        """Actualiza un cliente"""
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return None
        
        for key, value in kwargs.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
        
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def reasignar(self, cliente_id: int, nuevo_usuario_id: int) -> Optional[Cliente]:
        """Reasigna cliente a otro contador"""
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return None
        
        cliente.asignado_a_usuario_id = nuevo_usuario_id
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def delete(self, cliente_id: int) -> bool:
        """Desactiva un cliente"""
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return False
        
        cliente.activo = False
        self.db.commit()
        return True
    
    def count_by_empresa(self, empresa_id: int) -> int:
        """Cuenta clientes activos de una empresa"""
        return self.db.query(Cliente)\
            .filter(Cliente.empresa_id == empresa_id)\
            .filter(Cliente.activo == True)\
            .count()