# ==============================================================================
# GESTOR F29 - Seeding inicial de base de datos
# ==============================================================================
# Este script inserta los datos mínimos para que el sistema pueda usarse
# por primera vez: la empresa cliente y un usuario admin genérico temporal.
#
# CUÁNDO ejecutarlo:
#   Solo una vez, durante la instalación inicial, DESPUÉS de que los
#   contenedores estén corriendo (docker compose up -d).
#
# CÓMO ejecutarlo (desde la raíz del proyecto, con los contenedores activos):
#   docker compose exec backend python seed.py
#
# IMPORTANTE:
#   El usuario admin genérico es temporal. Su propósito es enviar la primera
#   invitación al usuario admin real de la empresa. Una vez hecho eso,
#   este usuario debe eliminarse desde el panel de administración.
#
#   Credenciales del usuario admin genérico:
#     Email:      admin@ejemplo.cl
#     Contraseña: Admin1234!
# ==============================================================================

import sys
from sqlalchemy.orm import Session
from f29_backend.core.database import engine, Base
# Importar todos los modelos para que SQLAlchemy resuelva todas las relaciones
from f29_backend.infrastructure.persistence.models.Invitacion import Invitacion  # noqa: F401
from f29_backend.infrastructure.persistence.models.cliente import Cliente  # noqa: F401
from f29_backend.infrastructure.persistence.models.empresa import Empresa
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario


def seed():
    """
    Inserta la empresa y el usuario admin inicial si no existen todavía.
    Es seguro ejecutarlo más de una vez: verifica antes de insertar.
    """

    print("=" * 60)
    print("  GESTOR F29 - Seeding inicial")
    print("=" * 60)

    print("\n[1/3] Verificando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("      Tablas OK.")

    with Session(engine) as session:

        # ------------------------------------------------------------------
        # PASO 2: Insertar empresa
        # ------------------------------------------------------------------
        print("\n[2/3] Verificando empresa...")

        empresa_existente = session.query(Empresa).filter_by(
            rut="76.074.027-6"
        ).first()

        if empresa_existente:
            print("      Empresa ya existe, omitiendo inserción.")
            empresa = empresa_existente
        else:
            empresa = Empresa(
                rut="76.074.027-6",
                razon_social="Viña Center LTDA",
                nombre_comercial="Viña Center LTDA",
                email="contabilidadjpg56@gmail.com",
                telefono="+56998409235",
                activa=True,
            )
            session.add(empresa)
            session.flush()
            print(f"      Empresa insertada con ID: {empresa.id}")

        # ------------------------------------------------------------------
        # PASO 3: Insertar usuario admin genérico temporal
        # ------------------------------------------------------------------
        print("\n[3/3] Verificando usuario admin genérico...")

        usuario_existente = session.query(Usuario).filter_by(
            email="admin@ejemplo.cl"
        ).first()

        if usuario_existente:
            print("      Usuario admin ya existe, omitiendo inserción.")
        else:
            # Hash bcrypt de la contraseña inicial.
            # Contraseña: Admin1234!
            PASSWORD_HASH = (
                "$2b$12$qGe3DSNwvrAhv1p5OwwPP.2B6Qhb3YmEnVMv2rpCxYaQ0luVRHyb2"
            )

            usuario = Usuario(
                empresa_id=empresa.id,
                email="admin@ejemplo.cl",
                password_hash=PASSWORD_HASH,
                nombre="admin",
                apellido="admin",
                rol=RolUsuario.ADMIN,
                activo=True,
            )
            session.add(usuario)
            print(f"      Usuario admin insertado para empresa ID: {empresa.id}")

        session.commit()

    print("\n" + "=" * 60)
    print("  Seeding completado exitosamente.")
    print("=" * 60)
    print("\n  PRÓXIMOS PASOS:")
    print("  1. Inicia sesión con el usuario admin genérico:")
    print("     Email:      admin@ejemplo.cl")
    print("     Contraseña: Admin1234!")
    print("  2. Invita al usuario admin real de la empresa por email.")
    print("  3. Verifica que el admin real pueda iniciar sesión.")
    print("  4. Elimina el usuario admin@ejemplo.cl desde el panel.")
    print()


if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"\n[ERROR] El seeding falló: {e}")
        print("Verifica que los contenedores estén corriendo con: docker compose ps")
        sys.exit(1)