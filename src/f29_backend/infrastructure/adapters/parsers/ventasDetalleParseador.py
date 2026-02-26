
# Bibliotecas.
import pandas as pd
from typing import Dict
pd.set_option('future.no_silent_downcasting', True)
from io import StringIO
# Módulos.
from f29_backend.domain.entities.detalleVentas import DetalleVentas
from f29_backend.domain.entities.resumenVentas import ResumenVentas


# Recibe un .CSV y retorna un dataframe.
def parse_detalle_ventas(bytes_content: bytes):
    # 1. Leemos el contenido completo del archivo como texto  
    text_content = bytes_content.decode('utf-8', errors='replace')
    lines = text_content.splitlines()
    if not lines:
        raise ValueError("El archivo está vacío")

    # 2. Modificamos solo la primera línea (el header)
    header = lines[0].rstrip('\n\r')  # quitamos salto de línea si existe
    # Agregamos ; al final si no lo tiene ya
    if not header.endswith(';'):
        header += ';'

    # 3. Reconstruimos el contenido completo con el header corregido
    new_content = header + '\n' + ''.join(lines[1:])

    # 4. Ahora sí leemos con pandas usando el contenido modificado
    df = pd.read_csv(
        StringIO(new_content),
        sep=';',
        encoding='utf-8',
        dtype=str,
        header=0,
        on_bad_lines='warn',
        engine='python'
    )

    # 5. Limpieza de columnas y valores (igual que antes)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # 6. Columnas numéricas importantes en ventas.
    numeric_cols = [
        'Nro', 'Tipo Doc', 'Folio',
        'Monto Exento', 'Monto Neto', 'Monto IVA', 'Monto total',
        'IVA Retenido Total', 'IVA Retenido Parcial', 'IVA no retenido',
        'IVA propio', 'IVA Terceros',
        'Neto Comision Liquid. Factura', 'Exento Comision Liquid. Factura',
        'IVA Comision Liquid. Factura',
        'Monto No facturable', 'Total Monto Periodo',
        'Venta Pasajes Transporte Nacional', 'Venta Pasajes Transporte Internacional',
        'Valor Otro Imp.', 'Tasa Otro Imp.'
    ]
    for col in numeric_cols:
        if col in df.columns:
            # 1. Reemplazar valores no numéricos por '0' (como string)
            df[col] = df[col].replace(['', '-', '--', 'N/A'], '0')
            # 2. Forzamos todo a string ANTES de usar .str
            df[col] = df[col].astype(str)
            # 3. Ahora limpiamos el formato chileno sin miedo
            df[col] = df[col].str.replace('.', '', regex=False)      # quita puntos de miles
            df[col] = df[col].str.replace(',', '.', regex=False)     # coma → punto decimal
            # 4. Finalmente convertimos a número
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 7. Fechas.
    date_cols = ['Fecha Docto', 'Fecha Recepcion', 'Fecha Acuse Recibo', 'Fecha Reclamo']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    # 8. Aseguramos que 'Tipo Doc' sea string o int útil
    if 'Tipo Doc' in df.columns:
        df['Tipo Doc'] = df['Tipo Doc'].fillna('0').astype(str).str.strip()

    return df


# Recibe un dataframe y retorna un objeto de la clase DetalleVentas.
def parse_df_to_detalle_ventas(df: pd.DataFrame) -> DetalleVentas:
    # Convertimos a lista de dicts (más cómodos para tu dataclass)
    rows = df.to_dict(orient='records')

    facturas = []
    boletas = []          
    notas_debito = []
    notas_credito = []
    comprobantes_pago = []

    for row in rows:
        tipo_str = str(row.get('Tipo Doc', '0')).strip()
        tipo_int = int(tipo_str) if tipo_str.isdigit() else 0

        # Clasificación según códigos más comunes en ventas emitidas
        if tipo_int in (33, 34):           # Facturas afecta / exenta
            facturas.append(row)
        elif tipo_int in (39, 41):         # Boletas afecta / exenta
            boletas.append(row)
        elif tipo_int in (48):
            comprobantes_pago.append(row)
        elif tipo_int == 56:
            notas_debito.append(row)
        elif tipo_int == 61:
            notas_credito.append(row)

    # Resumen básico.
    resumen = {
    "total_neto_afecto": sum(float(r.get('Monto Neto', 0)) for r in facturas if float(r.get('Monto Exento', 0)) == 0),
    "total_exento": sum(float(r.get('Monto Exento', 0)) for r in rows),
    "total_iva_debito": sum(float(r.get('Monto IVA', 0)) for r in rows),
    "total_ventas": sum(float(r.get('Monto total', 0)) for r in rows),  # 34 ##
    "cantidad_facturas": len(facturas),  # 33  ##
    "cantidad_boletas_directas": len(boletas),              # 39/41
    "cantidad_comprobantes_pago": len(comprobantes_pago),   # 48  ##
    "cantidad_notas_debito": len(notas_debito),  # 56 ##
    "cantidad_notas_credito": len(notas_credito),  # 61  ##
    "total_documentos": len(rows),
    # Opcional: totales por grupo
    "total_ventas_boletas_directas": sum(float(r.get('Monto total', 0)) for r in boletas),
    "total_ventas_comprobantes_pago": sum(float(r.get('Monto total', 0)) for r in comprobantes_pago),
    }

    return DetalleVentas(
        facturas=facturas,
        boletas=boletas,
        comprobantesPago=comprobantes_pago,
        notasDebito=notas_debito,
        notasCredito=notas_credito,
        resumen=resumen
    )


# Recibe un dataframe y retorna un onjeto de la calse ResumenVentas.
def parse_df_to_resumen_ventas(df: pd.DataFrame) -> ResumenVentas:
    # Aseguramos que las columnas clave existan y sean numéricas (ya deberían estarlo por parse_detalle_ventas)
    required_cols = ['Tipo Doc', 'Monto Exento', 'Monto Neto', 'Monto IVA', 'Monto total']
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convertimos Tipo Doc a string para comparaciones seguras
    df['Tipo Doc'] = df['Tipo Doc'].astype(str).str.strip()

    # Limpieza de 'Tipo Venta' (en tu CSV es 'Del Giro')
    if 'Tipo Venta' in df.columns:
        df['Tipo Venta'] = df['Tipo Venta'].astype(str).str.strip().str.lower()
    else:
        df['Tipo Venta'] = 'del giro'  # fallback

    # Función auxiliar.
    def crear_dict_resumen(codigo: int, filtro_df: pd.DataFrame) -> Dict:
        if filtro_df.empty:
            return {
                'tipo': codigo,
                'desc': "",
                'td': 0,
                'exento': 0,
                'neto': 0.0,
                'iva': 0.0,
                'total': 0.0
            }
        return {
            'tipo': codigo,
            'desc': "",
            'td': len(filtro_df),
            'exento': int(filtro_df['Monto Exento'].sum()),
            'neto': int(filtro_df['Monto Neto'].sum()),
            'iva': int(filtro_df['Monto IVA'].sum()),
            'total': int(filtro_df['Monto total'].sum())
        }

    # cod110: Exportaciones.
    export_filter = df['Tipo Venta'].str.contains('export', case=False, na=False)
    cod110 = crear_dict_resumen(110, df[export_filter])
    cod110['desc'] = 'Exportaciones'

    # cod34: Ventas exentas/no gravadas → donde Monto Exento > 0 
    exento_filter = df['Monto Exento'] > 0
    cod34 = crear_dict_resumen(34, df[exento_filter])
    cod34['desc'] = 'Ventas y/o servicios exentos o no grabados'

    # cod46: Facturas de compra recibidas con retención total (cambio de sujeto total).
    filtro_cod46 = df['Tipo Doc'] == '46'
    cod46 = crear_dict_resumen(46,df[filtro_cod46])
    cod46['desc'] = 'Facturas de compra recibidas con ret.total (cambio de sujeto)'

    # cod33: Facturas emitidas.
    cod33 = crear_dict_resumen(33, df[df['Tipo Doc'] == '33'])
    cod33['desc'] = 'facturas emitidas'

    # cod39: Boletas (incluye 39 y posiblemente 41 para boletas electrónicas).
    boletas_filter = df['Tipo Doc'].isin(['39', '41'])
    cod39 = crear_dict_resumen(39, df[boletas_filter])
    cod39['desc'] = 'cantidad de documentos boletas'

    # cod48: Comprobante o recibo de transacciones medios
    cod48 = crear_dict_resumen(48, df[df['Tipo Doc'] == '48'])
    cod48['desc'] = 'comprobante o recibo de transacciones medios'

    # cod56: Notas de débito emitidas
    cod56 = crear_dict_resumen(56, df[df['Tipo Doc'] == '56'])
    cod56['desc'] = 'notas de débito emitidas'

    # cod61: Notas de crédito emitidas
    cod61 = crear_dict_resumen(61, df[df['Tipo Doc'] == '61'])
    cod61['desc'] = 'notas de crédito emitidas'

    # cod45: Facturas de compra recibidas (general o con retención parcial)
    # Aparece en Registro de Compras cuando es factura electrónica de compra (tipo 45)
    filtro_cod45 = df['Tipo Doc'] == '45'
    cod45 = crear_dict_resumen(45, df[filtro_cod45])
    cod45['desc'] = 'Facturas de compra recibidas'

    # cod43: Liquidación y liquidación factura
    cod43 = crear_dict_resumen(43, df[df['Tipo Doc'] == '43'])
    cod43['desc'] = 'liquidacion y liquidacion factura'

    return ResumenVentas(
        cod110=cod110,
        cod34=cod34,
        cod46=cod46,
        cod33=cod33,
        cod39=cod39,
        cod48=cod48,
        cod56=cod56,
        cod61=cod61,
        cod45=cod45,
        cod43=cod43
    )

