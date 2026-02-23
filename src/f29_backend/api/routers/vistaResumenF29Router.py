# Rutas de la vista vistaResumenF29.

# Bibliotecas. 
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
import json
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from fastapi import Depends
from dataclasses import asdict
from decimal import Decimal
# módulos.
from f29_backend.domain.entities.resumenF29 import ResumenF29
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import ResumenF29 as ResumenModel
from f29_backend.infrastructure.adapters.writers.resumenPlantilla import generar_plantilla_resumen_f292
from f29_backend.infrastructure.adapters.writers.resumenF29Escritor import resumenF29Escritor2
from f29_backend.core.security import CurrentUser
from f29_backend.core.database import get_db


router = APIRouter(prefix="/api/f29", tags=["f29"])


@router.post("/resumen/exportar2")
async def exportar_resumen(current_user: CurrentUser, body: Dict[str, Any]):
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






### persistencia ####
def _limpiar_dict(d):
    if isinstance(d, dict):
        return {k: _limpiar_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_limpiar_dict(i) for i in d]
    elif isinstance(d, Decimal):
        return int(d)
    return d

@router.post("/resumen/exportar")
async def exportar_resumen2(
    current_user: CurrentUser,
    body: Dict[str, Any],
    db: Session = Depends(get_db)
):
    try:
        resumen_dict = body.get("resumen")
        id_bd = body.get("id_bd")
        if not resumen_dict:
            raise ValueError("Falta el campo 'resumen' en el body")
        
        if id_bd:
            modelo = db.query(ResumenModel).filter(ResumenModel.id == id_bd).first()
            if not modelo:
                raise HTTPException(status_code=404, detail=f"Resumen con id {id_bd} no encontrado")
            
            resumen_obj = ResumenF29.from_dict(resumen_dict)
            modelo.detalles_json = _limpiar_dict(resumen_dict)
            flag_modified(modelo, "detalles_json")
            modelo.debito_fiscal = resumen_obj.ventas_total.get('iva', 0)
            modelo.credito_fiscal = resumen_obj.compras_total.get('iva_rec', 0)
            modelo.iva_a_pagar = resumen_obj.IVAPP
            modelo.remanente = resumen_obj.remanente
            modelo.total_ventas_netas = resumen_obj.ventas_total.get('neto', 0)
            modelo.total_compras_netas = resumen_obj.compras_total.get('neto', 0)
            modelo.total_iva_ventas = resumen_obj.ventas_total.get('iva', 0)
            modelo.total_iva_compras = resumen_obj.compras_total.get('iva_rec', 0)
            modelo.total_retenciones = (
                resumen_obj.remuneraciones.get('impt_unico', 0) +
                resumen_obj.honorarios.get('retencion', 0) +
                resumen_obj.remuneraciones.get('rem_3porc', 0) +
                resumen_obj.honorarios.get('cod155', 0)
            )
            modelo.ppm = resumen_obj.ppm.get('ppm', 0)
            modelo.total_a_pagar = resumen_obj.TT
            db.commit()

        resumen = ResumenF29.from_dict(resumen_dict)
        plantilla = generar_plantilla_resumen_f292()
        resumenF29Escritor2(resumen, plantilla)
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
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar Excel: {str(e)}")