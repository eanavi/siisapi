# -*- coding: utf-8 -*-
from ..componentes.siis1n.modelos.lista import Lista
from ..componentes.siis1n.modelos.grupo import Grupo
from ..componentes.siis1n.modelos.rol import Rol
from ..componentes.siis1n.modelos.empleado import Empleado
from ..componentes.siis1n.modelos.centro import Centro
from ..componentes.siis1n.modelos.usuario import Usuario
from ..componentes.siis1n.modelos.persona import Persona
from ..componentes.siis1n.modelos.prestacion import Prestacion
from ..componentes.siis1n.modelos.paciente import Paciente
from ..componentes.siis1n.modelos.turno import Turno
from ..componentes.siis1n.modelos.reserva import Reserva
from ..componentes.siis1n.modelos.consulta import Consulta
from ..componentes.siis1n.modelos.variables import Variables
from ..componentes.siis1n.modelos.base import ModeloBase, ParametroBase
from ..nucleo.configuracion import config
from ..nucleo.seguridad import generar_clave_encriptata
from ..nucleo.baseDatos import leer_bd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, configure_mappers
from sqlalchemy.sql import text
from datetime import date, datetime
import uuid
import sys
import os
import logging


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.orm").setLevel(logging.DEBUG)

# Configuración de la conexión a la base de datos

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
    INSERT INTO public.prestacion (id_centro,nombre_prestacion,sigla,edad_maxima,edad_minima,genero,tipo_prestador,tiempo_maximo,estado_reg,usuario_reg,ip_reg,fecha_reg) VALUES
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

    consulta2 = f"""
    insert into public.grupo (id_grupo, nombre_grupo, tipo, area, estado_reg) values
        (1,'cf_ingresofam','N','M','V'),
        (2,'hv_estadocivil','N','M','V'),
        (3,'hv_falle_ocurr','N','M','V'),
        (4,'hv_gradoinstruc','N','M','V'),
        (5,'hv_lugar','N','M','V'),
        (6,'hv_manera','N','M','V'),
        (7,'hv_mecanismo','N','M','V'),
        (8,'hv_proc_efectua','N','M','V'),
        (9,'hv_rango_inter','N','M','V'),
        (10,'hv_sexo','N','M','V'),
        (11,'hv_tipodocument','N','M','V'),
        (12,'se_atencion_par','N','M','V'),
        (13,'se_bucomax_medi','N','M','V'),
        (14,'se_bucomax_meno','N','M','V'),
        (15,'se_causafalle','N','M','V'),
        (16,'se_cirbucalmeno','N','M','V'),
        (17,'se_control','N','M','V'),
        (18,'se_control_pren','N','M','V'),
        (19,'se_cuarto_con','N','M','V'),
        (20,'se_dosis_comple','N','M','V'),
        (21,'se_dosis_hierro','N','M','V'),
        (22,'se_dosis_vitama','N','M','V'),
        (23,'se_dosis_zinc','N','M','V'),
        (24,'se_eclamsia','N','M','V'),
        (25,'se_endodoncia','N','M','V'),
        (26,'se_esta_nut5ano','N','M','V'),
        (27,'se_esta_nutr','N','M','V'),
        (28,'se_gestante_peu','N','M','V'),
        (29,'se_hemorragia','N','M','V'),
        (30,'se_hemorragia_p','N','M','V'),
        (31,'se_ingreso','N','M','V'),
        (32,'se_mebendazol','N','M','V'),
        (33,'se_metodo','N','M','V'),
        (34,'se_metodos_nat','N','M','V'),
        (35,'se_mortalidad','N','M','V'),
        (36,'se_mortalidad_i','N','M','V'),
        (37,'se_muer_mat_con','N','M','V'),
        (38,'se_muer_mat_not','N','M','V'),
        (39,'se_nacido15_49','N','M','V'),
        (40,'se_odonto_emb','N','M','V'),
        (41,'se_odonto_post','N','M','V'),
        (42,'se_otras_accion','N','M','V'),
        (43,'se_parto_dom','N','M','V'),
        (44,'se_parto_serv','N','M','V'),
        (45,'se_partopartera','N','M','V'),
        (46,'se_periodoncia','N','M','V'),
        (47,'se_pesoedad','N','M','V'),
        (48,'se_pesotalla','N','M','V'),
        (49,'se_piezadentari','N','M','V'),
        (50,'se_post_parto','N','M','V'),
        (51,'se_preeclamsia','N','M','V'),
        (52,'se_ref_contra','N','M','V'),
        (53,'se_reg_mortalid','N','M','V'),
        (54,'se_restaura','N','M','V'),
        (55,'se_rn_apegoprec','N','M','V'),
        (56,'se_rn_malfo','N','M','V'),
        (57,'se_rncontrol48h','N','M','V'),
        (58,'se_rx','N','M','V'),
        (59,'se_situacion_eg','N','M','V'),
        (60,'se_tallaedad','N','M','V'),
        (61,'se_tipo_anes','N','M','V'),
        (62,'se_tipo_pacient','N','M','V'),
        (63,'se_tipo_parto','N','M','V'),
        (64,'se_tipoegre','N','M','V'),
        (65,'variable_si_no','N','M','V'),
        (66,'se_tipo_dato','N','M','V');

        ALTER SEQUENCE public.grupo_id_grupo_seq
        RESTART 67;
    """

    db.execute(text(consulta2))
    db.commit()

    consulta3 = f"""
    INSERT INTO public.lista (id_grupo, cod_texto, cod_numero, descripcion, orden, estado_reg) VALUES
        (1,'',1,'Le Permite Ahorrar ', 1,'V'),
        (1,'',2,'Satisface Necesidades Basicas Y Otras ', 2,'V'),
        (1,'',3,'Satisface Necesidades Basicas ', 3,'V'),
        (1,'',4,'A Veces No Alcanza ', 4,'V'),
        (1,'',5,'Insuficiente ', 5,'V'),
        (2,'',1,'Soltera/O ', 1,'V'),
        (2,'',2,'Casada/O ', 2,'V'),
        (2,'',3,'Divorciada/O ', 3,'V'),
        (2,'',4,'Viuda/O ', 4,'V'),
        (2,'',5,'Union Estable ', 5,'V'),
        (2,'',6,'No Puede Determinarse ', 6,'V'),
        (3,'',1,'Establecimiento De Salud ', 1,'V'),
        (3,'',2,'Vivienda (Domicilio Particular) ', 2,'V'),
        (3,'',3,'Via Publica ', 3,'V'),
        (3,'',4,'Trabajo ', 4,'V'),
        (3,'',5,'No Puede Determinarse ', 5,'V'),
        (3,'',6,'Otros ', 6,'V'),
        (4,'',1,'Sin Instruccion ', 1,'V'),
        (4,'',2,'Primaria ', 2,'V'),
        (4,'',3,'Secundaria ', 3,'V'),
        (4,'',4,'Tecnico ', 4,'V'),
        (4,'',5,'Universitario ', 5,'V'),
        (4,'',6,'Otros ', 6,'V'),
        (4,'',7,'No Puede Determinarse ', 7,'V'),
        (5,'',1,'Domicilio ', 1,'V'),
        (5,'',2,'Via Publica ', 2,'V'),
        (5,'',3,'Trabajo ', 3,'V'),
        (5,'',4,'Institucion ', 4,'V'),
        (5,'',5,'Otros ', 5,'V'),
        (5,'',6,'No Puede Determinarse ', 6,'V'),
        (6,'',1,'Accidente ', 1,'V'),
        (6,'',2,'Suicidio ', 2,'V'),
        (6,'',3,'Homicidio ', 3,'V'),
        (6,'',4,'Natural ', 4,'V'),
        (6,'',5,'Subito ', 5,'V'),
        (6,'',6,'Indeterminada ', 6,'V'),
        (7,'',1,'Accidente De Transito ', 1,'V'),
        (7,'',2,'Caida (Precipitacion) ', 2,'V'),
        (7,'',3,'Golpe ', 3,'V'),
        (7,'',4,'Ataque De Animal ', 4,'V'),
        (7,'',5,'Asfixias ', 5,'V'),
        (7,'',6,'Electrocucion ', 6,'V'),
        (7,'',7,'Quemaduras ', 7,'V'),
        (7,'',8,'Intoxicacion ', 8,'V'),
        (7,'',9,'Desastre Natural ', 9,'V'),
        (7,'',10,'Arma Blanca ', 10,'V'),
        (7,'',11,'Proyectil De Arma De Fuego ', 11,'V'),
        (7,'',12,'Otros ', 12,'V'),
        (7,'',13,'No Puede Determinarse ', 13,'V'),
        (8,'',1,'Examen Fisico Clinico ', 1,'V'),
        (8,'',2,'Autopsia ', 2,'V'),
        (8,'',3,'Levantamiento De Cadaver ', 3,'V'),
        (8,'',4,'Exhumacion ', 4,'V'),
        (9,'',1,'Segundos ', 1,'V'),
        (9,'',2,'Minutos ', 2,'V'),
        (9,'',3,'Horas ', 3,'V'),
        (9,'',4,'Dias ', 4,'V'),
        (9,'',5,'Semanas ', 5,'V'),
        (9,'',6,'Meses ', 6,'V'),
        (9,'',7,'Años ', 7,'V'),
        (10,'',1,'Masculino ', 1,'V'),
        (10,'',2,'Femenino ', 2,'V'),
        (10,'',3,'No Puede Determinarse ', 3,'V'),
        (11,'',1,'Cedula De Identidad ', 1,'V'),
        (11,'',2,'Pasaporte ', 2,'V'),
        (11,'',3,'R.U.N. ', 3,'V'),
        (11,'',4,'Certificado De Nacimiento ', 4,'V'),
        (11,'',5,'No Porta ', 5,'V'),
        (12,'',1,'Proveedor Calificado En Servicio ', 1,'V'),
        (12,'',2,'Personal De Salud Calificado En Servicio ', 2,'V'),
        (12,'',3,'Partera Capacitada En Servicio ', 3,'V'),
        (12,'',4,'Partera Empirica En Servicio ', 4,'V'),
        (12,'',5,'Por Otros En Domicilio ', 5,'V'),
        (12,'',6,'Proveedor Calificado En Domicilio ', 6,'V'),
        (12,'',7,'Personal De Salud Calificado En Domicilio ', 7,'V'),
        (12,'',8,'Partera Capacitada En Domicilio ', 8,'V'),
        (12,'',9,'Partera Empirica En Domicilio ', 9,'V'),
        (13,'',1,'Tratamiento Dientes Y Maxilares ', 1,'V'),
        (13,'',2,'Tratamiento Tejidos Blandos ', 2,'V'),
        (13,'',3,'Tratamientos Quirurgicos ', 3,'V'),
        (13,'',4,'Tratamientos Glandulas Salivales ', 4,'V'),
        (13,'',5,'Tratamientos Articulacion Temporomandibular ', 5,'V'),
        (13,'',6,'Fractura Dentoalveolar Simple ', 6,'V'),
        (14,'',1,'Tratamiento Dientes Y Maxilares ', 1,'V'),
        (14,'',2,'Tratamiento Tejidos Blandos ', 2,'V'),
        (14,'',3,'Exodoncia De Diente Impactado ', 3,'V'),
        (15,'',1,'Menor De 7 Días ', 1,'V'),
        (15,'',2,'De 7 Dás A Menor De 1 Año ', 2,'V'),
        (15,'',3,'Por Diarrea En Menores De 5 Años ', 3,'V'),
        (15,'',4,'Por Desnutrición Aguda Grave En Menores De 5 Años ', 4,'V'),
        (15,'',5,'Por Neumonía En Menores De 5 Años ', 5,'V'),
        (15,'',6,'Por Otras Causas En Menores De 5 Años ', 6,'V'),
        (15,'',7,'Por Otras Causas En Personas De 5 Años Ó Más ', 7,'V'),
        (15,'',8,'Muerte Materna ', 8,'V'),
        (16,'',1,'Exodoncia ', 1,'V'),
        (16,'',2,'Tratamiento Alveolitis ', 2,'V'),
        (16,'',3,'Trat. De Absceso Periapical ', 3,'V'),
        (17,'',1,'Nueva Dentro ', 1,'V'),
        (17,'',2,'Repetido Dentro ', 2,'V'),
        (17,'',3,'Nueva Fuera ', 3,'V'),
        (17,'',4,'Repetida Fuera ', 4,'V'),
        (18,'',1,'Nuevos Antes Del 5º Mes - Dentro ', 1,'V'),
        (18,'',2,'Nuevos Antes Del 5º Mes - Fuera ', 2,'V'),
        (18,'',3,'Nuevos A Partir Del 5º Mes - Dentro ', 3,'V'),
        (18,'',4,'Nuevos A Partir Del 5º Mes - Fuera ', 4,'V'),
        (18,'',5,'Repetidos - Dentro ', 5,'V'),
        (18,'',6,'Repetidos - Fuera ', 6,'V'),
        (19,'',1,'Dentro ', 1,'V'),
        (19,'',2,'Fuera ', 2,'V'),
        (20,'',1,'Embarazadas ', 1,'V'),
        (20,'',2,'Puerperas ', 2,'V'),
        (21,'',1,'Menores De 1 Año ', 1,'V'),
        (21,'',2,'2 Años ', 2,'V'),
        (21,'',3,'3 A < 5 Años ', 3,'V'),
        (21,'',4,'1 Año ', 4,'V'),
        (21,'',5,'Menores De 6 Meses ', 5,'V'),
        (22,'',1,'Menor De 1 Año (Dosis Unica) ', 1,'V'),
        (22,'',2,'1 Año-1Ra Dosis ', 2,'V'),
        (22,'',3,'1 Año-2Da Dosis ', 3,'V'),
        (22,'',4,'2 A < 5 Años-1Ra Dosis ', 4,'V'),
        (22,'',5,'2 A < 5 Años-2Da Dosis ', 5,'V'),
        (23,'',1,'Menor De 1 Año ', 1,'V'),
        (23,'',2,'De 1 Año ', 2,'V'),
        (24,'',1,'Dentro ', 1,'V'),
        (24,'',2,'Fuera ', 2,'V'),
        (25,'',1,'Pulpotomía ', 1,'V'),
        (25,'',2,'Tratamiento Endodóntico ', 2,'V'),
        (26,'',1,'Bajo Peso ', 1,'V'),
        (26,'',2,'Peso Normal ', 2,'V'),
        (26,'',3,'Sobrepeso ', 3,'V'),
        (26,'',4,'Obesidad ', 4,'V'),
        (27,'',1,'Obesidad ', 1,'V'),
        (27,'',2,'Sobrepeso ', 2,'V'),
        (27,'',3,'Normal ', 3,'V'),
        (27,'',4,'Desnutrida ', 4,'V'),
        (28,'',1,'Dentro ', 1,'V'),
        (28,'',2,'Fuera ', 2,'V'),
        (29,'',1,'Dentro ', 1,'V'),
        (29,'',2,'Fuera ', 2,'V'),
        (30,'',1,'Dentro ', 1,'V'),
        (30,'',2,'Fuera ', 2,'V'),
        (31,'',1,'Referido ', 1,'V'),
        (31,'',2,'Espontaneo ', 2,'V'),
        (32,'',1,'1 A < 5 Años - 1Ra ', 1,'V'),
        (32,'',2,'1 A < 5 Años - 2Da ', 2,'V'),
        (33,'',1,'Diu-Nueva ', 1,'V'),
        (33,'',2,'Diu-Continua ', 2,'V'),
        (33,'',3,'Inyectable Trimestral-Nueva ', 3,'V'),
        (33,'',4,'Inyectable Trimestral-Continuo ', 4,'V'),
        (33,'',5,'Condon Masculino Nueva ', 5,'V'),
        (33,'',6,'Condon Masculino Continuo ', 6,'V'),
        (33,'',7,'Pildora-Nueva ', 7,'V'),
        (33,'',8,'Pildora-Continua ', 8,'V'),
        (33,'',9,'Pildora Anticonceptiva De Emergencia ', 9,'V'),
        (33,'',10,'Aqv-Masculino ', 10,'V'),
        (33,'',11,'Aqv-Femenino ', 11,'V'),
        (33,'',12,'Otros Metodos-Nueva ', 12,'V'),
        (33,'',13,'Otros Metodos-Continua ', 13,'V'),
        (33,'',14,'Condon Femenino Nuevo ', 14,'V'),
        (33,'',15,'Condon Femenino Continuo ', 15,'V'),
        (33,'',16,'Implante Subdermico Nuevo ', 16,'V'),
        (33,'',17,'Implante Subdermico Continuo ', 17,'V'),
        (34,'',1,'Mela-Nueva ', 1,'V'),
        (34,'',2,'Mela-Continua ', 2,'V'),
        (34,'',3,'Ritmo-Nueva ', 3,'V'),
        (34,'',4,'Ritmo-Continuo ', 4,'V'),
        (34,'',5,'Dias Fijos-Nuevo ', 5,'V'),
        (34,'',6,'Dias Fijos-Continuo ', 6,'V'),
        (35,'',1,'Muerte Neonatal Tardia (7-27 Días) ', 1,'V'),
        (35,'',2,'Muerte Menor De 28 Días Por Sepsis ', 2,'V'),
        (35,'',3,'Muerte Menor De 28 Días Por Asfixia Perinatal ', 3,'V'),
        (35,'',4,'Muerte De 28 Días A Menor De 1 Año ', 4,'V'),
        (35,'',5,'Muerte Menor 5 Años Por Diarrea ', 5,'V'),
        (35,'',6,'Muerte Menor 5 Años Por Neumonia ', 6,'V'),
        (35,'',7,'Muerte Menor 5 Años Por Desnutrición Aguda Grave ', 7,'V'),
        (35,'',8,'Muerte Menor De 5 Años Por Otras Causas ', 8,'V'),
        (35,'',9,'Sospecha De Muerte Por Dengue ', 9,'V'),
        (35,'',10,'Sospecha De Muerte Por Covid-19 ', 10,'V'),
        (36,'',1,'Muerte Fetal (Obito) ', 1,'V'),
        (36,'',2,'Muerte Neonatal Temprana (0-6 Días) ', 2,'V'),
        (36,'',3,'Muerte Neonatal Tardia (7-27 Días) ', 3,'V'),
        (36,'',4,'Muerte Menor De 28 Días Por Sepsis ', 4,'V'),
        (36,'',5,'Muerte Menor De 28 Días Por Asfixia Perinatal ', 5,'V'),
        (36,'',6,'Muerte De 28 Días A Menor De 1 Año ', 6,'V'),
        (36,'',7,'Muerte Menor 5 Años Por Diarrea ', 7,'V'),
        (36,'',8,'Muerte Menor 5 Años Por Neumonia ', 8,'V'),
        (36,'',9,'Muerte Menor 5 Años Por Desnutrición Aguda Grave ', 9,'V'),
        (36,'',10,'Muerte Menor De 5 Años Por Otras Causas ', 10,'V'),
        (36,'',11,'Muerte Materna ', 11,'V'),
        (36,'',12,'Todas Las Causas: 5 Años O Más ', 12,'V'),
        (36,'',13,'Sospecha De Muerte Por Dengue ', 13,'V'),
        (36,'',14,'Sospecha De Muerte Por Covid-19 ', 14,'V'),
        (37,'',1,'Dentro ', 1,'V'),
        (37,'',2,'Fuera ', 2,'V'),
        (38,'',1,'Dentro ', 1,'V'),
        (38,'',2,'Fuera ', 2,'V'),
        (39,'',1,'En Servicio ', 1,'V'),
        (39,'',2,'En Domicilio ', 2,'V'),
        (40,'',1,'Primera Consulta Embarazada ', 1,'V'),
        (40,'',2,'Consulta Nueva Embarazada ', 2,'V'),
        (40,'',3,'Consulta Repetida Embarazada ', 3,'V'),
        (41,'',1,'Primera Consulta Post-Parto ', 1,'V'),
        (41,'',2,'Consulta Nueva Post-Parto ', 2,'V'),
        (41,'',3,'Consulta Repetida Post-Parto ', 3,'V'),
        (42,'',1,'Historia Clinica ', 1,'V'),
        (42,'',2,'Primera Sesion Tartrectomia ', 2,'V'),
        (42,'',3,'Segunda Sesion Tartrectomia ', 3,'V'),
        (42,'',4,'Apertura De Camara ', 4,'V'),
        (42,'',5,'Instrumentacion/Irrigado Y/O Lavado De Conductos ', 5,'V'),
        (42,'',6,'Obturacion Temporal ', 6,'V'),
        (42,'',7,'Farmacoterapia ', 7,'V'),
        (42,'',8,'Pulido ', 8,'V'),
        (42,'',9,'Base Cavitaria ', 9,'V'),
        (42,'',10,'Retiro De Puntos ', 10,'V'),
        (42,'',11,'Ferulizacion ', 11,'V'),
        (42,'',12,'Apertura De Camara E Instrumentacion De Conducto ', 12,'V'),
        (42,'',13,'1Ra Fase Toma De Registro Superior ', 13,'V'),
        (42,'',14,'1Ra Fase Toma De Registro Inferior ', 14,'V'),
        (42,'',15,'2Da Fase Instalado Y Entrega Superior ', 15,'V'),
        (42,'',16,'2Da Fase Instalado Y Entrega Inferior ', 16,'V'),
        (42,'',17,'3Ra Fase Controles Superior ', 17,'V'),
        (42,'',18,'3Ra Fase Controles Inferior ', 18,'V'),
        (42,'',19,'Promocion - Entrega De Pasta / Entrega De Cepillo ', 19,'V'),
        (42,'',20,'Promocion - Entrega De Dedal De Silicona ', 20,'V'),
        (42,'',21,'Promocion - Educacion En Salud Oral ', 21,'V'),
        (42,'',22,'Estuches De Higiene Dental ', 22,'V'),
        (42,'',23,'Obturación Del Conducto Radicular ', 23,'V'),
        (43,'',1,'Rn Nacido Vivo < 2500 Gr ', 1,'V'),
        (43,'',2,'Rn Nacido Muerto < 2500 Gr ', 2,'V'),
        (43,'',3,'Rn Nacido Vivo >= 2500 Gr ', 3,'V'),
        (43,'',4,'Rn Nacido Muerto >= 2500 Gr ', 4,'V'),
        (43,'',5,'Partera Nacido Vivo ', 5,'V'),
        (43,'',6,'Partera Nacido Muerto ', 6,'V'),
        (43,'',7,'Atendido Por Otros Nacido Vivo ', 7,'V'),
        (43,'',8,'Atendido Por Otros Nacido Muerto ', 8,'V'),
        (44,'',1,'Menos De 2500 Gr.- Nacido Vivo ', 1,'V'),
        (44,'',2,'Menos De 2500 Gr.- Nacido Muerto ', 2,'V'),
        (44,'',3,'2500 Gr. O Mas - Nacido Vivo ', 3,'V'),
        (44,'',4,'2500 Gr. O Mas - Nacido Muerto ', 4,'V'),
        (45,'',1,'Nacido Vivo ', 1,'V'),
        (45,'',2,'Nacido Muerto ', 2,'V'),
        (46,'',1,'Tartrectomia ', 1,'V'),
        (46,'',2,'Gingivectomia Simple ', 2,'V'),
        (46,'',3,'Trat. No Quirurgico ', 3,'V'),
        (47,'',1,'Normal ', 1,'V'),
        (47,'',2,'Desnutricion Global Moderada ', 2,'V'),
        (47,'',3,'Desnutricion Global Severa ', 3,'V'),
        (48,'',1,'Obesidad (O) ', 1,'V'),
        (48,'',2,'Sobrepeso (S) ', 2,'V'),
        (48,'',3,'Normal (N) ', 3,'V'),
        (48,'',4,'Leve (L) ', 4,'V'),
        (48,'',5,'Moderada (M) ', 5,'V'),
        (48,'',6,'Grave (G) ', 6,'V'),
        (49,'',11,'Permanente Incisivo Central Superior Derecho ', 11,'V'),
        (49,'',12,'Permanente Incisivo Lateral Superior Derecho ', 12,'V'),
        (49,'',13,'Permanente Canino Superior Derecho ', 13,'V'),
        (49,'',14,'Permanente Primer Premolar Superior Derecho ', 14,'V'),
        (49,'',15,'Permanente Segundo Premolar Superior Derecho ', 15,'V'),
        (49,'',16,'Permanente Primer Molar Superior Derecho ', 16,'V'),
        (49,'',17,'Permanente Segundo Molar Superior Derecho ', 17,'V'),
        (49,'',18,'Permanente Tercer Molar Superior Derecho ', 18,'V'),
        (49,'',21,'Permanente Incisivo Central Superior Izquierdo ', 21,'V'),
        (49,'',22,'Permanente Incisivo Lateral Superior Izquierdo ', 22,'V'),
        (49,'',23,'Permanente Canino Superior Izquierdo ', 23,'V'),
        (49,'',24,'Permanente Primer Premolar Superior Izquierdo ', 24,'V'),
        (49,'',25,'Permanente Segundo Premolar Superior Izquierdo ', 25,'V'),
        (49,'',26,'Permanente Primer Molar Superior Izquierdo ', 26,'V'),
        (49,'',27,'Permanente Segundo Molar Superior Izquierdo ', 27,'V'),
        (49,'',28,'Permanente Tercer Molar Superior Izquierdo ', 28,'V'),
        (49,'',31,'Permanente Incisivo Central Inferior Izquierdo ', 31,'V'),
        (49,'',32,'Permanente Incisivo Lateral Inferior Izquierdo ', 32,'V'),
        (49,'',33,'Permanente Canino Inferior Izquierdo ', 33,'V'),
        (49,'',34,'Permanente Primer Premolar Inferior Izquierdo ', 34,'V'),
        (49,'',35,'Permanente Segundo Premolar Inferior Izquierdo ', 35,'V'),
        (49,'',36,'Permanente Primer Molar Inferior Izquierdo ', 36,'V'),
        (49,'',37,'Permanente Segundo Molar Inferior Izquierdo ', 37,'V'),
        (49,'',38,'Permanente Tercer Molar Inferior Izquierdo ', 38,'V'),
        (49,'',41,'Permanente Incisivo Central Inferior Derecho ', 41,'V'),
        (49,'',42,'Permanente Incisivo Lateral Inferior Derecho ', 42,'V'),
        (49,'',43,'Permanente Canino Inferior Derecho ', 43,'V'),
        (49,'',44,'Permanente Primer Premolar Inferior Derecho ', 44,'V'),
        (49,'',45,'Permanente Segundo Premolar Inferior Derecho ', 45,'V'),
        (49,'',46,'Permanente Primer Molar Inferior Derecho ', 46,'V'),
        (49,'',47,'Permanente Segundo Molar Inferior Derecho ', 47,'V'),
        (49,'',48,'Permanente Tercer Molar Inferior Derecho ', 48,'V'),
        (49,'',51,'Temporario Incisivo Central Superior Derecho ', 51,'V'),
        (49,'',52,'Temporario Incisivo Lateral Superior Derecho ', 52,'V'),
        (49,'',53,'Temporario Canino Superior Derecho ', 53,'V'),
        (49,'',54,'Temporario Primer Molar Superior Derecho ', 54,'V'),
        (49,'',55,'Temporario Segundo Molar Superior Derecho ', 55,'V'),
        (49,'',61,'Temporario Incisivo Central Superior Izquierdo ', 61,'V'),
        (49,'',62,'Temporario Incisivo Lateral Superior Izquierdo ', 62,'V'),
        (49,'',63,'Temporario Canino Superior Izquierdo ', 63,'V'),
        (49,'',64,'Temporario Primer Molar Superior Izquierdo ', 64,'V'),
        (49,'',65,'Temporario Segundo Molar Superior Izquierdo ', 65,'V'),
        (49,'',71,'Temporario Incisivo Central Inferior Izquierdo ', 71,'V'),
        (49,'',72,'Temporario Incisivo Lateral Inferior Izquierdo ', 72,'V'),
        (49,'',73,'Temporario Canino Inferior Izquierdo ', 73,'V'),
        (49,'',74,'Temporario Primer Molar Inferior Izquierdo ', 74,'V'),
        (49,'',75,'Temporario Segundo Molar Inferior Izquierdo ', 75,'V'),
        (49,'',81,'Temporario Incisivo Central Inferior Derecho ', 81,'V'),
        (49,'',82,'Temporario Incisivo Lateral Inferior Derecho ', 82,'V'),
        (49,'',83,'Temporario Canino Inferior Derecho ', 83,'V'),
        (49,'',84,'Temporario Primer Molar Inferior Derecho ', 84,'V'),
        (49,'',85,'Temporario Segundo Molar Inferior Derecho ', 85,'V'),
        (50,'',1,'Mujer Control En Las 48 Hrs Siguientes Al Parto ', 1,'V'),
        (50,'',2,'Mujer Con Control Despues De Las 48 Hrs Siguientes Al Parto Hasta Los 7 Dias ', 2,'V'),
        (51,'',1,'Dentro ', 1,'V'),
        (51,'',2,'Fuera ', 2,'V'),
        (52,'',1,'Pacientes Referidos Recibidos Por El Establecimiento ', 1,'V'),
        (52,'',2,'Pacientes Referidos A Otros Establecimientos ', 2,'V'),
        (52,'',3,'Pcd Referidas A Unidades De Calificación De Discapacidad. ', 3,'V'),
        (52,'',4,'Pacientes Contrareferidos Al Establecimiento ', 4,'V'),
        (52,'',5,'Pacientes Referidos De La Comunidad O Medicina Tradicional ', 5,'V'),
        (52,'',6,'Pacientes Referidos A La Medicina Tradicional ', 6,'V'),
        (52,'',7,'Pdc Referidos A Servicios/Centros De Rehabilitacion ', 7,'V'),
        (53,'',1,'Materna ', 1,'V'),
        (53,'',2,'Muerte Fetal (Obito) ', 2,'V'),
        (53,'',3,'Muerte Neonatal Temprana (0-6 Días) ', 3,'V'),
        (54,'',1,'Amalgama ', 1,'V'),
        (54,'',2,'Resina ', 2,'V'),
        (54,'',3,'Ionómero De Vidrio Obturación ', 3,'V'),
        (54,'',4,'Prat - Tra ', 4,'V'),
        (55,'',1,'En Servicio ', 1,'V'),
        (55,'',2,'En Domicilio ', 2,'V'),
        (56,'',1,'En Servicio ', 1,'V'),
        (56,'',2,'En Domicilio ', 2,'V'),
        (57,'',1,'En Servicio ', 1,'V'),
        (57,'',2,'En Domicilio ', 2,'V'),
        (58,'',1,'Dentro ', 1,'V'),
        (58,'',2,'Fuera ', 2,'V'),
        (59,'',1,'Vivo ', 1,'V'),
        (59,'',2,'Muerto ', 2,'V'),
        (60,'',1,'Talla Normal (Tn) ', 1,'V'),
        (60,'',2,'Talla Baja (Tb) ', 2,'V'),
        (61,'',1,'General ', 1,'V'),
        (61,'',2,'Regional ', 2,'V'),
        (62,'',1,'Profilaxis ', 1,'V'),
        (62,'',2,'Fluor Topico ', 2,'V'),
        (62,'',3,'Sellado De Fosas Y Fisuras ', 3,'V'),
        (62,'',4,'Aplicacion De Cariostatico ', 4,'V'),
        (63,'',1,'Vaginal ', 1,'V'),
        (63,'',2,'Cesarea ', 2,'V'),
        (64,'',1,'Alta Medica ', 1,'V'),
        (64,'',2,'Alta Solicitada ', 2,'V'),
        (64,'',3,'Fuga ', 3,'V'),
        (64,'',4,'Fallecido - Antes De48 Hrs ', 4,'V'),
        (64,'',5,'Fallecido - A Partir De 48 Hrs ', 5,'V'),
        (65,'',1,'Si ', 1,'V'),
        (65,'',2,'No ', 2,'V'),
        (66,'',0,'Falso/Verdadero ', 1,'V'),
        (66,'',1,'Numerico Suma ', 2,'V'),
        (66,'',2,'Fecha ', 3,'V'),
        (66,'',3,'Cie 10 ', 4,'V'),
        (66,'',4,'Descripciones ', 5,'V'),
        (66,'',5,'Numero Agrupa ', 6,'V'),
        (66,'',6,'Descripcion Corta ', 7,'V'),
        (66,'',7,'Hora ', 8,'V'),
        (66,'',8,'Mumerico Conteo ', 9,'V'),
        (66,'',9,'Medico ', 10,'V'),
        (66,'',10,'Enfermera ', 11,'V'),
        (66,'',11,'Internos Recidentes ', 12,'V'),
        (66,'',12,'Paramedicos ', 13,'V'),
        (66,'',13,'Profesional Externo ', 14,'V'),
        (66,'',15,'Lista Generica ', 15,'V'),
        (66,'',16,'Imagen ', 16,'V');


    """
    db.execute(text(consulta3))
    db.commit()

    grupo = db.query(Grupo).filter(Grupo.nombre_grupo == "depto").first()
    if not grupo:
        grupo = Grupo(
            nombre_grupo="hv_expedidoen",
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
              ('NP', 10, 'No Porta', 10),
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


def inicio_bd():
    db = next(leer_bd())

    configure_mappers()

    ModeloBase.metadata.create_all(bind=engine)
    ParametroBase.metadata.create_all(bind=engine)

    admin_rol = db.query(Rol).filter(Rol.nombre_rol == "Administrador").first()
    if not admin_rol:
        admin_rol = Rol(
            nombre_rol='Administrador',
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

    cs = db.query(Centro).filter(Centro.nombre_centro == "San José Natividad").first()
    if not cs:
        cs = Centro(
            codigo_snis=200061,
            nombre_centro="San José Natividad",
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
    """

    """

    db.close()


if __name__ == "__main__":
    # preparar_bd()
    inicio_bd()
    inicia_tablas()
