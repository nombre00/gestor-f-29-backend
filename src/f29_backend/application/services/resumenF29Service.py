
# Bibliotecas 
import os
import io
import logging
from typing import Dict
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dataclasses import asdict
# Clases de los imputs.
from f29_backend.domain.entities.resumenVentas import ResumenVentas
from f29_backend.domain.entities.resumenCompras import ResumenCompras
from f29_backend.domain.entities.libroRemuneraciones import LibroRemuneraciones
from f29_backend.domain.entities.honorarios import RegistroHonorariosMensual
# Clases de los outputs. 
from f29_backend.domain.entities.resumenF29 import ResumenF29
# Parseadores.
from f29_backend.infrastructure.adapters.parsers.ventasDetalleParseador import parse_detalle_ventas, parse_df_to_resumen_ventas
from f29_backend.infrastructure.adapters.parsers.comprasDetalleParseador import parse_detalle_compras, parse_df_to_resumen_compras
from f29_backend.infrastructure.adapters.parsers.libroRemuneracionesParseador import parse_libro_remuneraciones
from f29_backend.infrastructure.adapters.parsers.registroHonorariosParseador import parse_registro_honorarios
# Escritores.
from f29_backend.infrastructure.adapters.writers.resumenGenerador import resumenGenerador3
from f29_backend.infrastructure.adapters.writers.resumenPlantilla import generar_plantilla_resumen_f292
from f29_backend.infrastructure.adapters.writers.resumenF29Escritor import resumenF29Escritor2
# Persistencia.
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import ResumenF29 as ResumenModel, EstadoF29
from f29_backend.infrastructure.persistence.models.cliente import Cliente



# Se usa en la vista gestionarF29. 
# Controlador que recibe las rutas y las importaciones como parámetro, crea un excel y lo exporta.
def controladorResumenF29_v4(
        rutaResumenVentas, 
        rutaResumenCompras, 
        ruta_libroRemuneraciones, 
        ruta_registroHonorarios, 
        remanente=0,
        ruta="",
        importaciones: Dict = []):
    # Partimos capturando los datos y guardándolos en sus clases correspondientes.
    # ResumenVentas.
    # Generamos el data frame.
    df_ventas = parse_detalle_ventas(rutaResumenVentas)
    # Generamos el ResumenVentas.
    rv: ResumenVentas = parse_df_to_resumen_ventas(df_ventas)

    # ResumenCompras.
    # Generamos el data frame (df).
    df_compras = parse_detalle_compras(rutaResumenCompras)
    # Generamos el ResumenCompras.
    rc: ResumenCompras = parse_df_to_resumen_compras(df_compras)

    # LibroRemuneraciones.
    # Generamos el LibroRemuneraciones.
    lr: LibroRemuneraciones = parse_libro_remuneraciones(ruta_libroRemuneraciones)

    # RegistroHonorarios.
    # Generamos el detalleVentas. 
    rh: RegistroHonorariosMensual = parse_registro_honorarios(ruta_registroHonorarios)


    # Generamos un resumen y lo llenamos con datos.
    resumen: ResumenF29 = resumenGenerador3(rv, rc, lr, rh, remanente, importaciones)

    # Creamos una plantilla de resumenf29.
    plantillaResumen = generar_plantilla_resumen_f292()

    # LLenamos la plantilla del resumen con los datos del resumen.
    resumenF29Escritor2(resumen, plantillaResumen)

    # Guardamos en carpeta de salidas. 
    # Decidir dónde y con qué nombre guardar.
    if ruta and ruta.strip():  # si se pasó una ruta válida y no está vacía
        ruta_salida = ruta
        # Aseguramos que tenga extensión .xlsx (por si el usuario olvidó)
        if not ruta_salida.lower().endswith(('.xlsx', '.xls')):
            ruta_salida += '.xlsx'
    else:
        # Comportamiento por defecto
        carpeta_salidas = "salidas"
        os.makedirs(carpeta_salidas, exist_ok=True)
        nombre_salida = f"resumenPrueba_F29_107.xlsx"   # ← podrías hacer este nombre más dinámico después
        ruta_salida = os.path.join(carpeta_salidas, nombre_salida)
        
    # Guardar.
    try:
        plantillaResumen.save(ruta_salida)
        print(f"Plantilla generada en: {ruta_salida}")
        return ruta_salida  # ← opcional: devolver la ruta para usarla en la vista
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        raise  # relanzamos para que la vista lo capture


# Se usa en la vista resumenF29.
# Puede que requiera corutina si demora mucho.
# Controlador que recibe las rutas y las importaciones como parámetro, crea un objeto de la clase ResumenRCV y lo retorna.
def controladorResumenF29_v5(
        rutaResumenVentas, 
        rutaResumenCompras, 
        ruta_libroRemuneraciones, 
        ruta_registroHonorarios, 
        remanente=0,
        importaciones: Dict = []) -> ResumenF29:
    
    # Partimos capturando los datos y guardándolos en sus clases correspondientes.
    # ResumenVentas.
    # Generamos el data frame.
    df_ventas = parse_detalle_ventas(rutaResumenVentas)
    # Generamos el ResumenVentas.
    rv: ResumenVentas = parse_df_to_resumen_ventas(df_ventas)

    # ResumenCompras.
    # Generamos el data frame (df).
    df_compras = parse_detalle_compras(rutaResumenCompras)
    # Generamos el ResumenCompras.
    rc: ResumenCompras = parse_df_to_resumen_compras(df_compras)

    # LibroRemuneraciones.
    # Generamos el LibroRemuneraciones.
    lr: LibroRemuneraciones = parse_libro_remuneraciones(ruta_libroRemuneraciones)

    # RegistroHonorarios.
    # Generamos el detalleVentas. 
    rh: RegistroHonorariosMensual = parse_registro_honorarios(ruta_registroHonorarios)


    # Generamos un resumen y lo llenamos con datos.
    resumen: ResumenF29 = resumenGenerador3(rv, rc, lr, rh, remanente, importaciones)

    # Retornamos el objeto creado.
    return resumen



# Se usa en la vista resumenF29. 
# Recibe un resumen y exporta un excel.
def exportarAExcel(resumen: ResumenF29, ruta: str):
    # Creamos una plantilla de resumenf29.
    plantillaResumen = generar_plantilla_resumen_f292()

    # LLenamos la plantilla del resumen con los datos del resumen.
    resumenF29Escritor2(resumen, plantillaResumen)

    # Exportamos.
    plantillaResumen.save(ruta)





# Funciones que gestionan inputs en bytes (esto es para recibir los datos del front).
# Se usan en las funciones de las páginas, el front manda los archivos como bytes.
logger = logging.getLogger(__name__)
def procesar_f29_y_obtener_resumen(
    ventas_bytes: bytes,
    compras_bytes: bytes,
    remuneraciones_bytes: bytes,
    honorarios_bytes: bytes,
    remanente: int,
    arriendos_pagados: int,
    gastos_generales_boletas: int
) -> ResumenF29:
    try:
        # Parseo de ventas
        df_ventas = parse_detalle_ventas(ventas_bytes)
        rv = parse_df_to_resumen_ventas(df_ventas)

        # Parseo de compras
        df_compras = parse_detalle_compras(compras_bytes)  # ← corregido
        rc = parse_df_to_resumen_compras(df_compras)

        # Parseo de remuneraciones
        lr = parse_libro_remuneraciones(remuneraciones_bytes)

        # Parseo de honorarios
        rh = parse_registro_honorarios(honorarios_bytes)

        # Generación del resumen
        resumen: ResumenF29 = resumenGenerador3(
            rv, rc, lr, rh, remanente
        )

        # Agregamos los datos extra.
        resumen.arriendos_pagados = arriendos_pagados
        resumen.gastos_generales_boletas = gastos_generales_boletas

        return resumen

    except Exception as e:
        logger.error(f"Error al procesar F29: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error al procesar los archivos: {str(e)}"
        )



def generar_excel_en_memoria(resumen: ResumenF29) -> bytes:
    try:
        plantilla = generar_plantilla_resumen_f292()
        resumenF29Escritor2(resumen, plantilla)

        output = io.BytesIO()
        plantilla.save(output)
        output.seek(0)
        return output.read()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar Excel en memoria: {str(e)}"
        )
    




###### Persistencia ######
# Guarda o actualiza un resumenf29.
def guardar_resumen_f29(
    db: Session,
    entity: ResumenF29,
    cliente_id: int,
    creado_por_id: int,
    periodo: str,          # 'YYYY-MM'
    force_update: bool = True
) -> ResumenModel:
    # Funciones auxiliares
    def _limpiar_dict(d):
        """Recursivamente convierte Decimals en un dict/list."""
        if isinstance(d, dict):
            return {k: _limpiar_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [_limpiar_dict(i) for i in d]
        elif isinstance(d, Decimal):
            return int(d)
        return d
    

    # 1. Validar que el cliente exista y sea accesible
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.activo == True
    ).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o inactivo")

    # 2. Buscar si ya existe un borrador para este cliente + periodo
    existente = db.query(ResumenModel).filter(
        ResumenModel.cliente_id == cliente_id,
        ResumenModel.periodo == periodo,
        ResumenModel.estado == EstadoF29.BORRADOR
    ).first()

    if existente:
        if not force_update:
            raise HTTPException(
                status_code=409,  # Conflict
                detail=f"Ya existe un borrador para este cliente y período (ID {existente.id})."
            )
        model = existente
    else:
        model = ResumenModel()

    # 3. Llenar campos
    model.cliente_id = cliente_id
    model.periodo = periodo
    model.creado_por_usuario_id = creado_por_id
    model.estado = EstadoF29.BORRADOR  # Siempre borrador al guardar automáticamente

    # Totales clave
    model.debito_fiscal = entity.ventas_total.get('iva', 0)
    model.credito_fiscal = entity.compras_total.get('iva_rec', 0)
    model.remanente_mes_anterior = entity.remanenteMesAnterior
    model.iva_a_pagar = entity.IVAPP
    model.remanente = entity.remanente
    model.total_ventas_netas = entity.ventas_total.get('neto', 0)
    model.total_compras_netas = entity.compras_total.get('neto', 0)
    model.total_iva_ventas = entity.ventas_total.get('iva', 0)
    model.total_iva_compras = entity.compras_total.get('iva_rec', 0)
    model.total_retenciones = (
        entity.remuneraciones.get('impt_unico', 0) +
        entity.honorarios.get('retencion', 0) +
        entity.remuneraciones.get('rem_3porc', 0) +
        entity.honorarios.get('cod155', 0)
    )
    model.ppm = entity.ppm.get('ppm', 0) + entity.ppm.get('PPM2_valor', 0) + entity.ppm.get('PPM_transportista_valor', 0)
    model.total_a_pagar = entity.TT

    # Guardar TODO como JSON
    # model.detalles_json = asdict(entity)
    model.detalles_json = _limpiar_dict(asdict(entity))  # cambiamos Decimal a int para serializar.

    db.add(model)
    db.commit()
    db.refresh(model)

    return model