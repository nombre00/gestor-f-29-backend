
# Bibliotecas
import os
import io
import logging
from typing import Dict
from fastapi import HTTPException
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
from f29_backend.infrastructure.adapters.writers.resumenGenerador import resumenGenerador2
from f29_backend.infrastructure.adapters.writers.resumenPlantilla import generar_plantilla_resumen_f292
from f29_backend.infrastructure.adapters.writers.resumenF29Escritor import resumenF29Escritor2



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
    resumen: ResumenF29 = resumenGenerador2(rv, rc, lr, rh, remanente, importaciones)

    # Creamos una plantilla de resumenf29.
    plantillaResumen = generar_plantilla_resumen_f292()

    # LLenamos la plantilla del resumen con los datos del resumen.
    resumenF29Escritor2(resumen, plantillaResumen)

    # Guardamos en carpeta de salidas. 
    # Verificamos.
    # ── Decidir dónde y con qué nombre guardar ───────────────────────────────
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
        
    # ── Guardar ───────────────────────────────────────────────────────────────
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
    resumen: ResumenF29 = resumenGenerador2(rv, rc, lr, rh, remanente, importaciones)

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





# Funciones que gestionan inputs en bytes.
logger = logging.getLogger(__name__)
def procesar_f29_y_obtener_resumen(
    ventas_bytes: bytes,
    compras_bytes: bytes,
    remuneraciones_bytes: bytes,
    honorarios_bytes: bytes,
    remanente: int,
    importaciones: dict
) -> ResumenF29:
    try:
        # ── Parseo de ventas ───────────────────────────────────────────────────────
        df_ventas = parse_detalle_ventas(ventas_bytes)
        rv = parse_df_to_resumen_ventas(df_ventas)

        # ── Parseo de compras ──────────────────────────────────────────────────────
        df_compras = parse_detalle_compras(compras_bytes)  # ← corregido
        rc = parse_df_to_resumen_compras(df_compras)

        # ── Parseo de remuneraciones ───────────────────────────────────────────────
        lr = parse_libro_remuneraciones(remuneraciones_bytes)

        # ── Parseo de honorarios ───────────────────────────────────────────────────
        rh = parse_registro_honorarios(honorarios_bytes)

        # ── Generación del resumen ─────────────────────────────────────────────────
        resumen: ResumenF29 = resumenGenerador2(
            rv, rc, lr, rh, remanente, importaciones
        )

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