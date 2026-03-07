# Escritor que genera un objeto de la clase entidad ResumenF29.

# Bibliotecas.
from typing import Dict
# Entidades de entrada.
from f29_backend.domain.entities.resumenVentas import ResumenVentas
from f29_backend.domain.entities.resumenCompras import ResumenCompras
from f29_backend.domain.entities.libroRemuneraciones import LibroRemuneraciones
from f29_backend.domain.entities.honorarios import RegistroHonorariosMensual
# Entidades de salida.
from f29_backend.domain.entities.resumenF29 import ResumenF29


def resumenGenerador(rv: ResumenVentas, rc: ResumenCompras, lr: LibroRemuneraciones, rh: RegistroHonorariosMensual, remanenteMesAnterior=0) -> ResumenF29:
    # Partimos creando el RVC
    resumen = ResumenF29()
    
    # Seguimos con el detalle ventas.
    # Pasamos los atributos del objeto a la lista de diccionarios.  
    resumen.ventas_detalle.append(rv.cod110)
    resumen.ventas_detalle.append(rv.cod34)
    resumen.ventas_detalle.append(rv.cod46)
    resumen.ventas_detalle.append(rv.cod33)
    resumen.ventas_detalle.append(rv.cod39)
    resumen.ventas_detalle.append(rv.cod48)
    resumen.ventas_detalle.append(rv.cod56)
    resumen.ventas_detalle.append(rv.cod61)
    resumen.ventas_detalle.append(rv.cod45)
    resumen.ventas_detalle.append(rv.cod43)
    # Seguimos con el total ventas
    totalTDVentas = 0
    totalExentoVentas = 0
    totalNetoVentas = 0
    totalIVAVentas = 0
    montoTotalVentas = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.ventas_detalle:
        if fila['tipo'] != 61:
            totalTDVentas = totalTDVentas + fila['td']
            totalExentoVentas = totalExentoVentas + fila['exento']
            totalNetoVentas = totalNetoVentas + fila['neto']
            totalIVAVentas = totalIVAVentas + fila['iva']
            montoTotalVentas = montoTotalVentas + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDVentas = totalTDVentas + rv.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoVentas = totalNetoVentas - rv.cod61['neto']
    totalIVAVentas = totalIVAVentas - rv.cod61['iva']
    montoTotalVentas = montoTotalVentas - rv.cod61['total']
    # Asignamos los valores al diccionario
    resumen.ventas_total = {'td': totalTDVentas, 'exento': totalExentoVentas, 'neto': totalNetoVentas, 'iva': totalIVAVentas, 'total': montoTotalVentas}
    

    # Seguimos con el DetalleCompras, códigos relevantes: 34, 33, codPendiente1, codPendiente2, cod61, cod56, cod914, codPendiente3
    resumen.compras_detalle.append(rc.cod34)
    resumen.compras_detalle.append(rc.cod33)
    resumen.compras_detalle.append(rc.codSupermercado)
    resumen.compras_detalle.append(rc.codActivoFijo)
    resumen.compras_detalle.append(rc.cod61)
    resumen.compras_detalle.append(rc.cod56)
    resumen.compras_detalle.append(rc.cod914)
    resumen.compras_detalle.append(rc.codActivoFijoImportacion)
    
    # Seguimos con el total compras.
    totalTDCompras = 0
    totalExemptoCompras = 0
    totalNetoCompras = 0
    totalIVARecuperable = 0
    totalIVANoRecuperable = 0
    totalMontoTotalCompras = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.compras_detalle:
        if fila['tipo'] != 61:
            totalTDCompras = totalTDCompras + fila['td']
            totalExemptoCompras = totalExemptoCompras + fila['exento']
            totalNetoCompras = totalNetoCompras + fila['neto']
            totalIVARecuperable = totalIVARecuperable + fila['iva_rec']
            totalIVANoRecuperable = totalIVANoRecuperable + fila['iva_no_rec']
            totalMontoTotalCompras = totalMontoTotalCompras + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDCompras = totalTDCompras + rc.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoCompras = totalNetoCompras - rc.cod61['neto']
    totalIVARecuperable = totalIVARecuperable - rc.cod61['iva_rec']
    totalIVANoRecuperable = totalIVANoRecuperable - rc.cod61['iva_no_rec']
    totalMontoTotalCompras = totalMontoTotalCompras - rc.cod61['total']


    # Calculamos el iva por pagar y el remanente y se asignan.
    # Recuerda que el remanente se hereda de el mes anterior, no caduca y se anota en el codigo 504
    resumen.remanenteMesAnterior = remanenteMesAnterior
    # Recuerda que el total iva se anota en el coidgo 511.
    # Cálculo del IVA por pagar:
    remanente = 0
    IVAPorPagar = 0

    # Si positivo hay IVA por pagar, si negativo hay crédito fiscal (remanente).
    IVANeto = totalIVAVentas - totalIVARecuperable
    IVANetoAjustado = IVANeto - resumen.remanenteMesAnterior

    if IVANetoAjustado > 0:
        IVAPorPagar = IVANetoAjustado
        remanente = 0
    else:
        remanente = IVANetoAjustado * -1
        IVAPorPagar = 0
    
    resumen.IVAPP = IVAPorPagar
    resumen.remanente = remanente
    # Asignamos los valores al diccionario (Linea 36 del resumen).
    resumen.compras_total = {'td': totalTDCompras, 'exento': totalExemptoCompras, 'neto': totalNetoCompras, 'iva_rec': totalIVARecuperable, 'iva_no_rec': totalIVANoRecuperable, 'total': totalMontoTotalCompras}


    # Seguimos con el LibroRemuneraciones, codigos relevantes: 48, 151, 49, 155
    # Linea 39 del resumen.
    resumen.remuneraciones['th_remuneraciones'] = lr.totales['total_haberes_remuneraciones']  # cod 48.
    resumen.remuneraciones['impt_unico'] = lr.totales['impuesto_unico']  # Sin codigo pero en la misma fila que el cod 48, a su derecha.
    # Linea 40 del resumen.
    resumen.remuneraciones['honorarios'] = rh.totales['brutos']  # cod 151.
    resumen.remuneraciones['retencion'] = rh.totales['retenido']  # Sin código pero en la misma fila que el cod 151, asu derecha.
    # Linea 41 del resumen.
    resumen.remuneraciones['base_rem_3porc'] = lr.totales['total_haberes_remuneraciones'] # Se repite el valor de remuneraciones en el código 49.
    resumen.remuneraciones['rem_3porc'] = lr.totales['retencion_3porc']  # Sin código pero en la misma fila que el cod 49, asu derecha.

    # Seguimos con el PPM.
    # Linea 47, la base imponible es el total neto de las ventas.
    resumen.ppm['base'] = totalNetoVentas
    resumen.ppm['tasa'] = 2  # Pregunta si hay condiciones que cambien esto o si es una constante durante el año contable.
    resumen.ppm['ppm'] = (resumen.ppm['base'] * resumen.ppm['tasa']) / 100  # Es la base imponible por la tasa partido 100.


    # Terminamos en el total total.
    # Calculamos el total total.
    TotalT = 0
    TotalT = int(resumen.IVAPP) + int(resumen.remuneraciones['impt_unico']) + int(resumen.remuneraciones['retencion']) + int(resumen.remuneraciones['rem_3porc']) + int(resumen.ppm['ppm'])
    resumen.TT = TotalT

    # LLenamos el encabezado usando datos del libro de remuneraciones.
    encabezado = {
        'titulo': '',
        'periodo_mes': '',
        'periodo_anio': '',
        'nombre': '',
        'numero': '',
        'rut': '',
        'clave_sii': ''
    }
    # Capturamos mes año
    periodo = lr.encabezado['periodo']
    mes, anio = periodo.split(' ')  # Los separamos y asignamos a viarables.
    encabezado['periodo_mes'] = mes
    encabezado['periodo_anio'] = anio
    encabezado['nombre'] = lr.encabezado['razon_social']
    encabezado['numero'] = 0  # sacamos el número del cliente.
    encabezado['rut'] = lr.encabezado['rut']
    encabezado['clave_sii'] = 1  # No la usamos.
    resumen.encabezado = encabezado

    # Retornamos el RVC.
    return resumen



# Versión que incluye importaciones.
def resumenGenerador2(
        rv: ResumenVentas, 
        rc: ResumenCompras, 
        lr: LibroRemuneraciones, 
        rh: RegistroHonorariosMensual, 
        remanenteMesAnterior=0,
        importaciones: Dict = []) -> ResumenF29:
    
    # Partimos creando el RVC
    resumen = ResumenF29()
    
    # Seguimos con el detalle ventas.
    # Pasamos los atributos del objeto a la lista de diccionarios.
    resumen.ventas_detalle.append(rv.cod110)
    resumen.ventas_detalle.append(rv.cod34)
    resumen.ventas_detalle.append(rv.cod46)
    resumen.ventas_detalle.append(rv.cod33)
    resumen.ventas_detalle.append(rv.cod39)
    resumen.ventas_detalle.append(rv.cod48)
    resumen.ventas_detalle.append(rv.cod56)
    resumen.ventas_detalle.append(rv.cod61)
    resumen.ventas_detalle.append(rv.cod45)
    resumen.ventas_detalle.append(rv.cod43)
    # Seguimos con el total ventas
    totalTDVentas = 0
    totalExentoVentas = 0
    totalNetoVentas = 0
    totalIVAVentas = 0
    montoTotalVentas = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.ventas_detalle:
        if fila['tipo'] != 61:
            totalTDVentas = totalTDVentas + fila['td']
            totalExentoVentas = totalExentoVentas + fila['exento']
            totalNetoVentas = totalNetoVentas + fila['neto']
            totalIVAVentas = totalIVAVentas + fila['iva']
            montoTotalVentas = montoTotalVentas + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDVentas = totalTDVentas + rv.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoVentas = totalNetoVentas - rv.cod61['neto']
    totalIVAVentas = totalIVAVentas - rv.cod61['iva']
    montoTotalVentas = montoTotalVentas - rv.cod61['total']
    # Asignamos los valores al diccionario. 
    resumen.ventas_total = {'td': totalTDVentas, 'exento': totalExentoVentas, 'neto': totalNetoVentas, 'iva': totalIVAVentas, 'total': montoTotalVentas}
    

    # Seguimos con el DetalleCompras, códigos relevantes: 34, 33, codSupermercado, codActivoFijo, cod61, cod56, cod914, codPendiente3
    resumen.compras_detalle.append(rc.cod34)
    resumen.compras_detalle.append(rc.cod33)
    resumen.compras_detalle.append(rc.codSupermercado)
    resumen.compras_detalle.append(rc.codActivoFijo)
    resumen.compras_detalle.append(rc.cod61)
    resumen.compras_detalle.append(rc.cod56)
    # Las importaciones pueden estar incompletas en el resumen de compras, se ingresan manualmente los valores que podrían faltar. 
    rc.cod914['td'] += importaciones['cant_giro']  # Ingresamos valor al diccionario.
    rc.cod914['neto'] += importaciones['monto_giro']  # Ingresamos valor al diccionario. 
    rc.cod914['iva_rec'] += importaciones['iva_giro']  # Ingresamos valor al diccionario. 
    resumen.compras_detalle.append(rc.cod914)  # Agregamos el diccionario.
    rc.codActivoFijoImportacion['td'] += importaciones['cant_activo']  # Ingresamos valor al diccionario.
    rc.codActivoFijoImportacion['neto'] += importaciones['monto_activo']  # Ingresamos valor al diccionario.
    rc.codActivoFijoImportacion['iva_rec'] += importaciones['iva_activo']  # Ingresamos valor al diccionario.
    resumen.compras_detalle.append(rc.codActivoFijoImportacion)  # Agregamos el diccionario.
    
    # Seguimos con el total compras.
    totalTDCompras = 0
    totalExemptoCompras = 0
    totalNetoCompras = 0
    totalIVARecuperable = 0
    totalIVANoRecuperable = 0
    totalMontoTotalCompras = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.compras_detalle:
        if fila['tipo'] != 61:
            totalTDCompras = totalTDCompras + fila['td']
            totalExemptoCompras = totalExemptoCompras + fila['exento']
            totalNetoCompras = totalNetoCompras + fila['neto']
            totalIVARecuperable = totalIVARecuperable + fila['iva_rec']
            totalIVANoRecuperable = totalIVANoRecuperable + fila['iva_no_rec']
            totalMontoTotalCompras = totalMontoTotalCompras + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDCompras = totalTDCompras + rc.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoCompras = totalNetoCompras - rc.cod61['neto']
    totalIVARecuperable = totalIVARecuperable - rc.cod61['iva_rec']
    totalIVANoRecuperable = totalIVANoRecuperable - rc.cod61['iva_no_rec']
    totalMontoTotalCompras = totalMontoTotalCompras - rc.cod61['total']


    # Calculamos el iva por pagar y el remanente y se asignan.
    # Recuerda que el remanente se hereda de el mes anterior, no caduca y se anota en el codigo 504
    resumen.remanenteMesAnterior = remanenteMesAnterior
    # Recuerda que el total iva se anota en el coidgo 511.
    # Cálculo del IVA por pagar:
    remanente = 0
    IVAPorPagar = 0

    # Si positivo hay IVA por pagar, si negativo hay crédito fiscal (remanente).
    IVANeto = totalIVAVentas - totalIVARecuperable
    IVANetoAjustado = IVANeto - resumen.remanenteMesAnterior

    if IVANetoAjustado > 0:
        IVAPorPagar = IVANetoAjustado
        remanente = 0
    else:
        remanente = IVANetoAjustado * -1
        IVAPorPagar = 0
    
    resumen.IVAPP = IVAPorPagar
    resumen.remanente = remanente
    # Asignamos los valores al diccionario (Linea 40 del resumen).
    resumen.compras_total = {'td': totalTDCompras, 'exento': totalExemptoCompras, 'neto': totalNetoCompras, 'iva_rec': totalIVARecuperable, 'iva_no_rec': totalIVANoRecuperable, 'total': totalMontoTotalCompras}


    # Seguimos con el LibroRemuneraciones, codigos relevantes: 48, 151, 49, 155
    # Linea 39 del resumen.
    resumen.remuneraciones['th_remuneraciones'] = lr.totales['total_haberes_remuneraciones']  # cod 48.
    resumen.remuneraciones['impt_unico'] = lr.totales['impuesto_unico']  # Sin codigo pero en la misma fila que el cod 48, a su derecha.
    # Linea 40 del resumen.
    resumen.honorarios['honorarios'] = rh.totales['brutos']  # cod 151.
    resumen.honorarios['retencion'] = rh.totales['retenido']  # Sin código pero en la misma fila que el cod 151, a su derecha.
    # Linea 41 del resumen.
    resumen.remuneraciones['base_rem_3porc'] = lr.totales['total_haberes_remuneraciones'] # Se repite el valor de remuneraciones en el código 49.
    resumen.remuneraciones['rem_3porc'] = lr.totales['retencion_3porc']  # Sin código pero en la misma fila que el cod 49, a su derecha.
    # Linea 42 del resumen. Es un caso puntual y poco probable, lo vamos a dejar en 0 por ahora y puede ser editado más adelante por el usuario.
    resumen.honorarios['cod155'] = 0

    # Seguimos con el PPM.
    # Linea 43, la base imponible es el total neto de las ventas.
    resumen.ppm['base'] = totalNetoVentas
    resumen.ppm['tasa'] = 2  # Pregunta si hay condiciones que cambien esto o si es una constante durante el año contable.
    resumen.ppm['ppm'] = (resumen.ppm['base'] * resumen.ppm['tasa']) / 100  # Es la base imponible por la tasa partido 100. 
    # Linea 44, PPM 2° categoría.
    resumen.ppm['PPM2_base'] = 0
    resumen.ppm['PPM2_tasa'] = 0
    resumen.ppm['PPM2_valor'] = 0
    # Linea 45, PPM transportista.
    resumen.ppm['PPM_transportista_base'] = 0
    resumen.ppm['PPM_transportista_tasa'] = 0
    resumen.ppm['PPM_transportista_valor'] = 0


    # Terminamos en el total total.
    # Calculamos el total total.
    # Pregunta si se resta el remanente del total total o quedan como montos aparte.
    TotalT = 0
    TotalT = int(resumen.IVAPP) + int(resumen.remuneraciones['impt_unico']) + int(resumen.honorarios['retencion']) + int(resumen.remuneraciones['rem_3porc']) + resumen.honorarios['cod155'] + int(resumen.ppm['ppm'] + resumen.ppm['PPM2_valor'] + resumen.ppm['PPM_transportista_valor'])
    resumen.TT = TotalT

    # LLenamos el encabezado usando datos del libro de remuneraciones. 
    encabezado = {
        'titulo': '',
        'periodo_mes': '',
        'periodo_anio': '',
        'nombre': '',
        'numero': '',
        'rut': '',
        'clave_sii': ''
    }
    # Capturamos mes año
    periodo = lr.encabezado['periodo']
    mes, anio = periodo.split(' ')  # Los separamos y asignamos a viarables.
    encabezado['periodo_mes'] = mes
    encabezado['periodo_anio'] = anio
    encabezado['nombre'] = lr.encabezado['razon_social']
    encabezado['numero'] = 0  # sacamos el número del cliente.
    encabezado['rut'] = lr.encabezado['rut']
    encabezado['clave_sii'] = 1  # No la usamos.
    resumen.encabezado = encabezado

    # Retornamos el RVC.
    return resumen






### Verión que no incluye el ingreso manual de importaciones: 
def resumenGenerador3(
    rv: ResumenVentas, 
    rc: ResumenCompras, 
    lr: LibroRemuneraciones, 
    rh: RegistroHonorariosMensual, 
    remanenteMesAnterior=0
    ) -> ResumenF29:
    
    # Partimos creando el RVC
    resumen = ResumenF29()
    
    # Seguimos con el detalle ventas.
    # Pasamos los atributos del objeto a la lista de diccionarios.
    resumen.ventas_detalle.append(rv.cod110)
    resumen.ventas_detalle.append(rv.cod34)
    resumen.ventas_detalle.append(rv.cod46)
    resumen.ventas_detalle.append(rv.cod33)
    resumen.ventas_detalle.append(rv.cod39)
    resumen.ventas_detalle.append(rv.cod48)
    resumen.ventas_detalle.append(rv.cod56)
    resumen.ventas_detalle.append(rv.cod61)
    resumen.ventas_detalle.append(rv.cod45)
    resumen.ventas_detalle.append(rv.cod43)
    # Seguimos con el total ventas
    totalTDVentas = 0
    totalExentoVentas = 0
    totalNetoVentas = 0
    totalIVAVentas = 0
    montoTotalVentas = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.ventas_detalle:
        if fila['tipo'] != 61:
            totalTDVentas = totalTDVentas + fila['td']
            totalExentoVentas = totalExentoVentas + fila['exento']
            totalNetoVentas = totalNetoVentas + fila['neto']
            totalIVAVentas = totalIVAVentas + fila['iva']
            montoTotalVentas = montoTotalVentas + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDVentas = totalTDVentas + rv.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoVentas = totalNetoVentas - rv.cod61['neto']
    totalIVAVentas = totalIVAVentas - rv.cod61['iva']
    montoTotalVentas = montoTotalVentas - rv.cod61['total']
    # Asignamos los valores al diccionario. 
    resumen.ventas_total = {'td': totalTDVentas, 'exento': totalExentoVentas, 'neto': totalNetoVentas, 'iva': totalIVAVentas, 'total': montoTotalVentas}
    

    # Seguimos con el DetalleCompras, códigos relevantes: 34, 33, codSupermercado, codActivoFijo, cod61, cod56, cod914, codPendiente3
    resumen.compras_detalle.append(rc.cod34)
    resumen.compras_detalle.append(rc.cod33)
    resumen.compras_detalle.append(rc.codSupermercado)
    resumen.compras_detalle.append(rc.codActivoFijo)
    resumen.compras_detalle.append(rc.cod61)
    resumen.compras_detalle.append(rc.cod56)
    
    # Seguimos con el total compras.
    totalTDCompras = 0
    totalExemptoCompras = 0
    totalNetoCompras = 0
    totalIVARecuperable = 0
    totalIVANoRecuperable = 0
    totalMontoTotalCompras = 0
    # Sumamos los datos menos los del codigo 61.
    for fila in resumen.compras_detalle:
        if fila['tipo'] != 61:
            totalTDCompras = totalTDCompras + fila['td']
            totalExemptoCompras = totalExemptoCompras + fila['exento']
            totalNetoCompras = totalNetoCompras + fila['neto']
            totalIVARecuperable = totalIVARecuperable + fila['iva_rec']
            totalIVANoRecuperable = totalIVANoRecuperable + fila['iva_no_rec']
            totalMontoTotalCompras = totalMontoTotalCompras + fila['total']
    # Sumamos y restamos los datos del codigo 61. (pregunta que pasa con el monto exento en este cálculo).
    totalTDCompras = totalTDCompras + rc.cod61['td']
    # Pregunta que pasa con exento compras
    totalNetoCompras = totalNetoCompras - rc.cod61['neto']
    totalIVARecuperable = totalIVARecuperable - rc.cod61['iva_rec']
    totalIVANoRecuperable = totalIVANoRecuperable - rc.cod61['iva_no_rec']
    totalMontoTotalCompras = totalMontoTotalCompras - rc.cod61['total']


    # Calculamos el iva por pagar y el remanente y se asignan.
    # Recuerda que el remanente se hereda de el mes anterior, no caduca y se anota en el codigo 504
    resumen.remanenteMesAnterior = remanenteMesAnterior
    # Recuerda que el total iva se anota en el coidgo 511.
    # Cálculo del IVA por pagar:
    remanente = 0
    IVAPorPagar = 0

    # Si positivo hay IVA por pagar, si negativo hay crédito fiscal (remanente).
    IVANeto = totalIVAVentas - totalIVARecuperable
    IVANetoAjustado = IVANeto - resumen.remanenteMesAnterior

    if IVANetoAjustado > 0:
        IVAPorPagar = IVANetoAjustado
        remanente = 0
    else:
        remanente = IVANetoAjustado * -1
        IVAPorPagar = 0
    
    resumen.IVAPP = IVAPorPagar
    resumen.remanente = remanente
    # Asignamos los valores al diccionario (Linea 40 del resumen).
    resumen.compras_total = {'td': totalTDCompras, 'exento': totalExemptoCompras, 'neto': totalNetoCompras, 'iva_rec': totalIVARecuperable, 'iva_no_rec': totalIVANoRecuperable, 'total': totalMontoTotalCompras}


    # Seguimos con el LibroRemuneraciones, codigos relevantes: 48, 151, 49, 155
    # Linea 39 del resumen.
    resumen.remuneraciones['th_remuneraciones'] = lr.totales['total_haberes_remuneraciones']  # cod 48.
    resumen.remuneraciones['impt_unico'] = lr.totales['impuesto_unico']  # Sin codigo pero en la misma fila que el cod 48, a su derecha.
    # Linea 40 del resumen.
    resumen.honorarios['honorarios'] = rh.totales['brutos']  # cod 151.
    resumen.honorarios['retencion'] = rh.totales['retenido']  # Sin código pero en la misma fila que el cod 151, a su derecha.
    # Linea 41 del resumen.
    resumen.remuneraciones['base_rem_3porc'] = lr.totales['total_haberes_remuneraciones'] # Se repite el valor de remuneraciones en el código 49.
    resumen.remuneraciones['rem_3porc'] = lr.totales['retencion_3porc']  # Sin código pero en la misma fila que el cod 49, a su derecha.
    # Linea 42 del resumen. Es un caso puntual y poco probable, lo vamos a dejar en 0 por ahora y puede ser editado más adelante por el usuario.
    resumen.honorarios['cod155'] = 0

    # Seguimos con el PPM.
    # Linea 43, la base imponible es el total neto de las ventas.
    resumen.ppm['base'] = totalNetoVentas
    resumen.ppm['tasa'] = 2  # Pregunta si hay condiciones que cambien esto o si es una constante durante el año contable.
    resumen.ppm['ppm'] = round((resumen.ppm['base'] * resumen.ppm['tasa']) / 100)  # Es la base imponible por la tasa partido 100. 
    # Linea 44, PPM 2° categoría.
    resumen.ppm['PPM2_base'] = 0
    resumen.ppm['PPM2_tasa'] = 0
    resumen.ppm['PPM2_valor'] = 0
    # Linea 45, PPM transportista.
    resumen.ppm['PPM_transportista_base'] = 0
    resumen.ppm['PPM_transportista_tasa'] = 0
    resumen.ppm['PPM_transportista_valor'] = 0


    # Terminamos en el total total.
    # Calculamos el total total.
    # Pregunta si se resta el remanente del total total o quedan como montos aparte.
    TotalT = 0
    TotalT = int(resumen.IVAPP) + int(resumen.remuneraciones['impt_unico']) + int(resumen.honorarios['retencion']) + int(resumen.remuneraciones['rem_3porc']) + resumen.honorarios['cod155'] + int(resumen.ppm['ppm'] + resumen.ppm['PPM2_valor'] + resumen.ppm['PPM_transportista_valor'])
    resumen.TT = TotalT

    # LLenamos el encabezado usando datos del libro de remuneraciones. 
    encabezado = {
        'titulo': '',
        'periodo_mes': '',
        'periodo_anio': '',
        'nombre': '',
        'numero': '',
        'rut': '',
        'clave_sii': ''
    }
    # Capturamos mes año
    periodo = lr.encabezado['periodo']
    mes, anio = periodo.split(' ')  # Los separamos y asignamos a viarables.
    encabezado['periodo_mes'] = mes
    encabezado['periodo_anio'] = anio
    encabezado['nombre'] = lr.encabezado['razon_social']
    encabezado['numero'] = 0  # sacamos el número del cliente.
    encabezado['rut'] = lr.encabezado['rut']
    encabezado['clave_sii'] = 1  # No la usamos.
    resumen.encabezado = encabezado

    # Retornamos el RVC. 
    return resumen