# Accesadores de la clase Usuario.


# Biblioteca.
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
# Módulos.
from f29_backend.infrastructure.persistence.models import Usuario, RolUsuario


class UsuarioRepository:
    # Constructor, levanta la conección.
    def __init__(self, db: Session):
        self.db = db
    

    # Crear un usuario.
    def create(self,empresa_id: int,email: str,password_hash: str,nombre: str,apellido: str | None = None,rol: RolUsuario = RolUsuario.CONTADOR) -> Usuario:
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
    

    # Búsquedas unitarias.
    # Busca un usuario por su id.
    def find_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    # Busca un usuario por su id y su id de empresa (para consultas hechas por un admin).
    def find_by_id_and_empresa(self, usuario_id: int, empresa_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario)\
            .filter(Usuario.id == usuario_id)\
            .filter(Usuario.empresa_id == empresa_id)\
            .first()
    
    # Busca un usuario activo.
    def find_by_id_and_active(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.query(Usuario)\
            .filter(Usuario.id == usuario_id)\
            .filter(Usuario.activo == True)\
            .first()
    
    # Busca usuario por email y, opcional por empresa.
    def find_by_email(self, email: str, empresa_id: int | None = None) -> Optional[Usuario]:
        query = self.db.query(Usuario).filter(Usuario.email == email)
        if empresa_id is not None:
            query = query.filter(Usuario.empresa_id == empresa_id)
        return query.first()
    

    # Búsquedas que retornan listas.
    # Lista usuarios de una empresa.
    def find_by_empresa(self, empresa_id: int, solo_activos: bool = True) -> List[Usuario]:
        query = self.db.query(Usuario).filter(Usuario.empresa_id == empresa_id)
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.order_by(Usuario.nombre).all()
    
    # Lista usuarios de una empresa que tienen un rol en particular, opcional solo activos.
    def find_by_rol(self, empresa_id: int, rol: RolUsuario, solo_activos: bool = True) -> List[Usuario]:
        query = self.db.query(Usuario)\
            .filter(Usuario.empresa_id == empresa_id)\
            .filter(Usuario.rol == rol)
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.all()
    

    # Actualizaciones.
    # Actualiza un usuario.
    def update(self, usuarioActualizado: Usuario) -> Optional[Usuario]:
        self.db.commit()
        self.db.refresh(usuarioActualizado)
        return usuarioActualizado
    
    # Actualiza la clave de un usuario.
    def update_password(self, usuario_id: int, new_password_hash: str) -> bool:
        usuario = self.find_by_id(usuario_id)
        if not usuario:
            return False
        
        usuario.password_hash = new_password_hash
        usuario.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    # Actualiza la fecha de último acceso.
    def update_last_access(self, usuario_id: int) -> bool:
        usuario = self.find_by_id(usuario_id)
        if not usuario:
            return False
        
        usuario.ultimo_acceso = datetime.utcnow()
        self.db.commit()
        return True
    

    # Activar/desactivar usuario.
    # Desactiva un usuario.
    def deactivate(self, usuario_id: int) -> bool:
        usuario = self.find_by_id(usuario_id)
        if not usuario or not usuario.activo:
            return False
        
        usuario.activo = False
        self.db.commit()
        return True
    
    # Reactiva un usuario.
    def reactivate(self, usuario_id: int) -> bool:
        usuario = self.find_by_id(usuario_id)
        if not usuario or usuario.activo:
            return False
        
        usuario.activo = True
        self.db.commit()
        return True
    

    # Eliminar.
    # Borra un usuario de la base de datos.
    def delete(self, usuario_id: int) -> bool:
        usuario = self.find_by_id(usuario_id)
        if not usuario:
            return False
        
        self.db.delete(usuario)
        self.db.commit()
        return True
    
    
    # Funciones auxiliares (no modifican la base de datos y retornan valores que no son usuarios ni listas de uusarios).
    # Cuenta usuarios de una empresa.
    def count_by_empresa(self, empresa_id: int, solo_activos: bool = True) -> int:
        query = self.db.query(Usuario).filter(Usuario.empresa_id == empresa_id)
        if solo_activos:
            query = query.filter(Usuario.activo == True)
        return query.count()
    
    # Revisa si un mail existe en la base de datos, 2 usuarios no pueden tener el mismo mail.
    def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        query = self.db.query(Usuario).filter(Usuario.email == email)
        if exclude_id is not None:
            query = query.filter(Usuario.id != exclude_id)
        return query.first() is not None
    

    