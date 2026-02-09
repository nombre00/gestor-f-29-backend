# Punto de entrada del código.

# Recordatorios.
# Version 1:
# Models: clases que se mapean a la base de datos.
# Repositories: accesadores.
# Services: lógica de negocios.
# Controller: endpoints.
# Domain/Entities: clases de java típicas.
# Schemas: clases de input y output de la api, valida datos, protege datos internos, genera documentación (por lo que entiendo).

# Flujo típico de trabajo: Flujo típico: Frontend envía schema → Controller valida → Service usa domain para lógica → Repository mapea a model y guarda → Retorna schema.


# Version 2:
# Api: endpoints, incluye las carpetas schemas y la carpeta routers (controllers).
# application: lógica de negocio, incluye la carpeta services (orquestación, se llama funciones de otras partes).
# Domain/entities: modelos del negocio, clases tipicas de java.
# Infrastructure: incluye adaptadores (parsers y writers) y presistencia: archivo conección y carpetas: models y repository