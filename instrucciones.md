# GESTOR F29 — Instrucciones de instalación y uso
**Viña Center LTDA — Marzo 2026**

---

## 1. Requisitos previos

Antes de comenzar, verificar que el PC servidor tenga instalado:

- **Docker Desktop** (descarga gratuita en https://www.docker.com/products/docker-desktop)
- **Windows 10 u 11** (64 bits)
- **Mínimo 4 GB de RAM** disponibles
- **Puerto 8000 libre** (no debe estar en uso por otro programa)
- **Conexión a Internet** solo durante la instalación inicial

> Una vez instalado, el sistema funciona completamente en red local sin necesidad de Internet.

---

## 2. Instalación inicial

Realizar estos pasos **solo una vez**, al instalar el sistema por primera vez.

### 2.1 Preparar el archivo de configuración

1. Ubicar el archivo `.env.example` en la carpeta del sistema.
2. Hacer una copia y renombrarla exactamente `.env` (sin extensión adicional).
3. Abrir `.env` con el Bloc de notas y reemplazar todos los valores que digan `cambia_esto_por...` con los valores reales.

> **Importante:** El archivo `.env` contiene contraseñas. No compartirlo ni enviarlo por correo.

### 2.2 Levantar el sistema

1. Asegurarse de que Docker Desktop esté abierto y corriendo.
2. Hacer doble clic en `iniciar.bat`.
3. La **primera vez** tardará varios minutos mientras se descargan las imágenes. Las veces siguientes será casi inmediato.
4. Cuando aparezca el mensaje `Sistema iniciado correctamente`, el sistema está listo.

### 2.3 Cargar datos iniciales (solo la primera vez)

Una vez que el sistema esté corriendo, abrir una terminal en la carpeta del sistema y ejecutar:

```
docker compose exec backend python seed.py
```

Este comando crea la empresa y el usuario administrador inicial en la base de datos.

**Credenciales del administrador inicial:**

| Campo      | Valor             |
|------------|-------------------|
| Email      | admin@ejemplo.cl  |
| Contraseña | Admin1234!        |

> **Importante:** Este usuario es temporal. Una vez dentro del sistema, usarlo para invitar al administrador real por correo y luego eliminarlo.

---

## 3. Acceso al sistema

### Desde el PC servidor

Abrir el navegador e ingresar:

```
http://localhost:8000
```

### Desde otros PCs de la red

1. Conocer la IP del PC servidor en la red local.  
   Para verla: abrir una terminal en el servidor y ejecutar `ipconfig`. Buscar la línea **Dirección IPv4**.
2. En cualquier PC de la misma red, abrir el navegador e ingresar:

```
http://[IP del servidor]:8000
Ejemplo: http://192.168.1.100:8000
```

---

## 4. Operación diaria

### Iniciar el sistema
- Hacer doble clic en `iniciar.bat`.
- Docker Desktop debe estar abierto antes de ejecutarlo.

### Detener el sistema
- Hacer doble clic en `detener.bat`.
- Los datos quedan guardados. El sistema se puede volver a iniciar sin perder información.

### Reinicio del PC servidor
- El sistema **se reinicia automáticamente** al encender el PC, siempre que Docker Desktop esté configurado para iniciar con Windows (configuración por defecto).

---

## 5. Respaldo de datos (Backup)

Se recomienda realizar un respaldo **al menos una vez por semana**.

### Cómo hacer un backup

1. Asegurarse de que el sistema esté corriendo (`iniciar.bat`).
2. Hacer doble clic en `backup.bat`.
3. El archivo de respaldo se guarda automáticamente en la carpeta `backups\` con la fecha y hora en el nombre.

> **Recomendación:** Copiar los archivos de la carpeta `backups\` a un disco externo o pendrive de forma periódica. Si el PC falla, los datos podrán recuperarse desde ese respaldo.

---

## 6. Solución de problemas frecuentes

### El sistema no carga en el navegador
- Verificar que Docker Desktop esté abierto y corriendo.
- Ejecutar `iniciar.bat` y esperar hasta el mensaje de confirmación.
- Verificar que la URL sea correcta (`http://localhost:8000` o la IP del servidor).

### iniciar.bat da error: "Docker no está corriendo"
- Abrir Docker Desktop desde el menú de inicio.
- Esperar a que el ícono de la ballena deje de moverse (indica que está listo).
- Volver a ejecutar `iniciar.bat`.

### La primera vez tarda mucho
- Es normal. Docker descarga las imágenes necesarias (~500 MB la primera vez). Las veces siguientes el inicio es casi inmediato.

### Un usuario no puede acceder desde su PC
- Verificar que el PC del usuario esté en la **misma red** que el servidor.
- Verificar que esté usando la **IP del servidor**, no `localhost`.

---

## 7. Contacto y soporte

Para consultas técnicas o problemas con el sistema, contactar al desarrollador.

Al reportar un problema, incluir siempre:
- Descripción de lo que ocurrió
- Mensaje de error si aparece en pantalla
- Captura de pantalla si es posible
