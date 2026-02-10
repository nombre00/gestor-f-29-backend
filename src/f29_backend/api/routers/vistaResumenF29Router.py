# Rutas de la vista vistaResumenF29.

# Bibliotecas.
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
import json
from typing import Dict, List, Any
# módulos.
from f29_backend.domain.entities.resumenF29 import ResumenF29
from f29_backend.infrastructure.adapters.writers.resumenPlantilla import generar_plantilla_resumen_f292
from f29_backend.infrastructure.adapters.writers.resumenF29Escritor import resumenF29Escritor2


router = APIRouter(prefix="/api/f29", tags=["f29"])


@router.post("/resumen/exportar")
async def exportar_resumen(body: Dict[str, Any]):
    try:
        resumen_dict = body.get("resumen")
        if not resumen_dict:
            raise ValueError("Falta el campo 'resumen' en el body")

        # Reconstruye el objeto desde el JSON recibido
        resumen = ResumenF29.from_dict(resumen_dict)

        # Genera la plantilla y la llena (usa tus funciones existentes)
        plantilla = generar_plantilla_resumen_f292()
        resumenF29Escritor2(resumen, plantilla)

        # Guarda en memoria
        output = io.BytesIO()
        plantilla.save(output)
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resumen_f29.xlsx"}
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar Excel: {str(e)}")