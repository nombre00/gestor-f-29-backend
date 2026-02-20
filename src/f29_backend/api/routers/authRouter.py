# Endpoints del login, acá se autentica las credenciales.


# Bibliotecas.
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
# Bibliotecas.
from f29_backend.core.security import verify_password, create_access_token, get_current_user
from f29_backend.core.settings import settings
from f29_backend.core.database import get_db
from f29_backend.infrastructure.persistence.models.usuario import Usuario
from f29_backend.api.schemas.authSchema import Token, TokenWithUser
from f29_backend.api.schemas.usuarioSchema import UsuarioResponse


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/auth", tags=["auth"])


# Endpoint para hacer login.
@router.post("/login", response_model=TokenWithUser)   # Público, sin current user.
def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    # Buscamos por email.
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    # Autentificación que el usuario exista.
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Credenciales inválidas",headers={"WWW-Authenticate": "Bearer"},)

    # Autentificación que la clave sea la correcta.
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Credenciales inválidas",headers={"WWW-Authenticate": "Bearer"},)
    
    # Autentificación que el usuatio esté activo.
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Usuario inactivo o deshabilitado")

    # Token con duración configurable
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id,expires_delta=access_token_expires)

    # Actualizamos último acceso (opcional pero útil)
    from datetime import datetime, timezone
    user.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()

    # Respuesta: token + datos básicos del usuario.
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "rol": user.rol.value if hasattr(user.rol, "value") else user.rol,
            "activo": user.activo
        }
    }



# Parece estar deprecado, en un futuro se puede borrar.
# Endpoint llamado por páginas para verificar el token de ingreso de un usuario.
@router.get("/me", response_model=UsuarioResponse)  # UserOut = tu schema de salida sin password
def get_current_user_info(current_user: Usuario = Depends(get_current_user),db: Session = Depends(get_db)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "rol": current_user.rol.value if hasattr(current_user.rol, "value") else current_user.rol,
        "activo": current_user.activo,
        # Agrega empresa si la tienes en el modelo
    }