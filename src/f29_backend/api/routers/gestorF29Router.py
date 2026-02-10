# Rutas de la vista gestorF29.

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
import json

from f29_backend.application.services.resumenF29Service import procesar_f29_y_obtener_resumen, generar_excel_en_memoria
from f29_backend.domain.entities.resumenF29 import ResumenF29


router = APIRouter(prefix="/api/f29", tags=["f29"])


@router.post("/procesar")
async def procesar_resumen(
    remanente_anterior: int = Form(0),
    importaciones: str = Form(None),
    archivo_ventas: UploadFile = File(...),
    archivo_compras: UploadFile = File(...),
    archivo_remuneraciones: UploadFile = File(...),
    archivo_honorarios: UploadFile = File(...),
):
    try:
        importaciones_dict = json.loads(importaciones) if importaciones else {}

        resumen: ResumenF29 = procesar_f29_y_obtener_resumen(
            ventas_bytes=await archivo_ventas.read(),
            compras_bytes=await archivo_compras.read(),
            remuneraciones_bytes=await archivo_remuneraciones.read(),
            honorarios_bytes=await archivo_honorarios.read(),
            remanente=remanente_anterior,
            importaciones=importaciones_dict,
        )

        return {"resumen": resumen.to_dict()}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/generar-excel")
async def generar_excel(
    remanente_anterior: int = Form(0),
    importaciones: str = Form(None),
    archivo_ventas: UploadFile = File(...),
    archivo_compras: UploadFile = File(...),
    archivo_remuneraciones: UploadFile = File(...),
    archivo_honorarios: UploadFile = File(...),
):
    try:
        importaciones_dict = json.loads(importaciones) if importaciones else {}

        resumen: ResumenF29 = procesar_f29_y_obtener_resumen(
            ventas_bytes=await archivo_ventas.read(),
            compras_bytes=await archivo_compras.read(),
            remuneraciones_bytes=await archivo_remuneraciones.read(),
            honorarios_bytes=await archivo_honorarios.read(),
            remanente=remanente_anterior,
            importaciones=importaciones_dict,
        )

        excel_bytes = generar_excel_en_memoria(resumen)

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resumen_f29.xlsx"}
        )

    except ValueError as ve:
        raise HTTPException(400, detail=str(ve))
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")