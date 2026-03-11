# Bibliotecas.
from typing import List, Dict, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
# Módulos.
from f29_backend.infrastructure.persistence.repository.resumenAnualRepository import ResumenAnualRepository
from f29_backend.infrastructure.persistence.repository.resumenF29Repository import ResumenF29Repository
from f29_backend.domain.entities.resumenF29 import ResumenF29  # entidad dominio
from f29_backend.api.schemas.resumenAnualSchema import ResumenAnualResponse, ResumenAnualContenido, EstadoResumenAnual
from f29_backend.infrastructure.persistence.models.usuario import Usuario
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository


class ResumenAnualService:
    # Constructor, genera la conección.
    def __init__(self, db: Session):
        self.db = db  # Conección a la base de datos.
        self.repo_anual = ResumenAnualRepository(db)  # Coneccion a tabla resumenes anuales.
        self.repo_f29 = ResumenF29Repository(db)  # Conección a tabla f29s.
    


    # Funcion que busca los datos del dashboard.
    def get_dashboard_anual(self, current_user: Usuario, anio: str) -> Dict:
        if not hasattr(current_user, 'empresa_id') or not current_user.empresa_id:
            raise ValueError("Usuario sin empresa asignada")
        repo_cliente = ClienteRepository(self.db)  # Nos conectamos a la tabla cliente.
        # Buscamos los clientes activos asociados a este empresa y los guardamos en una lista.
        clientes = repo_cliente.find_by_empresa(empresa_id=current_user.empresa_id,solo_activos=True,skip=0,limit=1000)
        resultado = []  # Declaramos una lista, esta va a ser una lista de diccionarios.
        for cliente in clientes:  # Iteramos los clientes encontrados.
            anual = self.repo_anual.get_by_cliente_and_año(cliente.id, anio)  # Buscamos el resumenAnual del cliente durante el año seleccionado.
            f29s = self.repo_anual.get_all_f29_del_año(cliente.id, anio)  # Buscamos todos los f29s del cliente durante el año seleccionado.
            total_f29 = len(f29s)  # Contamos los 29s encontrados.
            # Buscamos y contamos los meses incluidos en el resumenAnual, si no hay un resumen anual asignamos 0.
            meses_incluidos = len(anual.periodos_incluidos_json) if anual else 0
            # Restamos los meses incluidos en el resumenAnual de los f29s encontrados, lo que sobra son los f29s aun no incluidos.
            f29_pendientes = total_f29 - meses_incluidos if anual else total_f29
            # Con estos datos tenemos lo necesario para una fila del dashboard, que es un cliente.
            resultado.append({  # Agregamos los datos de la fila
                "id": cliente.id,  # id del cliente.
                "nombre": cliente.razon_social,  # nombre.
                "rut": cliente.rut,  # rut.
                "nro_cliente": cliente.nro_cliente,  # nro del cliente.
                "resumen_anual": {   # Del resumen anual: 
                    "existe": bool(anual),  # si existe.
                    "estado": anual.estado.value if anual else None,  # el estado.
                    "meses_incluidos": meses_incluidos,  # meses incluidos
                    "f29_pendientes": max(0, f29_pendientes),  # meses pendientes.
                }
            })
        return {  # Terminadas las iteraciones de los clientes retornamos:
            "clientes": resultado,  # Las filas de la tabla.
            "total_clientes": len(clientes),  # El total de los clientes.
            "total_generados": sum(1 for c in resultado if c["resumen_anual"]["existe"]),  # Resumenes anuales generados
            "total_pendientes": sum(1 for c in resultado if not c["resumen_anual"]["existe"]),  # Resúmenes anuales aun no generados.
        }



    # Método que se usa cuando navegamos de la página gestor a la pagina vista de resumenAnual.
    # Crea o retorna un resumenAnual (no calcula datos, solo crea la entrada en la tabla con 0s).
    def get_or_create_anual(self, cliente_id: int, año: str, usuario_id: int) -> ResumenAnualResponse:
        anual = self.repo_anual.get_by_cliente_and_año(cliente_id, año)  # Buscamos el resumenAnual.
        if not anual:  # Si no lo encontramos lo creamos.
            anual = self.repo_anual.create(
                cliente_id=cliente_id,
                año=año,
                creado_por_usuario_id=usuario_id,
                detalles_json={},
                periodos_incluidos_json=[],
            )
        return self._to_response(anual)  # Retornamos el resumenAnual creado o encontrado.



    # Tabula los datos de los f29s ingresados en un resumen anual y retorna una respuesta.
        # Esta función recibe: cliente_id  +  año  +  usuario_id.
        # Busca los f29_modelos, los desserializa a f29_entidades.
        # LLama a la función auxiliar _acumular_f29s() que hace los cálculos y retorna un resumenAnual.
        # Creamos o actualizamos el resumen anual creado acorde al caso.
        # LLama a la función _to_response para retornar un esquema de respuesta REST para esta operación.
    def recalcular_anual(self, cliente_id: int, año: str, usuario_id: int) -> ResumenAnualResponse:
        # Buscamos los f29s del cliente el año seleccionado y los guardamos en una lista.
        f29s_modelos = self.repo_anual.get_all_f29_del_año(cliente_id, año)
        if not f29s_modelos:  # Si no encontramos:
            raise HTTPException(404, "No hay F29 generados para este cliente y año")
        
        # Deserializamos los datos de la columna detalles_json
        f29s_entidades = []  # Creamos la lista donde guaradmos los objetos de la clase entidad ResumenF29.
        for modelo in f29s_modelos:  # Por f29 en f29_modelos:
            if modelo.detalles_json:  # Si hay un detalle: 
                f29s_entidades.append(ResumenF29.from_dict(modelo.detalles_json))  # Desserializamos. 
        if not f29s_entidades:  # Si no: 
            raise HTTPException(404, "Los F29 encontrados no tienen datos procesados")
        
        # Guardamos los periodos de los f29s_modelos encontrados
        periodos = self.repo_anual.get_periodos_de_f29s(f29s_modelos)
        # LLamamos a la funcion _acumular_f29s() para hacer los cálculos, esta retorna un resumenAnual (entidad).
        acumulado: ResumenF29 = self._acumular_f29s(f29s_entidades)

        # Para persistir:
        # Revisamos si el resumenAnual existe.
        anual = self.repo_anual.get_by_cliente_and_año(cliente_id, año)  # Buscamos el resumenAnual por cliente y año.
        if anual:  # Si existe actualizamos.
            anual = self.repo_anual.update(resumen=anual,detalles_json=acumulado.to_dict(),periodos_incluidos_json=periodos,)
        else:  # Si no existe lo creamos.
            anual = self.repo_anual.create(cliente_id=cliente_id,año=año,creado_por_usuario_id=usuario_id,
                                            detalles_json=acumulado.to_dict(),periodos_incluidos_json=periodos,)
        # LLamamos a la función _to_response() para formatear la respuesta al esquema REST correspondiente y retornamos.
        return self._to_response(anual)



    # Funciones auxiliares 
    # Calcula los datos.
    def _acumular_f29s(self, f29s: List[ResumenF29]) -> ResumenF29:
        if not f29s:  # Si la lista está vacía:
            return ResumenF29()  # Retorna un resumenAnual vacío.
        acum = ResumenF29()  # Inicializamos un resumenAnual (es lo mismo que un ResumenF29, reutilizamos la entidad).

        # Tabulamos.
        # Empezamos con detalle_compras y detalle_ventas que son los más complejos, son las listas de diccionarios.
        ventas_acum = {}  # Declaramos el diciconario de ventas acumuladas.
        compras_acum = {}  # Declaramos el diccionario de compras acumuladas.
        for f29 in f29s:  # Por f29 en f29s: 
            # Partimos con ventas:
            for fila in f29.ventas_detalle:  # Por diccionario en venta_detalle (una fila del detalle):
                tipo = fila['tipo']   # Buscamos el tipo (código) de la fila.
                if tipo not in ventas_acum:  # Buscamos en el diccionario que recibe si la fila existe:
                    ventas_acum[tipo] = fila.copy()  # Si no existe copiamos.
                else:  # Si existe sumamos los valores numéricos.
                    for k in ['td', 'exento', 'neto', 'iva', 'total']:  # Por k (llave) en la lista de llaves: 
                        ventas_acum[tipo][k] += fila.get(k, 0)  # Ventas_acum[codigo][llave] += fila.get(llave, sino 0).
            # Seguimos con compras y repetimos el mismo patrón:
            for fila in f29.compras_detalle:  # Por diccionario en compras_detalle (una fila del detalle):
                tipo = fila['tipo']   # Buscamos el tipo (código) de la fila.
                if tipo not in compras_acum:  # Buscamos en el diccionario que recibe si la fila existe:
                    compras_acum[tipo] = fila.copy()  # Si no existe copiamos.
                else:  # Si existe sumamos los valores numéricos.
                    for k in ['td', 'exento', 'neto', 'iva_rec', 'iva_no_rec', 'total']:  # Por k (llave) en la lista de llaves: 
                        compras_acum[tipo][k] += fila.get(k, 0)  # Compras_acum[codigo][llave] += fila.get(llave, sino 0).

        # Terminadas las iteraciones agregamos los diccionarios de forma ordenada, recuerda que los diccionarios no son ordenados.
        codigos_ventas_orden = [110, 34, 46, 33, 39, 48, 56, 61, 45, 43]   # Orden de las filas en el documento.
        for cod in codigos_ventas_orden:  # Iteramos los diccionarios en orden por su código.
            if cod in ventas_acum:  # Si el codigo existe:
                acum.ventas_detalle.append(ventas_acum[cod])  # Agregamos al resumenAnual.
            else:  # Si no existe: 
                acum.ventas_detalle.append({'tipo': cod, 'td': 0, 'exento': 0, 'neto': 0, 'iva': 0, 'total': 0})   # Agregamos el diccionario en 0s.
        codigos_compras_orden = [34, 33, 761, 524, 61, 56, 914, 536]   # Orden de las filas en el documento.
        for cod in codigos_compras_orden:  # Iteramos los diccionarios en orden por su código.
            if cod in compras_acum:  # Si el codigo existe:
                acum.compras_detalle.append(compras_acum[cod])  # Agregamos al resumenAnual.
            else:  # Si no existe: 
                acum.compras_detalle.append({'tipo': cod, 'td': 0, 'exento': 0, 'neto': 0, 'iva_rec': 0, 'iva_no_rec': 0, 'total': 0})   # Agregamos el diccionario en 0s.

        # Ahora agregamos los totales, que son más simples, son ints o dicts.
        for f29 in f29s:  # Por f29 en f29s: 
            for k in ['td', 'exento', 'neto', 'iva', 'total']:  # Por llave en la lista de llaves: 
                acum.ventas_total[k] = acum.ventas_total.get(k, 0) + f29.ventas_total.get(k, 0)  # Agregamos los totales de ventas.
            for k in ['td', 'exento', 'neto', 'iva_rec', 'iva_no_rec', 'total']:  # Por llave en la lista de llaves: 
                acum.compras_total[k] = acum.compras_total.get(k, 0) + f29.compras_total.get(k, 0)  # Agregamos los totales de compras.
            acum.IVAPP += f29.IVAPP  # Agregamos iva por pagar.
            acum.TT += f29.TT  # agregamos total total.
            acum.arriendos_pagados += f29.arriendos_pagados  # agregamos arriendos pagados.
            acum.gastos_generales_boletas += f29.gastos_generales_boletas  # Agregamos gastos generales boletas.
            acum.remanente = f29.remanente  # Remanente no se agrega, nos quedamos con el último.

            # remuneraciones y honorarios: suma todos los valores numéricos
            for seccion in ['remuneraciones', 'honorarios']:  # Por llave en lista llaves: 
                sec = getattr(f29, seccion, {})
                if not sec:
                    continue
                target = getattr(acum, seccion)
                if not target:
                    setattr(acum, seccion, sec.copy())
                else:
                    for k, v in sec.items():
                        if isinstance(v, (int, float)):
                            target[k] = target.get(k, 0) + v
            
            # getattr:  getattr(objeto, nombre_del_atributo: string, valor_default_retornado); 
            # acá le estamos pasando un f29, el string 'ppm', y le decimos que retorne un diccionario vacío si no hay datos.
            # ppm: suma valores numéricos EXCEPTO tasa, que se queda con el del último mes
            # sec_ppm: diccionario que recibe, guarda datos de cada iteración.
            sec_ppm = getattr(f29, 'ppm', {})  # Si encuentra datos retorna el diccionario ppm que es el valor asociado a la llave ppm.
            if sec_ppm:   # Si encuentra el diccionario: 
                target_ppm = acum.ppm  # Asignamos al diccionario donde acumulamos el diccionario que acumula en resumenAnual.
                if not target_ppm:  # Si el diccionario no existe aun en resumenAnual:
                    acum.ppm = sec_ppm.copy()  # Copiamos los datos del diccionario encontrado al diccionario de resumenAnual.
                else:   # si el diccionario existe en resumenAnual:
                    for k, v in sec_ppm.items():  # Por llave valor en diccionario encontrado:
                        if isinstance(v, (int, float)):  # Si existe un valor int o float:
                            if k == 'tasa':  # Si llave es 'tasa':
                                target_ppm[k] = v  # Sobreescribinos, eso no se acumula.
                            else:   # Para lo demas acumulamos:
                                # diccionario_que_recibe[llave] = diccionario_resumenAnual.get(llave) + valor
                                target_ppm[k] = target_ppm.get(k, 0) + v
          
        # Encabezado del último mes.
        ultimo_f29 = f29s[-1]  # Buscamos el últmo 29 de la lista.
        enc = ultimo_f29.encabezado.copy()  # copiamos el encabezamo.
        enc['titulo'] = 'RESUMEN ACUMULADO FORMULARIO 29'  # Cambiamos el texto y lo guardamos en una variable.
        acum.encabezado = enc  # Asigamos el nuevo encabezado a resumenAnual.
        # Retornamos.
        return acum



    # Calcula o cuenta cuantos meses se incluyeron en el resumen anual.
    def _generar_rango_texto(self, periodos: List[str], año: str) -> str:
        if not periodos:
            return f"Año {año}"
        primer_mes = periodos[0].split("-")[1]
        ultimo_mes = periodos[-1].split("-")[1]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"{meses[int(primer_mes)-1]} - {meses[int(ultimo_mes)-1]} {año}"
    


    # Calcula o cuenta cuantos meses sin el año.
    def _generar_meses(self, periodos: List[str]) -> str:
        if not periodos:
            return " - "
        primer_mes = periodos[0].split("-")[1]
        ultimo_mes = periodos[-1].split("-")[1]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"{meses[int(primer_mes)-1]} - {meses[int(ultimo_mes)-1]}"



    # Genera un esquema de respuesta, recibe un resumenAnual de argumento.
    # Acá cambio el encabezado del resumenAnual entidad por el de resumenAnual modelo.
    def _to_response(self, anual) -> ResumenAnualResponse:  # Retorna un esquema de una respuesta de resumenAnual.
        periodos = anual.periodos_incluidos_json or []
        meses_count = len(periodos)
        rango_de_texto = self._generar_rango_texto(periodos, anual.año)  # este valor reemplaza encabezado['periodo_mes']
        meses = self._generar_meses(periodos)

        # modificamos el encabezado antes de retornar la respuesta.
        encabezado = anual.detalles_json.get('encabezado')  # Buscamos el encabezado.
        if encabezado:   # Si existe el encabezado.
            anual.detalles_json['encabezado']['periodo_mes'] = meses  # Modificamos los meses.
            anual.detalles_json['encabezado']['periodo_anio'] = anual.año  # Reasignamos el año, redundante pero igual.

        # Generamos la respuesta.
        contenido = ResumenAnualContenido(**anual.detalles_json) if anual.detalles_json else ResumenAnualContenido()
        return ResumenAnualResponse(
            id=anual.id,
            cliente_id=anual.cliente_id,
            año=anual.año,
            estado=anual.estado,
            creado_por_usuario_id=anual.creado_por_usuario_id,
            created_at=anual.created_at,
            updated_at=anual.updated_at,
            periodos_incluidos=periodos,
            contenido=contenido,
            meses_incluidos_count=meses_count,
            rango_texto=rango_de_texto,
        )

