# Accesadores de la clase Usuario.


# Biblioteca.
from sqlalchemy.orm import Session
from typing import List, Optional
# Módulos.
from f29_backend.infrastructure.persistence.models import Usuario, RolUsuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, empresa_id: int, email: str, password_hash: str,
               nombre: str, apellido: str = None,
               rol: RolUsuario = RolUsuario.CONTADOR) -> Usuario:
        """Crea un nuevo usuario"""
        usuario = Usuario(
            empresa_id=empresa_id,
            email=email,
            password_hash=password_hash,
            nombre=nombre,
            apellido=apellido,
            rol=rol,
            activo=True
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca usuario por ID"""
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    def find_by_email(self, email: str, empresa_id: int) -> Optional[Usuario]:
        """Busca usuario por email en una empresa"""
        return self.db.query(Usuario)\
            .filter(Usuario.email == email)\
            .filter(Usuario.empresa_id == empresa_id)\
            .first()
    
    def find_by_empresa(self, empresa_id: int, solo_activos: bool = True) -> List[Usuario]:
        """Lista usuarios de una empresa"""
        query = self.db.query(Usuario).filter(Usuario.empresa_id == empresa_id)
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.all()
    
    def find_by_rol(self, empresa_id: int, rol: RolUsuario) -> List[Usuario]:
        """Busca usuarios por rol en una empresa"""
        return self.db.query(Usuario)\
            .filter(Usuario.empresa_id == empresa_id)\
            .filter(Usuario.rol == rol)\
            .filter(Usuario.activo == True)\
            .all()
    
    def update(self, usuario_id: int, **kwargs) -> Optional[Usuario]:
        """Actualiza un usuario"""
        usuario = self.find_by_id(usuario_id)
        if not usuario:
            return None
        
        for key, value in kwargs.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)
        
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def delete(self, usuario_id: int) -> bool:
        """Desactiva un usuario"""
        usuario = self.find_by_id(usuario_id)
        if not usuario:
            return False
        
        usuario.activo = False
        self.db.commit()
        return True
    
    def update_ultimo_acceso(self, usuario_id: int):
        """Actualiza fecha de último acceso"""
        from datetime import datetime
        usuario = self.find_by_id(usuario_id)
        if usuario:
            usuario.ultimo_acceso = datetime.now()
            self.db.commit()