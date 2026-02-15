# Esquema del token de autentificación del usuario.

# Un token consiste de 3 partes:
        #  Header: algoritmo usado para encriptar.
        #  Payload: información útil, en este caso la id del usuario, fecha de creación del token, fecha de caducación del token.
        #  Firma:  firma criptográfica que asegura que no ha sido modificado.


# Bibliotecas.
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenWithUser(Token):
    user: dict  