# Acá tenemos funciones de seguridad.


# Bibliotecas.
from datetime import datetime, timedelta, timezone
from typing import Any, Union, List
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated, Any, Union
from fastapi import Depends, HTTPException, status
# Módulos.
from f29_backend.core.database import get_db
from f29_backend.core.settings import settings
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario


# Contexto de hashing de contraseñas (bcrypt).
# Elimina un bug al encriptar con la ultima version de bcrypt.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False   # evita que bcrypt lance error en passwords >72
)

# Configuración para JWT
ALGORITHM = "HS256"   # Algoritmo de hasheo más usado.
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Esquema OAuth2 para FastAPI (indica dónde obtener el token)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",  # debe coincidir exactamente con tu ruta de login
    scheme_name="JWT",
    description="JWT Authorization header usando el esquema Bearer.",
)


# Para hashear la clave.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Compara la clave con el hash de la clave.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Crea un token de acceso.
def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value() , algorithm=ALGORITHM)
    return encoded_jwt


# Valida el token.
async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db),) -> Usuario:
    """
    Dependencia principal: valida el JWT y retorna el usuario actual.
    Levanta HTTPException automáticamente si falla.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,settings.SECRET_KEY.get_secret_value() ,algorithms=[ALGORITHM],)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Intentamos convertir a int (porque tu modelo usa Integer id)
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise credentials_exception

    except JWTError as exc:
        if isinstance(exc, jwt.ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o deshabilitado"
        )

    return user


# Valida el rol.
def require_role(roles_permitidos: List[RolUsuario]):
    async def role_checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: {[r.value for r in roles_permitidos]}"
            )
        return current_user
    
    return role_checker



# Ayudadores para el rol
SuperUser = Annotated[Usuario, Depends(require_role([RolUsuario.SUPER]))]  # Usuario sudo. 
AdminUser = Annotated[Usuario, Depends(require_role([RolUsuario.ADMIN]))]  # Administrador empresa.
CurrentUser = Annotated[Usuario, Depends(get_current_user)]  # Administador sus clientes.
