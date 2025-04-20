from app.componentes.siis1n.modelos.lista import Lista
from app.componentes.siis1n.modelos.grupo import Grupo
from app.componentes.siis1n.modelos.rol import Rol
from app.componentes.siis1n.modelos.empleado import Empleado
from app.componentes.siis1n.modelos.centro import Centro
from app.componentes.siis1n.modelos.usuario import Usuario
from app.componentes.siis1n.modelos.persona import Persona
from app.componentes.siis1n.modelos.base import ModeloBase, ParametroBase
from app.nucleo.configuracion import config
from app.nucleo.seguridad import generar_clave_encriptata
from app.nucleo.baseDatos import leer_bd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import date, datetime
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

engine = create_engine(
    url=config.DB_URL,
    pool_size=config.conexiones_minimas,
    max_overflow=config.conexiones_maximas,
    pool_timeout=config.tiempo_expiracion,
    pool_recycle=config.pool_tiempo_espera,
)


def inicio_bd():
    db = next(leer_bd())

    ModeloBase.metadata.create_all(bind=engine)
    ParametroBase.metadata.create_all(bind=engine)

    admin_rol = db.query(Rol).filter(Rol.nombre == "Administrador").first()
    if not admin_rol:
        admin_rol = Rol(
            nombre='Administrador',
            descripcion='Rol de administrador del sistema',

            usuario_reg='eanavi',
            ip_reg='127.0.0.1'
        )
        db.add(admin_rol)
        db.commit()

    persona = db.query(Persona).filter(Persona.ci == "3379293").first()
    if not persona:
        persona = Persona(
            id_persona=uuid.uuid4(),
            tipo="E",
            ci="3379293",
            paterno="Anavi",
            materno="Jiménez",
            nombres="Elvis Roger",
            fecha_nacimiento=date(1968, 11, 13),
            sexo="M",
            direccion=[{"personal": {"calle": "Calle B", "numero": "341",
                                     "zona": "San José Obrero Alto Koani", "ciudad": "La Paz"}}],
            telefono={"celular": "62418210", "fijo": "987654321"},
            correo={"personal": "eanavi@gmail.com",
                    "trabajo": "elvis.anavi@lapaz.bo"},

            usuario_reg="eanavi",
            ip_reg="127.0.0.1"
        )
        db.add(persona)
        db.commit()

    cs = db.query(Centro).filter(Centro.nombre == "San José Natividad").first()
    if not cs:
        cs = Centro(
            codigo_snis=200061,
            nombre="San José Natividad",
            direccion="localhost",
            usuario="soaps1nusr",
            clave="soaps1npsw",
            puerto="1433",

            usuario_reg="eanavi",
            ip_reg="127.0.0.1",
        )
        db.add(cs)
        db.commit()

    empleado = db.query(Empleado).filter(
        Empleado.id_persona == persona.id_persona).first()
    if not empleado:
        empleado = Empleado(
            id_persona=persona.id_persona,
            id_centro=cs.id_centro,
            tipo_empleado='A',
            profesion=1,
            registro_profesional='M-1368',
            cargo="Jefe de Sistemas",

            usuario_reg="eanavi",
            ip_reg="127.0.0.1"

        )
        db.add(empleado)
        db.commit()

    usuario = db.query(Usuario).filter(
        Usuario.nombre_usuario == "eanavi").first()
    if not usuario:
        usuario = Usuario(
            id_empleado=empleado.id_empleado,
            id_rol=admin_rol.id_rol,
            nombre_usuario='eanavi',
            clave=generar_clave_encriptata("vicho.1368"),

            usuario_reg="eanavi",
            ip_reg="127.0.0.1",
        )
        db.add(usuario)
        db.commit()
    grupo = db.query(Grupo).filter(Grupo.nombre_grupo == "depto").first()
    if not grupo:
        grupo = Grupo(
            nombre_grupo="depto",
            tipo="N",
            area="A"

        )
        db.add(grupo)
        db.commit()

    deptos = [('Ch', 1, 'Chuquisaca', 1),
              ('LP', 2, 'La Paz', 2),
              ('Cb', 3, 'Cochabamba', 3),
              ('Or', 4, 'Oruro', 4),
              ('Pt', 5, 'Potosi', 5),
              ('Tj', 6, 'Tarija', 6),
              ('SC', 7, 'Santa Cruz', 7),
              ('Bn', 8, 'Beni', 8),
              ('Pn', 9, 'Pando', 9),
              ]

    for depto in deptos:
        departamento = Lista(
            id_grupo=grupo.id_grupo,
            cod_texto=depto[0],
            cod_numero=depto[1],
            descripcion=depto[2],
            orden=depto[3],
        )
        db.add(departamento)
        db.commit()

    db.close()


if __name__ == "__main__":
    inicio_bd()
