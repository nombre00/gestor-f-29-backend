# Rutas de la vista gestorF29.


# Bibliotecas.
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Depends     # para la comunicación REST
from fastapi.responses import StreamingResponse    # para la comunicación REST
import io    # para manejar carpetas del pc creo
import json   # para manejar json
from sqlalchemy.orm import Session    # para manejar la base de datos
from typing import Optional, Dict    # tipos de datos 
import re   # validación de fechas
# Módulos. 
from f29_backend.application.services.resumenF29Service import procesar_f29_y_obtener_resumen, generar_excel_en_memoria, guardar_resumen_f29
from f29_backend.domain.entities.resumenF29 import ResumenF29
from f29_backend.core.security import CurrentUser, get_current_user
from f29_backend.core.database import get_db
from f29_backend.infrastructure.persistence.models.usuario import Usuario


router = APIRouter(prefix="/api/f29", tags=["f29"])


### Persistencia ####
# Aun no incorporamos esto al front, este endpoint solo guarda en la base de datos.
@router.post("/resumenes", status_code=201)
def crear_resumen_f29(
    cliente_id: int = Body(...),
    periodo: str = Body(..., description="Formato 'YYYY-MM'"),
    remanente_anterior: int = Body(0),
    importaciones: Optional[Dict] = Body(None),
    resumen_dict: Optional[Dict] = Body(None),
    current_user: Usuario = Depends(get_current_user),   # ← correcto
    db: Session = Depends(get_db)                         # ← faltaba
):
    try:
        # Reconstruir entidad desde dict si se envió (o desde los otros params si no)
        if resumen_dict:
            resumen = ResumenF29(**resumen_dict)
        else:
            # Si no envían resumen completo, podrían generar uno aquí (pero por ahora asumimos que viene de /procesar)
            raise HTTPException(400, "Falta el resumen completo para persistir")
        modelo = guardar_resumen_f29(
            db=db,
            entity=resumen,
            cliente_id=cliente_id,
            creado_por_id=current_user.id,
            periodo=periodo
        )
        return {
            "id": modelo.id,
            "cliente_id": modelo.cliente_id,
            "periodo": modelo.periodo,
            "estado": modelo.estado,
            "mensaje": "Resumen guardado como borrador"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar resumen: {str(e)}")


# Genera un resumen nuevo, lo guarda en la base de datos y retorna el resumen.
# Se usa en el botón donde generamos un resumen y vamos a la previsualización.
@router.post("/procesar")
async def procesar_resumen(
    cliente_id: int = Form(..., description="ID del cliente seleccionado"),
    periodo: str = Form(..., description="Período en formato 'YYYY-MM' (ej: 2025-12)"),
    remanente_anterior: int = Form(0),
    arriendos_pagados: int = Form(0),  # Nuevo dato.
    gastos_generales_boletas: int = Form(0),  # Nuevo dato.
    nro_cliente: str = Form(""),
    archivo_ventas: UploadFile = File(...),
    archivo_compras: UploadFile = File(...),
    archivo_remuneraciones: UploadFile = File(...),
    archivo_honorarios: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validar formato de periodo
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', periodo):
            raise HTTPException(status_code=400,detail="Formato de período inválido. Use 'YYYY-MM' (ej: 2025-12)")

        # Generar el resumen en memoria (asíncrono).
        resumen: ResumenF29 = procesar_f29_y_obtener_resumen(
            ventas_bytes=await archivo_ventas.read(),
            compras_bytes=await archivo_compras.read(),
            remuneraciones_bytes=await archivo_remuneraciones.read(),
            honorarios_bytes=await archivo_honorarios.read(),
            remanente=remanente_anterior,
            arriendos_pagados = arriendos_pagados,  # valores nuevos.
            gastos_generales_boletas = gastos_generales_boletas,  # valores nuevos.
        )
        # Asignamos el nro del cliente.
        resumen.encabezado['numero'] = nro_cliente

        # Persistimos
        modelo = guardar_resumen_f29(db=db,entity=resumen,cliente_id=cliente_id,creado_por_id=current_user.id,periodo=periodo)

        # Retornamos el resumen + info de persistencia
        return {
            "resumen": resumen.to_dict(),
            "id_bd": modelo.id,
            "cliente_id": modelo.cliente_id,
            "periodo": modelo.periodo,
            "estado": modelo.estado,
            "mensaje": "Resumen generado y guardado como borrador en la base de datos"
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# Genera un resumen, lo guarda en la base de datos y lo exporta en el PC del usuario.
# Se usa en el botón exportar.
@router.post("/generar-excel")
async def generar_excel(
    cliente_id: int = Form(..., description="ID del cliente seleccionado"),
    periodo: str = Form(..., description="Período en formato 'YYYY-MM' (ej: 2025-12)"),
    remanente_anterior: int = Form(0),
    arriendos_pagados: int = Form(0),  # Nuevo dato.
    gastos_generales_boletas: int = Form(0),  # Nuevo dato
    nro_cliente: str = Form(""),
    archivo_ventas: UploadFile = File(...),
    archivo_compras: UploadFile = File(...),
    archivo_remuneraciones: UploadFile = File(...),
    archivo_honorarios: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #print(f"Entró a generar-excel | cliente_id={cliente_id}, periodo={periodo}, user={current_user.email}")
    try:
        # Convertir manualmente
        cliente_id_int = int(cliente_id)
        remanente_int = int(remanente_anterior)
        #print("Parámetros convertidos OK")
    except ValueError:
        raise HTTPException(422, detail="cliente_id y remanente_anterior deben ser números enteros")
    try:
        # Validar formato de periodo
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', periodo):
            raise HTTPException(
                status_code=400,
                detail="Formato de período inválido. Use 'YYYY-MM' (ej: 2025-12)"
            )

        # Generar el resumen en memoria
        resumen: ResumenF29 = procesar_f29_y_obtener_resumen(
            ventas_bytes=await archivo_ventas.read(),
            compras_bytes=await archivo_compras.read(),
            remuneraciones_bytes=await archivo_remuneraciones.read(),
            honorarios_bytes=await archivo_honorarios.read(),
            remanente=remanente_int,
            arriendos_pagados = arriendos_pagados,  # valores nuevos.
            gastos_generales_boletas = gastos_generales_boletas,  # valores nuevos.
        )
        #print("Resumen generado OK")
        # Asignamos el nro del cliente.
        resumen.encabezado['numero'] = nro_cliente

        # Persistimos, modelo no se usa
        modelo = guardar_resumen_f29(db=db,entity=resumen,cliente_id=cliente_id_int,creado_por_id=current_user.id,periodo=periodo)
        #print(f"Guardado en BD → id={modelo.id}")

        # Generar el Excel en memoria
        excel_bytes = generar_excel_en_memoria(resumen)
        #print(f"Excel generado → tamaño {len(excel_bytes)} bytes")

        # Nombre de archivo dinámico.
        filename = f"resumen_f29_{cliente_id_int}_{periodo}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    



