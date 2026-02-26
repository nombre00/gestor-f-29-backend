
import pandas as pd
from typing import Dict
from io import StringIO
# Importación módulos.
from f29_backend.domain.entities.detalleCompras import DetalleCompras
from f29_backend.domain.entities.resumenCompras import ResumenCompras

# Lee el documento y retorna un data frame.
def parse_detalle_compras(bytes_content: bytes):
    # 1. Convertimos bytes a texto
    try:
        text_content = bytes_content.decode('utf-8')
    except UnicodeDecodeError:
        text_content = bytes_content.decode('latin-1', errors='replace')

    lines = text_content.splitlines()
    if not lines:
        raise ValueError("El archivo está vacío")

    # 2. Fix del header (igual que antes)
    header = lines[0].rstrip('\n\r')
    if not header.endswith(';'):
        header += ';'

    # 3. Reconstruimos
    new_content = header + '\n' + '\n'.join(lines[1:])

    # 4. Leemos con pandas desde StringIO
    df = pd.read_csv(
        StringIO(new_content),
        sep=';',
        encoding='utf-8',
        dtype=str,
        header=0,
        on_bad_lines='warn',
        engine='python'
    )

    # 5. Limpieza de columnas y valores.
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # 6. Conversión de tipos numéricos
    numeric_cols = [
        'Nro', 'Tipo Doc', 'Folio', 'Monto Exento', 'Monto Neto',
        'Monto IVA Recuperable', 'Monto Iva No Recuperable',
        'Monto Total', 'Monto Neto Activo Fijo', 'IVA Activo Fijo',
        'IVA uso Comun', 'Impto. Sin Derecho a Credito', 'IVA No Retenido',
        'Tabacos Puros', 'Tabacos Cigarrillos', 'Tabacos Elaborados',
        'NCE o NDE sobre Fact. de Compra', 'Codigo Otro Impuesto',
        'Valor Otro Impuesto', 'Tasa Otro Impuesto'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 7. Conversión de fechas
    date_cols = ['Fecha Docto', 'Fecha Recepcion', 'Fecha Acuse']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    return df # Remornamos el dataframe creado.


# Recibe un dataframe y genera un objeto de la calse DetalleCompras. (Por ahora avanzado y no terminado, se trabaja con el resumenCompras).
def parse_df_to_detalle_compras(df) -> DetalleCompras:
    # Convertir filas a dicts.
    rows = df.to_dict(orient='records')

    facturas = []
    nd = []
    nc = []
    fe = []

    for row in rows:
        tipo = int(row.get('Tipo Doc', 0))
        if tipo == 33:
            facturas.append(row)
        elif tipo == 56:
            nd.append(row)
        elif tipo == 61:
            nc.append(row)
        elif tipo == 34:
            fe.append(row)

    # Calcular resumen básico
    resumen = {
        "total_neto": sum(r.get('Monto Neto', 0) for r in rows),
        "total_iva_recuperable": sum(r.get('Monto IVA Recuperable', 0) for r in rows),
        "total_compras": sum(r.get('Monto Total', 0) for r in rows),
        "credito_fiscal": sum(r.get('Monto IVA Recuperable', 0) for r in rows),
        "cantidad_documentos": len(rows),
    }

    return DetalleCompras(
        facturas=facturas,
        notas_debito=nd,
        notas_credito=nc,
        factura_exenta=fe,
        resumen=resumen
    )


# Recibe un dataframe y retorna un objeto de la clase ResumenCompras.
def parse_df_to_resumen_compras(df: pd.DataFrame) -> ResumenCompras:

    # Nos aseguramos que las columnas clave existan y sean numéricas.
    required_cols = ['Tipo Doc', 'Monto Exento', 'Monto Neto', 'Monto IVA', 'Monto total']
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convertimos Tipo Doc a string para comparaciones seguras.
    df['Tipo Doc'] = df['Tipo Doc'].astype(str).str.strip()

    # Convertimos Tipo Compra a string minuscula para comparaciones seguras.
    if 'Tipo Compra' in df.columns:
        df['Tipo Compra'] = df['Tipo Compra'].astype(str).str.strip().str.lower()
    else:
        # Si no existe, asumimos todo 'del giro' y logueamos.
        df['Tipo Compra'] = 'del giro'
        print("Advertencia: Columna 'Tipo Compra' no encontrada → asumiendo 'del giro' para todos")

    # Función auxiliar.
    def crear_dict(
        tipo: int,
        desc: str,
        filtro_df: pd.DataFrame,
        iva_rec_extra: int = 0
    ) -> Dict:
        if filtro_df.empty:
            return {
                'tipo': tipo,
                'desc': desc,
                'td': 0,
                'exento': 0,
                'neto': 0,
                'iva_rec': 0,
                'iva_no_rec': 0,
                'total': 0
            }

        iva_rec = (
            filtro_df['Monto IVA Recuperable'].sum() +
            filtro_df['IVA uso Comun'].sum() +   # Uso común suele ser recuperable (prorrateo aparte)
            iva_rec_extra
        )

        iva_no_rec = (
            filtro_df['Monto Iva No Recuperable'].sum() +
            filtro_df['Impto. Sin Derecho a Credito'].sum() 
            # filtro_df['Codigo IVA No Rec.'].sum()   # Posible error, comentado por ahora.
        )

        return {
            'tipo': tipo,
            'desc': desc,
            'td': len(filtro_df),
            'exento': int(filtro_df['Monto Exento'].sum()),
            'neto': int(filtro_df['Monto Neto'].sum()),
            'iva_rec': int(iva_rec),
            'iva_no_rec': int(iva_no_rec),
            'total': int(filtro_df['Monto Total'].sum())
        }
    

    # Ingreso de los datos.
    # cod34: Compras internas exentas o no grabadas 
    exento_filter = df['Monto Exento'] > 0
    cod34 = crear_dict(34, 'Compras internas exentas o no grabadas', df[exento_filter])
    

    # cod33: Facturas recibidas y facturas de compra (principal). SOLO las del giro (excluyendo supermercado/activo fijo)
    # Supermercado: contiene 'supermercado', 'superm', 'comercio similar'. No tenemos un ejemplo en el ejemplo.
    es_supermercado = df['Tipo Compra'].str.contains('supermercado|superm|comercio similar', na=False)
    filtro_cod33 = (df['Tipo Doc'] == '33') & (~es_supermercado) & (~es_activo_fijo)
    cod33 = crear_dict(33, 'Facturas recibidas y facturas de compra', df[filtro_cod33])

    # codSupermercado: Facturas recibidas Prom. Superm art.33
    filtro_superm = es_supermercado & (df['Tipo Doc'].isin(['33', '39']))  # Limita a docs relevantes
    codSupermercado = crear_dict(
        761,  # Tipo como 761 (cantidad docs supermercado, para referencia)
        'Fact.Recib.Prov.Superm.Art.33 N°4 DL825(Ley 20.780)',
        df[filtro_superm]
    )

    # codActivoFijo: Facturas activo fijo.
    # Activo Fijo: contiene 'activo fijo' o 'activo' (para codPendiente2)
    es_activo_fijo = df['Tipo Compra'].str.contains('activo fijo|activo', na=False)
    filtro_activo = es_activo_fijo | ((df['Monto Neto Activo Fijo'] > 0) | (df['IVA Activo Fijo'] > 0))
    codActivoFijo = crear_dict(
        524,  # Tipo como 524 (cantidad docs activo fijo)
        'Facturas activo fijo',
        df[filtro_activo],
        iva_rec_extra=int(df[filtro_activo]['IVA Activo Fijo'].sum())
    )

    # cod61: Notas de crédito recibidas (normalmente restan crédito → valores negativos o en iva_rec negativo)
    cod61 = crear_dict(61, 'Notas de crédito recibidos', df[df['Tipo Doc'] == '61'])

    # cod56: Notas de débito recibidas
    cod56 = crear_dict(56, 'Notas de débito recibidas', df[df['Tipo Doc'] == '56'])

    
    # cod914: Form. de pago de importaciones del giro. Revisamos que el codigo sea 914 y el tipo compra del giro.
    filtro_914 = (df['Tipo Doc'] == '914') & (df['Tipo Compra'].str.lower() == 'del giro')
    cod914 = crear_dict(914, 'Importaciones del giro', df[filtro_914])

    # codActivoFijoImportacion: Form. de pago de importaciones de activo fijo. Revisamos que el coidgo sea 914 y el tipo compra activo fijo.
    codActivoFijoImportacion = crear_dict(536, 'Importaciones activo fijo', df[df['Tipo Doc'] == '914'] & es_activo_fijo)

    return ResumenCompras(
        cod34=cod34,
        cod33=cod33,
        codSupermercado=codSupermercado,
        codActivoFijo=codActivoFijo,
        cod61=cod61,
        cod56=cod56,
        cod914=cod914,
        codActivoFijoImportacion=codActivoFijoImportacion
    )

