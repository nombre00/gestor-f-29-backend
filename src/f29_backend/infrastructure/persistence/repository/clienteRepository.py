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
    
    # Crear nuevo cliente.
    def create(self, empresa_id: int, asignado_a_usuario_id: int,
               rut: str, razon_social: str, **kwargs) -> Cliente:
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
    

    # Buscar uno.
    # Busca por id.  -- Lo usa SUPER.
    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    # Busca por id  y  id de la empresa.  -- Lo usa ADMIN de la empresa.
    def find_by_id_y_empresa(self, cliente_id: int, empresa_id: int) -> Optional[Cliente]:
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).filter(Cliente.empresa_id == empresa_id).first()
    
    # Busca por id y id del usuario asignado.
    def find_by_id_y_usuario(self, cliente_id: int, usuario_id: int) -> Optional[Cliente]:
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).filter(Cliente.asignado_a_usuario_id == usuario_id).first()
    
    # Busca por rut.
    def find_by_rut(self, empresa_id: int, rut: str) -> Optional[Cliente]:
        return self.db.query(Cliente)\
            .filter(Cliente.empresa_id == empresa_id)\
            .filter(Cliente.rut == rut)\
            .first()
    
    # Listas.
    # Lista clientes asociados a una empresa.
    def find_by_empresa(self, empresa_id: int, solo_activos: bool = True, skip: int = 0, limit: int = 100) -> List[Cliente]:
        query = self.db.query(Cliente).filter(Cliente.empresa_id == empresa_id)
        if solo_activos:
            query = query.filter(Cliente.activo == True)
        return query.offset(skip).limit(limit).all()
    
    # Lista clientes asociados a un usuario.
    def find_by_usuario(self, usuario_id: int, solo_activos: bool = True) -> List[Cliente]:
        query = self.db.query(Cliente).filter(Cliente.asignado_a_usuario_id == usuario_id)
        if solo_activos:
            query = query.filter(Cliente.activo == True)
        return query.all()
    

    # Actualizar.
    # Actualiza todo un cliente.
    def update(self, cliente_id: int, **kwargs) -> Optional[Cliente]:
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return None
        
        for key, value in kwargs.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
        
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    # Reasigna un cliente a otro usuario de la misma empresa.
    def reasignar(self, cliente_id: int, nuevo_usuario_id: int) -> Optional[Cliente]:
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return None
        
        cliente.asignado_a_usuario_id = nuevo_usuario_id
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    # Desactiva un cliente activado.
    def deactivate(self, cliente_id: int) -> bool:
        cliente = self.find_by_id(cliente_id)
        if not cliente  or  not cliente.activo:
            return False
        
        cliente.activo = False
        self.db.commit()
        return True
    
    # Reactiva un cliente desactivado.
    def activate(self, cliente_id: int) -> bool:
        cliente = self.find_by_id(cliente_id)
        if not cliente  or  cliente.activo:
            return False
        
        cliente.activo = True
        self.db.commit()
        return True
    

    # Borrar.
    def delete(self, cliente_id: int) -> bool:
        cliente = self.find_by_id(cliente_id)
        if not cliente:
            return False
        self.db.delete(cliente)
        self.db.commit()
        return True
    

    # Funciones auxiliares.
    # Cuenta clientes asociados a una empresa.
    def count_by_empresa(self, empresa_id: int) -> int:
        return self.db.query(Cliente)\
            .filter(Cliente.empresa_id == empresa_id)\
            .filter(Cliente.activo == True)\
            .count()
    
    # Revisa si el mail está en uso.
    def revisar_mail(self, cliente_id: int, email: str) -> bool:
        cliente = self.find_by_id(cliente_id)  # Buscamos al cliente.
        if cliente.contacto_email:  # Filtramos por email y excluimos el cliente actual de la búsqueda.
            conflicto = self.db.query(Cliente).filter(Cliente.contacto_email == email, Cliente.id != cliente_id).first()
            if conflicto:
                return True
        return False