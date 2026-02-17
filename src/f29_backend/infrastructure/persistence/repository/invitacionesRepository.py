# Accesadores de la clase Invitacion.

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
# Módulos.
from f29_backend.infrastructure.persistence.models.Invitacion import Invitacion
from f29_backend.infrastructure.persistence.models.usuario import RolUsuario


class InvitacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        empresa_id: int,
        email: str,
        invitado_por_usuario_id: int,
        nombre: str = None,
        apellido: str = None,
        rol: RolUsuario = RolUsuario.CONTADOR,
    ) -> Invitacion:
        """Crea una nueva invitación"""
        invitacion = Invitacion(
            empresa_id=empresa_id,
            email=email,
            nombre=nombre,
            apellido=apellido,
            rol=rol.value if hasattr(rol, "value") else rol,
            token=Invitacion.generar_token(),
            expires_at=Invitacion.calcular_expiracion(),
            invitado_por_usuario_id=invitado_por_usuario_id,
            usado=False,
        )
        self.db.add(invitacion)
        self.db.commit()
        self.db.refresh(invitacion)
        return invitacion

    def find_by_id(self, invitacion_id: int) -> Optional[Invitacion]:
        """Busca invitación por ID"""
        return self.db.query(Invitacion).filter(Invitacion.id == invitacion_id).first()

    def find_by_token(self, token: str) -> Optional[Invitacion]:
        """Busca invitación por token (para validar registro)"""
        return self.db.query(Invitacion).filter(Invitacion.token == token).first()

    def find_by_email(self, email: str) -> Optional[Invitacion]:
        """Busca la invitación más reciente para un email"""
        return (
            self.db.query(Invitacion)
            .filter(Invitacion.email == email)
            .order_by(Invitacion.created_at.desc())
            .first()
        )

    def find_pendiente_por_email(self, email: str) -> Optional[Invitacion]:
        """Busca si existe una invitación activa (no usada y no expirada) para un email"""
        return (
            self.db.query(Invitacion)
            .filter(
                Invitacion.email == email,
                Invitacion.usado == False,
                Invitacion.expires_at > datetime.utcnow(),
            )
            .first()
        )

    def find_by_empresa(
        self,
        empresa_id: int,
        solo_pendientes: bool = True,
    ) -> List[Invitacion]:
        """Lista invitaciones de una empresa"""
        query = self.db.query(Invitacion).filter(Invitacion.empresa_id == empresa_id)
        if solo_pendientes:
            query = query.filter(Invitacion.usado == False)
        return query.order_by(Invitacion.created_at.desc()).all()

    def marcar_como_usada(self, invitacion_id: int) -> Optional[Invitacion]:
        """Marca una invitación como utilizada"""
        invitacion = self.find_by_id(invitacion_id)
        if not invitacion:
            return None
        invitacion.usado = True
        self.db.commit()
        self.db.refresh(invitacion)
        return invitacion

    def extender_expiracion(self, invitacion_id: int, dias: int = 7) -> Optional[Invitacion]:
        """Extiende la fecha de expiración (para el reenvío)"""
        invitacion = self.find_by_id(invitacion_id)
        if not invitacion:
            return None
        invitacion.expires_at = Invitacion.calcular_expiracion(dias)
        self.db.commit()
        self.db.refresh(invitacion)
        return invitacion

    def delete(self, invitacion_id: int) -> bool:
        """Elimina una invitación (cancelar)"""
        invitacion = self.find_by_id(invitacion_id)
        if not invitacion:
            return False
        self.db.delete(invitacion)
        self.db.commit()
        return True

    def count_pendientes_by_empresa(self, empresa_id: int) -> int:
        """Cuenta invitaciones pendientes de una empresa"""
        return (
            self.db.query(Invitacion)
            .filter(
                Invitacion.empresa_id == empresa_id,
                Invitacion.usado == False,
                Invitacion.expires_at > datetime.utcnow(),
            )
            .count()
        )