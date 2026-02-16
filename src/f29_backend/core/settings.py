from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr  # ← SecretStr para ocultar en logs


class Settings(BaseSettings):  # BaseSettings es la que carga las variables de entorno, así referenciamos el .env.
    # ── Claves secretas ── (usa SecretStr para que no se muestren en logs/debug)
    SECRET_KEY: SecretStr = Field(  # Oculto en los logs.
        default=...,  # ← "..." significa "obligatorio, no hay default"
        description="Clave secreta para firmar JWT. Obligatoria."
    )

    # ── Base de datos ──
    DATABASE_URL: SecretStr = Field(  # Oculto en los logs.
        default=...,
        description="URL completa de conexión a la BD (incluye user:pass)"
    )

    # ── Configuración general ──
    PROJECT_NAME: str = "F29 Manager"
    
    ENVIRONMENT: str = Field(
        default="development",
        description="Entorno: development | testing | production"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default= 60 * 12,  # 12 horas másximo.
        ge=60,         # mínimo 1 hora, para evitar valores absurdos
        description="Duración de los access tokens en minutos"
    )



 
    # model_config es para configurar como se cargan los datos del ambiente.
    model_config = SettingsConfigDict(  # SettingsConfigDict es para configurar como se cargan los datos.
        env_file=".env",                # Carga automática desde .env
        env_file_encoding="utf-8",
        case_sensitive=False,           # APP_NAME == app_name
        extra="ignore",                # Ignora vars extras en .env
        env_nested_delimiter="__",      # Opcional: para vars anidadas si después lo necesitas
    )


# Instancia global (singleton-ish)
settings = Settings()