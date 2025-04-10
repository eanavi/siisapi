from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .base import ServicioBase
from ..modelos.persona import Persona
from app.componentes.siis1n.servicios.centro import ServicioCentro
from app.nucleo.bdSoaps import obtener_sesion_mssql
from app.utiles.paginacion import paginacion
from typing import Generator
from app.utiles.convertir import transformar_se_hc_persona


class ServicioPersona(ServicioBase):
    def __init__(self):
        super().__init__(Persona, 'id_persona')

    def buscar_persona(self, db: Session, criterio: str, pagina: int, tamanio: int):
        resultado = db.execute(text(f"""
            SELECT * FROM public.buscar_personas(:criterio)
        """), {'criterio': criterio})
        filas = resultado.mappings().all()
        if filas:
            personas = [dict(f) for f in filas]
            for persona in personas:
                persona["procedencia"] = "propio"
            return paginacion(personas, pagina, tamanio)

        ser_centro = ServicioCentro()
        centros_paginados = ser_centro.leer_todos(db, 1, 1000)
        centros = centros_paginados["items"]

        for centro in centros:
            serv = centro.direccion
            base_datos = "BDEstadistica"
            usuario = centro.usuario
            clave = centro.clave

            try:
                with next(obtener_sesion_mssql(serv, base_datos, usuario, clave)) as db_mssql:
                    resultado = db_mssql.execute(text(f"""
                       exec dbo.spBuscaPersona :criterio
                    """), {'criterio': criterio})
                    filas = resultado.mappings().all()
                    if filas:
                        personas = [
                            transformar_se_hc_persona(f, centro.nombre) for f in filas]
                        return paginacion(personas, pagina, tamanio)
            except Exception as e:
                print(f"Error al consultar centro {centro.nombre}: {str(e)}")
                continue
        return []
