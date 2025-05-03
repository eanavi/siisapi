import pdb
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
from sqlalchemy.sql import text
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


def preparar_bd():
    db = next(leer_bd())
    consulta = f"""
    CREATE TYPE public.edad AS (
	anio int4,
	mes int4,
	dia int4);

    CREATE OR REPLACE FUNCTION public.calcular_edad_pg(fecha_nacimiento date)
    RETURNS edad
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        fecha_actual DATE := CURRENT_DATE;
        anios INTEGER;
        meses INTEGER;
        dias INTEGER;
    BEGIN
        anios := EXTRACT(YEAR FROM fecha_actual) - EXTRACT(YEAR FROM fecha_nacimiento);
        meses := EXTRACT(MONTH FROM fecha_actual) - EXTRACT(MONTH FROM fecha_nacimiento);
        dias := EXTRACT(DAY FROM fecha_actual) - EXTRACT(DAY FROM fecha_nacimiento);

        IF meses < 0 OR (meses = 0 AND dias < 0) THEN
            anios := anios - 1;
            meses := meses + 12;
            IF dias < 0 THEN
                meses := meses - 1;
                -- Calcular los días en el mes anterior de la fecha de nacimiento
                dias := dias + (DATE_TRUNC('day', fecha_actual - INTERVAL '1 month') + INTERVAL '1 month' - DATE_TRUNC('day', fecha_actual - INTERVAL '1 month'))::INTEGER;
                IF meses < 0 THEN
                    meses := 11;
                    anios := anios - 1;
                END IF;
            END IF;
        END IF;

        RETURN ROW(anios, meses, dias)::edad;
    END;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.es_dia_valido(anio integer, mes integer, dia integer)
    RETURNS boolean
    LANGUAGE plpgsql
    IMMUTABLE
    AS $function$
    DECLARE
        max_dias INTEGER;
    BEGIN
        IF mes < 1 OR mes > 12 OR dia < 1 THEN
            RETURN FALSE;
        END IF;

        CASE mes
            WHEN 2 THEN
                IF (anio % 4 = 0 AND anio % 100 <> 0) OR anio % 400 = 0 THEN
                    max_dias := 29;
                ELSE
                    max_dias := 28;
                END IF;
            WHEN 4, 6, 9, 11 THEN
                max_dias := 30;
            ELSE
                max_dias := 31;
        END CASE;

        RETURN dia <= max_dias;
    END;
    $function$
    ;
    """
    db.execute(text(consulta))
    db.commit()
    db.close()


def inicia_tablas():
    db = next(leer_bd())
    consulta = f""" 
    INSERT INTO public.prestacion (id_centro,nombre,sigla,edad_maxima,edad_minima,genero,tipo_prestador,tiempo_maximo,estado_reg,usuario_reg,ip_reg,fecha_reg) VALUES
        (1,'Consulta Externa','CE','(120,0,0)','(5,0,0)','A','M',15,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Atención al Niño Sano','NS','(5,12,31)','(0,0,0)','A','M',15,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Anticoncepción','AC','(120,0,0)','(5,0,0)','A','M',15,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Odontología','OD','(120,0,0)','(0,0,0)','A','O',20,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Control Prenatal','CP','(65,0,0)','(16,0,0)','F','M',20,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Seguimiento Internaciones','SI','(120,0,0)','(0,0,0)','A','M',10,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Vacunas','VC','(120,0,0)','(0,0,0)','A','E',5,'V','eanavi','127.0.0.1','2025-04-29 00:00:00'),
        (1,'Certificado de Defunción','CD','(120,0,0)','(0,0,0)','A','M',10,'V','eanavi','127.0.0.1','2025-04-29 00:00:00');
    """
    db.execute(text(consulta))
    db.commit()
    db.close()


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
    preparar_bd()
    inicio_bd()
    inicia_tablas()
