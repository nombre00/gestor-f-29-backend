# Punto de entrada del código.

# Recordatorios.
# Models: clases que se mapean a la base de datos.
# Repositories: accesadores.
# Services: lógica de negocios.
# Controller: endpoints.
# Domain/Entities: clases de java típicas.
# Schemas: clases de input y output de la api, valida datos, protege datos internos, genera documentación (por lo que entiendo).

# Flujo típico de trabajo: Flujo típico: Frontend envía schema → Controller valida → Service usa domain para lógica → Repository mapea a model y guarda → Retorna schema.