# -*- coding: utf-8 -*-

import sys
import os

# Agregamos el directorio raíz del proyecto al sys.path para que se pueda encontrar el módulo 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.componentes.siis1n.modelos.lista import Lista
from app.componentes.siis1n.modelos.grupo import Grupo
from app.componentes.siis1n.modelos.rol import Rol
from app.componentes.siis1n.modelos.empleado import Empleado
from app.componentes.siis1n.modelos.centro import Centro
from app.componentes.siis1n.modelos.usuario import Usuario
from app.componentes.siis1n.modelos.persona import Persona
from app.componentes.siis1n.modelos.prestacion import Prestacion
from app.componentes.siis1n.modelos.paciente import Paciente
from app.componentes.siis1n.modelos.turno import Turno
from app.componentes.siis1n.modelos.reserva import Reserva
from app.componentes.siis1n.modelos.consulta import Consulta
from app.componentes.siis1n.modelos.variables import Variables
from app.componentes.siis1n.modelos.base import ModeloBase, ParametroBase
from app.nucleo.configuracion import config
from app.nucleo.seguridad import generar_clave_encriptata
from app.nucleo.baseDatos import leer_bd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, configure_mappers
from sqlalchemy.sql import text
from datetime import date, datetime
import uuid
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
    consulta = r"""

    CREATE EXTENSION IF NOT EXISTS unaccent;

    do $$
    begin 
        if not exists (select 1 from pg_type where typname = 'dia_semana_enum') then 
            create type dia_semana_enum as enum('L','M','I','J','V','S','D');
        end if;
    end $$;

    do $$
    begin
        if not exists (select 1 from pg_type where typname = 'edad') then
            create type edad as (anio int4, mes int4, dia int4);
        end if;
    end $$;


    -- DROP FUNCTION public.buscar_empleado(text, int4, int4);

    CREATE OR REPLACE FUNCTION public.buscar_empleado(criterio text DEFAULT NULL::text, p_limit integer DEFAULT 20, p_offset integer DEFAULT 0)
    RETURNS TABLE(id_empleado integer, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, cargo character varying, profesion character varying, total_count bigint)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        aux TEXT[];
        base_query TEXT;
    BEGIN
        /* =========================
        Construcción de filtro base
        ========================= */
        IF criterio IS NULL THEN
            base_query := $$
                FROM public.persona p
                INNER JOIN public.empleado e ON p.id_persona = e.id_persona
                INNER JOIN public.lista l 
                    ON l.cod_numero = e.profesion 
                AND l.id_grupo = 67
                AND l.estado_reg = 'V'
                WHERE p.estado_reg = 'V'
                AND e.estado_reg = 'V'
                AND p.tipo = 'E'
                AND e.tipo_empleado = 'M'
            $$;

        ELSIF criterio ~ '^\d+$' THEN
            base_query := format($$
                FROM public.persona p
                INNER JOIN public.empleado e ON p.id_persona = e.id_persona
                INNER JOIN public.lista l 
                    ON l.cod_numero = e.profesion 
                AND l.id_grupo = 67
                AND l.estado_reg = 'V'
                WHERE p.estado_reg = 'V'
                AND e.estado_reg = 'V'
                AND p.tipo = 'E'
                AND e.tipo_empleado = 'M'
                AND p.ci LIKE '%%%s%%'
            $$, criterio);

        ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
            base_query := format($$
                FROM public.persona p
                INNER JOIN public.empleado e ON p.id_persona = e.id_persona
                INNER JOIN public.lista l 
                    ON l.cod_numero = e.profesion 
                AND l.id_grupo = 67
                AND l.estado_reg = 'V'
                WHERE p.estado_reg = 'V'
                AND e.estado_reg = 'V'
                AND p.tipo = 'E'
                AND e.tipo_empleado = 'M'
                AND p.fecha_nacimiento = CAST('%s' AS DATE)
            $$, criterio);

        ELSE
            aux := string_to_array(criterio, ' ');

            base_query := $$
                FROM public.persona p
                INNER JOIN public.empleado e ON p.id_persona = e.id_persona
                INNER JOIN public.lista l 
                    ON l.cod_numero = e.profesion 
                AND l.id_grupo = 67
                AND l.estado_reg = 'V'
                WHERE p.estado_reg = 'V'
                AND e.estado_reg = 'V'
                AND p.tipo = 'E'
                AND e.tipo_empleado = 'M'
                AND (
            $$ || CASE array_length(aux, 1)
                    WHEN 1 THEN
                        format(
                            'normalizar_cadena(p.paterno) LIKE ''%%%s%%''
                            OR normalizar_cadena(p.nombres) LIKE ''%%%s%%''',
                            normalizar_cadena(aux[1]),
                            normalizar_cadena(aux[1])
                        )
                    WHEN 2 THEN
                        format(
                            'normalizar_cadena(p.nombres) LIKE ''%%%s%%''
                            AND normalizar_cadena(p.paterno) LIKE ''%%%s%%''',
                            normalizar_cadena(aux[1]),
                            normalizar_cadena(aux[2])
                        )
                    WHEN 3 THEN
                        format(
                            'normalizar_cadena(p.nombres) LIKE ''%%%s%%''
                            AND normalizar_cadena(p.paterno) LIKE ''%%%s%%''
                            AND normalizar_cadena(p.materno) LIKE ''%%%s%%''',
                            normalizar_cadena(aux[1]),
                            normalizar_cadena(aux[2]),
                            normalizar_cadena(aux[3])
                        )
                    ELSE
                        format(
                            'normalizar_cadena(p.paterno) LIKE ''%%%s%%''',
                            normalizar_cadena(criterio)
                        )
                END || ')';
        END IF;

        /* =========================
        Query final con paginación
        ========================= */
        RETURN QUERY EXECUTE format($q$
            WITH total AS (
                SELECT COUNT(*) AS total_count
                %s
            )
            SELECT
                e.id_empleado,
                p.ci,
                p.paterno,
                p.materno,
                p.nombres,
                p.fecha_nacimiento,
                e.cargo,
                l.descripcion AS profesion,
                (SELECT total_count FROM total)
            %s
            ORDER BY p.paterno, p.materno, p.nombres
            LIMIT %s OFFSET %s
        $q$, base_query, base_query, p_limit, p_offset);

    END;
    $function$
    ;

    CREATE OR REPLACE FUNCTION public.buscar_empleados(criterio text DEFAULT NULL::text)
    RETURNS TABLE(id_persona text, id_empleado integer, tipo character, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, sexo character, direccion jsonb, telefono jsonb, correo jsonb, estado_reg character, usuario_reg character varying, ip_reg character varying)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        aux TEXT[];
    BEGIN
        -- Si criterio es NULL, retornar todos los registros activos
        IF criterio IS NULL THEN
            RETURN QUERY
            SELECT p.id_persona::text, e.id_empleado, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.empleado e ON p.id_persona = e.id_persona
            WHERE e.estado_reg = 'V';
        -- Búsqueda por cédula de identidad
        ELSIF criterio ~ '^\d+$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, e.id_empleado, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.empleado e ON p.id_persona = e.id_persona
            WHERE e.estado_reg = 'V' AND p.ci LIKE '%' || criterio || '%';
        -- Búsqueda por fecha de nacimiento
        ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, e.id_empleado, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.empleado e ON p.id_persona = e.id_persona
            WHERE e.estado_reg = 'V' AND p.fecha_nacimiento = CAST(criterio AS DATE);
        -- Búsqueda por nombres y apellidos
        ELSE
            aux := string_to_array(criterio, ' ');

            RETURN QUERY
            SELECT p.id_persona::text, e.id_empleado, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.empleado e ON p.id_persona = e.id_persona
            WHERE (
                CASE array_length(aux, 1)
                    WHEN 1 THEN normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[1]) || '%'
                    WHEN 2 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%'
                    WHEN 3 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[3]) || '%'
                    WHEN 4 THEN ((normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                OR normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[2]) || '%') 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[3]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[4]) || '%')
                    ELSE normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(criterio) || '%'
                END
            ) AND e.estado_reg = 'V';
        END IF;
    END;
    $function$
    ;



    CREATE OR REPLACE FUNCTION public.buscar_pacientes(criterio text DEFAULT NULL::text, p_limit integer DEFAULT 20, p_offset integer DEFAULT 0)
    RETURNS TABLE(id_paciente integer, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, edad text, sexo character, total_count bigint)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        aux TEXT[];
        base_query TEXT;
    BEGIN
        -- Construir consulta base según criterio
        IF criterio IS NULL THEN
            base_query := $$
                FROM public.persona p
                INNER JOIN public.paciente c ON p.id_persona = c.id_persona
                WHERE c.estado_reg = 'V'
            $$;
        ELSIF criterio ~ '^\d+$' THEN
            base_query := format($$
                FROM public.persona p
                INNER JOIN public.paciente c ON p.id_persona = c.id_persona
                WHERE c.estado_reg = 'V' AND p.ci LIKE '%%%s%%'
            $$, criterio);
        ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
            base_query := format($$
                FROM public.persona p
                INNER JOIN public.paciente c ON p.id_persona = c.id_persona
                WHERE c.estado_reg = 'V' AND p.fecha_nacimiento = CAST('%s' AS DATE)
            $$, criterio);
        ELSE
            aux := string_to_array(criterio, ' ');
            base_query := $$
                FROM public.persona p
                INNER JOIN public.paciente c ON p.id_persona = c.id_persona
                WHERE c.estado_reg = 'V' AND (
            $$ || CASE array_length(aux, 1)
                    WHEN 1 THEN format('normalizar_cadena(p.paterno) LIKE ''%%%s%%''', normalizar_cadena(aux[1]))
                    WHEN 2 THEN format('normalizar_cadena(p.nombres) LIKE ''%%%s%%'' AND normalizar_cadena(p.paterno) LIKE ''%%%s%%''', normalizar_cadena(aux[1]), normalizar_cadena(aux[2]))
                    WHEN 3 THEN format('normalizar_cadena(p.nombres) LIKE ''%%%s%%'' AND normalizar_cadena(p.paterno) LIKE ''%%%s%%'' AND normalizar_cadena(p.materno) LIKE ''%%%s%%''', normalizar_cadena(aux[1]), normalizar_cadena(aux[2]), normalizar_cadena(aux[3]))
                    WHEN 4 THEN format('((normalizar_cadena(p.nombres) LIKE ''%%%s%%'' OR normalizar_cadena(p.nombres) LIKE ''%%%s%%'') AND normalizar_cadena(p.paterno) LIKE ''%%%s%%'' AND normalizar_cadena(p.materno) LIKE ''%%%s%%'')',
                                        normalizar_cadena(aux[1]), normalizar_cadena(aux[2]), normalizar_cadena(aux[3]), normalizar_cadena(aux[4]))
                    ELSE format('normalizar_cadena(p.paterno) LIKE ''%%%s%%''', normalizar_cadena(criterio))
                END || ')';
        END IF;

        -- Retornar consulta con paginación y conteo total
        RETURN QUERY EXECUTE format($q$
            WITH total AS (
                SELECT COUNT(*) AS total_count %s
            )
            SELECT 
                c.id_paciente, p.ci, p.paterno, p.materno, 
                p.nombres, p.fecha_nacimiento, edad_a_texto(calcular_edad(p.fecha_nacimiento)) as edad, p.sexo,
                (SELECT total_count FROM total)
            %s
            ORDER BY p.paterno, p.materno, p.nombres
            LIMIT %s OFFSET %s
        $q$, base_query, base_query, p_limit, p_offset);
    END;
    $function$
    ;



    CREATE OR REPLACE FUNCTION public.buscar_pacientes(criterio text DEFAULT NULL::text)
    RETURNS TABLE(id_persona text, id_paciente integer, tipo character, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, sexo character, direccion jsonb, telefono jsonb, correo jsonb, estado_reg character, usuario_reg character varying, ip_reg character varying)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        aux TEXT[];
    BEGIN
        -- Si criterio es NULL, retornar todos los registros activos
        IF criterio IS NULL THEN
            RETURN QUERY
            SELECT p.id_persona::text, c.id_paciente, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, 
                p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.paciente c ON p.id_persona = c.id_persona
            WHERE c.estado_reg = 'V';
        -- Búsqueda por cédula de identidad
        ELSIF criterio ~ '^\d+$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, c.id_paciente, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.paciente c ON p.id_persona = c.id_persona
            WHERE c.estado_reg = 'V' AND p.ci LIKE '%' || criterio || '%';
        -- Búsqueda por fecha de nacimiento
        ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, c.id_paciente, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.paciente as c ON p.id_persona = c.id_persona
            WHERE c.estado_reg = 'V' AND p.fecha_nacimiento = CAST(criterio AS DATE);
        -- Búsqueda por nombres y apellidos
        ELSE
            aux := string_to_array(criterio, ' ');

            RETURN QUERY
            SELECT p.id_persona::text, c.id_paciente, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.direccion, p.telefono, p.correo, p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            INNER JOIN public.paciente c ON p.id_persona = c.id_persona
            WHERE (
                CASE array_length(aux, 1)
                    WHEN 1 THEN normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[1]) || '%'
                    WHEN 2 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%'
                    WHEN 3 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[3]) || '%'
                    WHEN 4 THEN ((normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                OR normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[2]) || '%') 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[3]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[4]) || '%')
                    ELSE normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(criterio) || '%'
                END
            ) AND c.estado_reg = 'V';
        END IF;
    END;
    $function$
    ;

    CREATE OR REPLACE FUNCTION public.buscar_pacientes_enf_por_usuario(nombre_usuario character varying, criterio character varying DEFAULT NULL::character varying, fecha date DEFAULT CURRENT_DATE)
    RETURNS TABLE(prestacion character varying, id_paciente integer, id_reserva integer, ci character varying, paterno character varying, materno character varying, nombres character varying, edad text, sexo character, fecha_reserva date, hora_reserva time without time zone)
    LANGUAGE plpgsql
    AS $function$
    declare 
        medico_id int;
        rol_id int;
        aux TEXT[];
    begin
        criterio := NULLIF(criterio, '');

        select u.id_empleado, u.id_rol into medico_id, rol_id
        from public.usuario u 
        where u.nombre_usuario = buscar_pacientes_enf_por_usuario.nombre_usuario
        and u.estado_reg = 'V';

        if (medico_id is null) or (rol_id is null) then
            return;
        end if;

        raise notice 'Criterio %', criterio;
        

        if criterio is null then
            raise notice 'criterio nulo';
            RETURN QUERY
                SELECT e.nombre_prestacion, p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                inner join prestacion e on t.id_prestacion = e.id_prestacion
                WHERE r.fecha_reserva = buscar_pacientes_enf_por_usuario.fecha
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E' --atendido en enfermeria 
                            when 3 then 'R' --atendido en caja
                            when 4 then 'E' --atendido en enfermeria
                            when 5 then 'V' --archivo creado vigente
                            else r.estado_reg
                        end ) 
                ORDER BY r.hora_reserva;
        -- Búsqueda por cédula de identidad
        elsif criterio ~ '^\d+$' then
            raise notice 'Criterio numeros'; 
            RETURN QUERY
                SELECT e.nombre_prestacion, p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                inner join prestacion e on t.id_prestacion = e.id_prestacion
                WHERE r.fecha_reserva = buscar_pacientes_enf_por_usuario.fecha and s.ci LIKE '%' || criterio || '%'
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E'  --atendido en enfermeria
                            when 3 then 'R'  --atendido en caja
                            when 4 then 'E'  --atendido en enfermeria
                            when 5 then 'V'  --archivo creado vigente
                            else r.estado_reg
                        end ) 
                ORDER BY r.hora_reserva;
        -- Búsqueda por fecha de nacimiento
        elsif criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' then
            raise notice 'fecha';
            return query
                SELECT e.nombre_prestacion, p.id_paciente,r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                inner join prestacion e on t.id_prestacion = e.id_prestacion
                WHERE r.fecha_reserva = buscar_pacientes_enf_por_usuario.fecha 
                    and s.fecha_nacimiento = CAST(criterio AS DATE)
                    and t.id_medico = medico_id
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E'  
                            when 3 then 'R'
                            when 4 then 'E'
                            when 5 then 'V'
                            else r.estado_reg
                        end )
                ORDER BY r.hora_reserva;
        else
            raise notice 'cadena de nombre';
            aux := string_to_array(criterio, ' ');
            raise notice 'aux %', buscar_pacientes_enf_por_usuario.fecha;
            return query
                SELECT e.nombre_prestacion, p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                inner join prestacion e on t.id_prestacion = e.id_prestacion
                WHERE (
                    CASE array_length(aux, 1)
                        WHEN 1 THEN normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[1]) || '%'
                        WHEN 2 THEN normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%'
                        WHEN 3 THEN normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%' 
                                    AND normalizar_cadena(s.materno) LIKE '%' || normalizar_cadena(aux[3]) || '%'
                        WHEN 4 THEN ((normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    OR normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[2]) || '%') 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[3]) || '%' 
                                    AND normalizar_cadena(s.materno) LIKE '%' || normalizar_cadena(aux[4]) || '%')
                        ELSE normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(criterio) || '%'
                    END
                )
            and r.fecha_reserva = buscar_pacientes_enf_por_usuario.fecha
            and r.estado_reg = (
                case rol_id 
                    when 2 then 'E'  
                    when 3 then 'R'
                    when 4 then 'E'
                    when 5 then 'V'
                    else r.estado_reg
                end ) 
            ORDER BY r.hora_reserva;


        end if;
    end;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.buscar_pacientes_por_usuario(nombre_usuario character varying, criterio character varying DEFAULT NULL::character varying, fecha date DEFAULT CURRENT_DATE)
    RETURNS TABLE(id_paciente integer, id_reserva integer, ci character varying, paterno character varying, materno character varying, nombres character varying, edad text, sexo character, fecha_reserva date, hora_reserva time without time zone)
    LANGUAGE plpgsql
    AS $function$
    declare 
        medico_id int;
        rol_id int;
        aux TEXT[];
    begin
        criterio := NULLIF(criterio, '');


        select u.id_empleado, u.id_rol into medico_id, rol_id
        from public.usuario u 
        where u.nombre_usuario = buscar_pacientes_por_usuario.nombre_usuario
        and u.estado_reg = 'V';

        if (medico_id is null) or (rol_id is null) then
            return;
        end if;
        
        if criterio is null then
            RETURN QUERY
                SELECT p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                WHERE r.fecha_reserva = buscar_pacientes_por_usuario.fecha
                    and t.id_medico = medico_id
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E'  
                            when 3 then 'R'
                            when 4 then 'E'
                            when 5 then 'V'
                            else r.estado_reg
                        end ) 
                ORDER BY r.hora_reserva;
        -- Búsqueda por cédula de identidad
        elsif criterio ~ '^\d+$' then
            RETURN QUERY
                SELECT p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                WHERE r.fecha_reserva = buscar_pacientes_por_usuario.fecha and s.ci LIKE '%' || criterio || '%'
                    and t.id_medico = medico_id
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E'  
                            when 3 then 'R'
                            when 4 then 'E'
                            when 5 then 'V'
                            else r.estado_reg
                        end ) 
                ORDER BY r.hora_reserva;
        -- Búsqueda por fecha de nacimiento
        elsif criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' then
            return query
                SELECT p.id_paciente,r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                WHERE r.fecha_reserva = buscar_pacientes_por_usuario.fecha 
                    and s.fecha_nacimiento = CAST(criterio AS DATE)
                    and t.id_medico = medico_id
                    and r.estado_reg = (
                        case rol_id 
                            when 2 then 'E'  
                            when 3 then 'R'
                            when 4 then 'E'
                            when 5 then 'V'
                            else r.estado_reg
                        end )
                ORDER BY r.hora_reserva;
        else

            aux := string_to_array(criterio, ' ');
            return query
                SELECT p.id_paciente, r.id_reserva, s.ci, s.paterno, s.materno, s.nombres,
                    public.edad_a_texto(public.calcular_edad(s.fecha_nacimiento)) AS edad,
                    s.sexo, r.fecha_reserva, r.hora_reserva
                FROM turno t
                INNER JOIN reserva r ON t.id_turno = r.id_turno
                INNER JOIN paciente p ON r.id_paciente = p.id_paciente
                INNER JOIN persona s ON p.id_persona = s.id_persona
                WHERE (
                    CASE array_length(aux, 1)
                        WHEN 1 THEN normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[1]) || '%'
                        WHEN 2 THEN normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%'
                        WHEN 3 THEN normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%' 
                                    AND normalizar_cadena(s.materno) LIKE '%' || normalizar_cadena(aux[3]) || '%'
                        WHEN 4 THEN ((normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                    OR normalizar_cadena(s.nombres) LIKE '%' || normalizar_cadena(aux[2]) || '%') 
                                    AND normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(aux[3]) || '%' 
                                    AND normalizar_cadena(s.materno) LIKE '%' || normalizar_cadena(aux[4]) || '%')
                        ELSE normalizar_cadena(s.paterno) LIKE '%' || normalizar_cadena(criterio) || '%'
                    END
                )
            and t.id_medico = medico_id 
            and r.estado_reg = (
                case rol_id 
                    when 2 then 'E'  
                    when 3 then 'R'
                    when 4 then 'E'
                    when 5 then 'V'
                    else r.estado_reg
                end ) 
            ORDER BY r.hora_reserva;


        end if;
    end;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.buscar_personas(criterio text DEFAULT NULL::text)
    RETURNS TABLE(id_persona text, tipo character, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, sexo character, estado_reg character, usuario_reg character varying, ip_reg character varying)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        aux TEXT[];
    BEGIN
        -- Si criterio es NULL, retornar todos los registros activos
        IF criterio IS NULL THEN
            RETURN QUERY
            SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            WHERE p.estado_reg = 'V';
        -- Búsqueda por cédula de identidad
        ELSIF criterio ~ '^\d+$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            WHERE p.estado_reg = 'V' AND p.ci LIKE '%' || criterio || '%';
        -- Búsqueda por fecha de nacimiento
        ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
            RETURN QUERY
            SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            WHERE p.estado_reg = 'V' AND p.fecha_nacimiento = CAST(criterio AS DATE);
        -- Búsqueda por nombres y apellidos
        ELSE
            aux := string_to_array(criterio, ' ');

            RETURN QUERY
            SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
                p.estado_reg, p.usuario_reg, p.ip_reg
            FROM public.persona p
            WHERE (
                CASE array_length(aux, 1)
                    WHEN 1 THEN normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[1]) || '%'
                    WHEN 2 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%'
                    WHEN 3 THEN normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[2]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[3]) || '%'
                    WHEN 4 THEN ((normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[1]) || '%' 
                                OR normalizar_cadena(p.nombres) LIKE '%' || normalizar_cadena(aux[2]) || '%') 
                                AND normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(aux[3]) || '%' 
                                AND normalizar_cadena(p.materno) LIKE '%' || normalizar_cadena(aux[4]) || '%')
                    ELSE normalizar_cadena(p.paterno) LIKE '%' || normalizar_cadena(criterio) || '%'
                END
            ) AND p.estado_reg = 'V';
        END IF;
    END;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.calcular_edad(fecha_nacimiento date)
    RETURNS edad
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        edad_resultado public.edad;
        anios INTEGER;
        meses INTEGER;
        dias INTEGER;
    BEGIN
        -- Calcular la diferencia en años, meses y días
        anios := DATE_PART('year', AGE(CURRENT_DATE, fecha_nacimiento));
        meses := DATE_PART('month', AGE(CURRENT_DATE, fecha_nacimiento));
        dias := DATE_PART('day', AGE(CURRENT_DATE, fecha_nacimiento));

        -- Asignar los valores al tipo compuesto edad
        edad_resultado.anio := anios;
        edad_resultado.mes := meses;
        edad_resultado.dia := dias;

        RETURN edad_resultado;
    END;
    $function$
    ;

    CREATE OR REPLACE FUNCTION public.edad_a_texto(edad edad)
    RETURNS text
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN edad.anio || ' años, ' || edad.mes || ' meses, ' || edad.dia || ' días';
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


    CREATE OR REPLACE FUNCTION public.fn_fechasturno(nombre_usuario character varying, fecha date DEFAULT CURRENT_DATE)
    RETURNS TABLE(id_turno integer, id_medico integer, dia_semana text, fecha_calendario date, hora_inicio time without time zone, hora_final time without time zone)
    LANGUAGE plpgsql
    AS $function$
    declare
        primer_dia date;
        ultimo_dia date;
        fecha_proc date;
        medico_id int;
        rol_id int;

        begin

            select u.id_empleado, u.id_rol into medico_id, rol_id
            from public.usuario u 
            where u.nombre_usuario = fn_fechasturno.nombre_usuario
            and u.estado_reg = 'V';

            if (medico_id is null) or (rol_id is null) then
                return;
            end if;
            
            if (date(fecha) = current_date) then
                fecha_proc := current_date;
            else
                fecha_proc := fecha;
            end if;

            select date_trunc('month', fecha_proc)::date, (date_trunc('month', fecha_proc) + interval '1 month' - interval '1 day')::date into primer_dia, ultimo_dia;

            return query
                SELECT 
                    t.id_turno,
                    t.id_medico,
                    case d.dia_valor :: text when 'D' then 'Domingo' when 'L' then 'Lúnes' when 'M' then 'Martes' when 'I' then 'Miércoles'
                                            when 'J' then 'Jueves' when 'V' then 'Viernes' when 'S' then 'Sabado' end as diaSemana,
                    fechas.dia::date AS fecha_calendario,
                    t.hora_inicio,
                    t.hora_final
                    --d.dia_valor AS dia_configurado,
                FROM public.turno t
                -- 1. Expandimos el array de días (L, M, I...) a filas individuales
                CROSS JOIN LATERAL unnest(t.dia_semana) AS d(dia_valor)
                -- 2. Generamos el rango de fechas para ese turno
                CROSS JOIN LATERAL generate_series(primer_dia, ultimo_dia, '1 day'::interval) AS fechas(dia)
                WHERE
                    fecha_proc between t.fecha_inicio and t.fecha_final 
                    and 
                        CASE d.dia_valor::text
                            WHEN 'D' THEN 0 -- Domingo
                            WHEN 'L' THEN 1 -- Lunes
                            WHEN 'M' THEN 2 -- Martes
                            WHEN 'I' THEN 3 -- Miércoles
                            WHEN 'J' THEN 4 -- Jueves
                            WHEN 'V' THEN 5 -- Viernes
                            WHEN 'S' THEN 6 -- Sábado
                        END = EXTRACT(DOW FROM fechas.dia) 
                    and t.id_medico = medico_id;
        end;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.fn_fechasturno(idmedico integer, fecha date DEFAULT CURRENT_DATE)
    RETURNS TABLE(id_turno integer, id_medico integer, dia_semana text, fecha_calendario date, hora_inicio time without time zone, hora_final time without time zone)
    LANGUAGE plpgsql
    AS $function$
    declare
        primer_dia date;
        ultimo_dia date;
        fecha_proc date;
        begin
            if (idMedico is null) then
                return;
            end if;
            
            if (date(fecha) = current_date) then
                fecha_proc := current_date;
            else
                fecha_proc := fecha;
            end if;

            select date_trunc('month', fecha_proc)::date, (date_trunc('month', fecha_proc) + interval '1 month' - interval '1 day')::date into primer_dia, ultimo_dia;

            return query
                SELECT 
                    t.id_turno,
                    t.id_medico,
                    case d.dia_valor :: text when 'D' then 'Domingo' when 'L' then 'Lúnes' when 'M' then 'Martes' when 'I' then 'Miércoles'
                                            when 'J' then 'Jueves' when 'V' then 'Viernes' when 'S' then 'Sabado' end as diaSemana,
                    fechas.dia::date AS fecha_calendario,
                    t.hora_inicio,
                    t.hora_final
                    --d.dia_valor AS dia_configurado,
                FROM public.turno t
                -- 1. Expandimos el array de días (L, M, I...) a filas individuales
                CROSS JOIN LATERAL unnest(t.dia_semana) AS d(dia_valor)
                -- 2. Generamos el rango de fechas para ese turno
                CROSS JOIN LATERAL generate_series(primer_dia, ultimo_dia, '1 day'::interval) AS fechas(dia)
                WHERE
                    fecha_proc between t.fecha_inicio and t.fecha_final 
                    and 
                        CASE d.dia_valor::text
                            WHEN 'D' THEN 0 -- Domingo
                            WHEN 'L' THEN 1 -- Lunes
                            WHEN 'M' THEN 2 -- Martes
                            WHEN 'I' THEN 3 -- Miércoles
                            WHEN 'J' THEN 4 -- Jueves
                            WHEN 'V' THEN 5 -- Viernes
                            WHEN 'S' THEN 6 -- Sábado
                        END = EXTRACT(DOW FROM fechas.dia) 
                    and t.id_medico = idMedico;
        end;
    $function$
    ;

    -- DROP FUNCTION public.fn_obtener_menu_por_rol(varchar);

    CREATE OR REPLACE FUNCTION public.fn_obtener_menu_por_rol(p_nombre_rol character varying)
    RETURNS TABLE(nombre_menu character varying, ruta character varying, icono character varying, orden integer, metodo character varying[])
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN QUERY
        SELECT 
            m.nombre_menu,
            m.ruta,
            m.icono,
            m.orden,
            rm.metodo
        FROM 
            public.rol r
            JOIN public.rol_menu rm ON r.id_rol = rm.id_rol
            JOIN public.menu m ON rm.id_menu = m.id_menu
        WHERE 
            r.nombre_rol = p_nombre_rol
            AND r.estado_reg = 'V'  -- Rol activo
            AND m.estado_reg = 'V'  -- Menú activo
            AND rm.estado_reg = 'V'  -- Relación activa
        ORDER BY 
            m.orden;
    END;
    $function$
    ;


    CREATE OR REPLACE FUNCTION public.fn_obtener_menu_por_usuario(p_nombre_usuario character varying)
    RETURNS TABLE(nombre_menu character varying, ruta character varying, icono character varying, orden integer, metodo character varying[])
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN QUERY
        SELECT 
            m.nombre_menu,
            m.ruta,
            m.icono,
            m.orden,
            rm.metodo
        FROM 
            public.rol r
            JOIN public.rol_menu rm ON r.id_rol = rm.id_rol
            JOIN public.menu m ON rm.id_menu = m.id_menu
            join public.usuario u on r.id_rol = u.id_rol
        WHERE 
            upper(u.nombre_usuario) like  '%' ||  upper(p_nombre_usuario) || '%'
            AND r.estado_reg = 'V'  -- Rol activo
            AND m.estado_reg = 'V'  -- Menú activo
            AND rm.estado_reg = 'V'  -- Relación activa
        ORDER BY 
            m.orden;
    END;
    $function$
    ;

    -- DROP FUNCTION public.fn_obtener_perfil_usuario(varchar);

    CREATE OR REPLACE FUNCTION public.fn_obtener_perfil_usuario(p_nombre_usuario character varying)
    RETURNS TABLE(nombre_completo text, nombre_centro character varying, nombre_rol character varying)
    LANGUAGE plpgsql
    AS $function$
    begin
            return query
            select CAST(coalesce(p.paterno, '') || ' ' || coalesce(p.materno, '') || ', ' || coalesce(p.nombres, '') AS TEXT) nombre_completo, 
            c.nombre_centro, r.nombre_rol  from usuario u 
                inner join empleado e on u.id_empleado = e.id_empleado 
                inner join persona p on e.id_persona = p.id_persona 
                inner join centro c on e.id_centro = c.id_centro 
                inner join rol r on u.id_rol = r.id_rol
            where upper(u.nombre_usuario) like '%' || upper(p_nombre_usuario) || '%'
                and u.estado_reg = 'V';
    end;
    $function$
    ;

    -- DROP FUNCTION public.fn_usuario(varchar);

    CREATE OR REPLACE FUNCTION public.fn_usuario(p_nombre_usuario character varying)
    RETURNS TABLE(nombre_usuario character varying, clave character varying, nombre_completo text, centro_salud character varying, id_centro integer, usuario_bd character varying, clave_bd character varying, direccion_bd character varying, puerto integer, nombre_rol character varying)
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN QUERY
        SELECT 
            u.nombre_usuario,
            u.clave, 
            coalesce(p.paterno, '') || ' ' || coalesce(p.materno, '') ||', ' || coalesce(p.nombres, '') as nombre_completo,
            c.nombre_centro AS centro_salud,
            c.id_centro,
            c.usuario as usuarbio_bd,
            c.clave as clave_bd,
            c.direccion as direccion_bd,
            c.puerto,
            r.nombre_rol as nombre_rol
        FROM usuario u
        INNER JOIN empleado e ON u.id_empleado = e.id_empleado
        inner join persona p on e.id_persona = p.id_persona 
        INNER JOIN centro c ON e.id_centro = c.id_centro
        inner join rol r on u.id_rol = r.id_rol
        WHERE u.nombre_usuario = p_nombre_usuario;
    END;
    $function$
    ;

    CREATE OR REPLACE FUNCTION public.normalizar_cadena(entrada text)
    RETURNS text
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        RETURN upper(translate(
            unaccent(entrada), 
            'áéíóúÁÉÍÓÚñÑ', 
            'aeiouAEIOUnN'
        ));
    END;
    $function$
    ;

    -- DROP FUNCTION public.obtener_lista_por_grupo(varchar);

    CREATE OR REPLACE FUNCTION public.obtener_lista_por_grupo(criterio character varying)
    RETURNS TABLE(codigo text, descripcion text)
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        v_tipo CHAR(1);
        v_id_grupo INT;
    BEGIN
        -- Buscar el grupo basado en el nombre_grupo
        SELECT g.tipo, g.id_grupo
        INTO v_tipo, v_id_grupo
        FROM public.grupo g
        WHERE g.nombre_grupo = criterio;

        -- Verificar si se encontraron registros
        IF v_tipo IS NOT NULL THEN
            IF v_tipo = 'N' THEN
                RETURN QUERY
                SELECT l.cod_numero::TEXT codigo, l.descripcion::TEXT descripcion  -- Conversión explícita
                FROM public.lista l
                WHERE l.id_grupo = v_id_grupo;
            ELSE
                RETURN QUERY
                SELECT l.cod_texto::TEXT codigo, l.descripcion::TEXT descripcion  -- Conversión explícita
                FROM public.lista l
                WHERE l.id_grupo = v_id_grupo;
            END IF;
        ELSE
            RAISE NOTICE 'No se encontraron registros en el grupo con el criterio dado.';
        END IF;
    END;
    $function$
    ;

    CREATE OR REPLACE FUNCTION public.unaccent(text)
    RETURNS text
    LANGUAGE c
    STABLE PARALLEL SAFE STRICT
    AS '$libdir/unaccent', $function$unaccent_dict$function$
    ;


    CREATE OR REPLACE FUNCTION public.unaccent(regdictionary, text)
    RETURNS text
    LANGUAGE c
    STABLE PARALLEL SAFE STRICT
    AS '$libdir/unaccent', $function$unaccent_dict$function$
    ;


    CREATE OR REPLACE FUNCTION public.unaccent_init(internal)
    RETURNS internal
    LANGUAGE c
    PARALLEL SAFE
    AS '$libdir/unaccent', $function$unaccent_init$function$
    ;



    CREATE OR REPLACE FUNCTION public.unaccent_lexize(internal, internal, internal, internal)
    RETURNS internal
    LANGUAGE c
    PARALLEL SAFE
    AS '$libdir/unaccent', $function$unaccent_lexize$function$
    ;

    -- DROP FUNCTION public.validate_reserva();

    CREATE OR REPLACE FUNCTION public.validate_reserva()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        -- Validate fecha_reserva
        IF NEW.fecha_reserva NOT BETWEEN (
            SELECT t.fecha_inicio FROM turno t WHERE t.id_turno = NEW.id_turno
        ) AND (
            SELECT t.fecha_final FROM turno t WHERE t.id_turno = NEW.id_turno
        ) THEN
            RAISE EXCEPTION 'Fecha de reserva fuera del rango del turno';
        END IF;

        -- Validate hora_reserva
        IF NEW.hora_reserva NOT BETWEEN (
            SELECT t.hora_inicio FROM turno t WHERE t.id_turno = NEW.id_turno
        ) AND (
            SELECT t.hora_final FROM turno t WHERE t.id_turno = NEW.id_turno
        ) THEN
            RAISE EXCEPTION 'Hora de reserva fuera del rango del turno';
        END IF;

        RETURN NEW;
    END;
    $function$
    ;
    

    




    """
    db.execute(text(consulta))
    db.commit()
    db.close()


def inicia_tablas():
    db = next(leer_bd())
    consulta = r""" 

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

    cons_inserta_roles = r"""

    insert into  public.rol (nombre_rol, descripcion, estado_reg, usuario_reg, ip_reg, fecha_reg) values 
        ('Administrador','Rol de administrador del sistema', 'V', 'eanavi', '127.0.0.1', '2025-05-27 02:35:54.886'),
        ('Enfermera', 'Rol con acceso a atenciones de enfermería y consultas', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        ('Odontologo', 'Rol con acceso a atenciones odontológicas y consultas', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        ('Medico','Rol con acceso a consultas y atenciones medicas', 'V', 'eanavi', '127.0.0.1', '2025-05-27 02:35:54.886'),
        ('Operador', 'Rol con acceso a la operacion del sistema', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00');


    insert into public.menu(id_menu_padre, nombre_menu, ruta, icono, orden, categoria, estado_reg, usuario_reg, ip_reg, fecha_reg) values
        (null, 'Inicio', '/inicio', 'fa fa-home', 1, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Pacientes', '/pacientes', 'fa fa-users', 1, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Consultas', '/consultas', 'fa fa-stethoscope', 2, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Reservas', '/reservas', 'fa fa-calendar', 3, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Turnos', '/turnos', 'fa fa-clock-o', 4, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Empleados', '/empleados', 'fa fa-user-md', 5, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Servicios', '/servicios', 'fa fa-cogs', 7, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Centro de Salud', '/centro', 'fa fa-hospital-o', 8, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Roles', '/roles', 'fa fa-shield', 9, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 'Menus', '/menus', 'fa fa-bars', 10, 'M', 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00');

    insert into rol_menu (id_rol, id_menu, metodo,  estado_reg, usuario_reg, ip_reg, fecha_reg) values
        (1, 2, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 4, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'), 
        (1, 5, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 6, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 7, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 8, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (1, 9, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),  
        (1, 10, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (2, 2, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (2, 3, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (2, 5, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (3, 2, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (3, 3, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (3, 5, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (4, 2, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (4, 3, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (4, 5, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 2, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 4, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'), 
        (5, 5, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 6, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 7, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 8, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),
        (5, 9, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00'),  
        (5, 10, ARRAY['GET, POST, PUT, DELETE']::varchar[], 'V', 'eanavi', '127.0.0.1', '2025-04-29 00:00:00');
    """


    db.execute(text(cons_inserta_roles))
    db.commit()


    consulta2 = r"""

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
        (66,'se_tipo_dato','N','M','V'),
        (67, 't_especialidad', 'N', 'A', 'V'),
        (68, 'se_profesion', 'N', 'A', 'V'),
        (69, 'se_estado_civil', 'N', 'A', 'V'),
        (70, 'se_profesion2', 'N', 'A', 'V'),
        (71, 'se_nivel_estudio', 'N', 'A', 'V'),
        (72, 'se_idioma', 'N', 'A', 'V'),
        (73, 'se_idiomamaterno', 'N', 'A', 'V'),
        (74, 'se_autopertenencia', 'N', 'A', 'V');


        ALTER SEQUENCE public.grupo_id_grupo_seq
        RESTART 75;
    """

    db.execute(text(consulta2))
    db.commit()

    consulta3 = r"""

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
        (66,'',16,'Imagen ', 16,'V'),
        (67,'',24,'Medico General',1,'V'),
        (67,'',32,'Medico General-Mi Salud',2,'V'),
        (67,'',29,'Medico Mi Salud',3,'V'),
        (67,'',27,'Medico Bono Ja',4,'V'),
        (67,'',23,'Medico Especialista Cirujano',5,'V'),
        (67,'',21,'Medico Especialista Ginecologo',6,'V'),
        (67,'',22,'Medico Especialista Internista',7,'V'),
        (67,'',20,'Medico Especialista Pediatra',8,'V'),
        (67,'',35,'Medico Especialista Safci',9,'V'),
        (67,'',33,'Medico Especialista Safci-Mi Salud',10,'V'),
        (67,'',14,'Auxiliares En Enfermeria',11,'V'),
        (67,'',25,'Otro Medico Especialista',12,'V'),
        (67,'',16,'Auxiliares En Estadistica',13,'V'),
        (67,'',15,'Auxiliares En Laboratorio',14,'V'),
        (67,'',5,'Bioquimico(A) Farmaceuticos(As)',15,'V'),
        (67,'',18,'Conductores De Vehiculo',16,'V'),
        (67,'',6,'Educador En Salud',17,'V'),
        (67,'',2,'Enfermero(A)',18,'V'),
        (67,'',34,'Lavandera',19,'V'),
        (67,'',28,'Lic. Enfermeria',20,'V'),
        (67,'',3,'Nutricionista',21,'V'),
        (67,'',1,'Odontologo(A)',22,'V'),
        (67,'',30,'Odontologo(A) Movil',23,'V'),
        (67,'',26,'Otros Auxiliares',24,'V'),
        (67,'',7,'Otros Profesionales',25,'V'),
        (67,'',13,'Otros Tecnicos',26,'V'),
        (67,'',17,'Personal Administrativo',27,'V'),
        (67,'',31,'Tecnico En Imagenologia',28,'V'),
        (67,'',11,'Tecnicos En Estadistica',29,'V'),
        (67,'',12,'Tecnicos En Fisioterapia',30,'V'),
        (67,'',8,'Tecnicos En Laboratorio',31,'V'),
        (67,'',9,'Tecnicos En Rayos "X"',32,'V'),
        (67,'',10,'Tecnicos En Saneamiento Amb.',33,'V'),
        (67,'',19,'Trabajador Manual',34,'V'),
        (67,'',4,'Trabajadora Social',35,'V'),
        (68,'',17,'Administradores de empresas de hospedaje, expendio de comidas, comercio y otros servicios',1,'V'),
        (68,'',7,'Artesanas y operarios de oficios',2,'V'),
        (68,'',54,'Ayudantes de preparación de alimentos',3,'V'),
        (68,'',50,'Conductores de vehículos y operadores de equipos pesados móviles',4,'V'),
        (68,'',57,'Desocupado',5,'V'),
        (68,'',1,'Directivos y gobierno y empresas',6,'V'),
        (68,'',15,'Directores, gerentes y/o jefes de área',7,'V'),
        (68,'',34,'Empleados de contabilidad y registro de materiales',8,'V'),
        (68,'',32,'Empleados de oficina tipo administrativo',9,'V'),
        (68,'',4,'Empleados de oficina y afines',10,'V'),
        (68,'',33,'Empleados de trato directo con el público',11,'V'),
        (68,'',49,'Ensambladores',12,'V'),
        (68,'',13,'Estudiante',13,'V'),
        (68,'',10,'Fuerzas armadas',14,'V'),
        (68,'',16,'Gerentes de pequeñas y medianas empresas ',15,'V'),
        (68,'',58,'Jubilado',16,'V'),
        (68,'',12,'Labores del hogar',17,'V'),
        (68,'',45,'Mecánicos de precisión, alfareros, artesanos, trabajadores de las artes gráficas y afines',18,'V'),
        (68,'',14,'Miembros del poder ejecutivo, legislativo, judicial, y demás personal de la adm pública y empresas',19,'V'),
        (68,'',59,'No corresponde',20,'V'),
        (68,'',48,'Operadores de instalaciones fijas y afines',21,'V'),
        (68,'',8,'Operarios de maquinas e instalaciones',22,'V'),
        (68,'',35,'Otro personal de apoyo administrativo',23,'V'),
        (68,'',26,'Otros miembros de las fuerzas armadas',24,'V'),
        (68,'',25,'Otros profesionales',25,'V'),
        (68,'',52,'Peones agropecuarios, forestales, pesqueros y afines',26,'V'),
        (68,'',53,'Peones de la minería, construcción, industria manufacturera y el transporte',27,'V'),
        (68,'',9,'Peones y trabajadores no calificados ',28,'V'),
        (68,'',39,'Personal de los servicios de protección y seguridad',29,'V'),
        (68,'',22,'Profesionales ciencias económicas, financieras, políticas, sociales y culturales',30,'V'),
        (68,'',2,'Profesionales científicos intelectuales',31,'V'),
        (68,'',21,'Profesionales de la enseñanza',32,'V'),
        (68,'',19,'Profesionales de las ciencias puras, naturales, geológicas, arquitectura e ingeniería',33,'V'),
        (68,'',23,'Profesionales de tecnología de la información y las comunicaciones (tic)',34,'V'),
        (68,'',24,'Profesionales del derecho, ciencias humanísticas y sociales',35,'V'),
        (68,'',20,'Profesionales en medicina y salud',36,'V'),
        (68,'',56,'Recolectores de desechos y otras ocupaciones de no calificados',37,'V'),
        (68,'',11,'Sin especificar',38,'V'),
        (68,'',18,'Suboficiales de las fuerzas armadas',39,'V'),
        (68,'',31,'Técnicos de la tecnología de la información y las comunicaciones',40,'V'),
        (68,'',27,'Técnicos de nivel medio de las ciencias puras, naturales, geológicas, arquitectura e ingeniería',41,'V'),
        (68,'',28,'Técnicos de nivel medio en medicina y salud',42,'V'),
        (68,'',30,'Técnicos de servicios jurídicos, sociales, culturales y afines',43,'V'),
        (68,'',29,'Técnicos en operaciones financieras y administrativas',44,'V'),
        (68,'',3,'Técnicos y profesionales de nivel medio ',45,'V'),
        (68,'',6,'Trab. Agrícolas, forestales y afines',46,'V'),
        (68,'',5,'Trab. De servicios, vendedores y afines',47,'V'),
        (68,'',51,'Trabajadoras del hogar, limpiadores de edificaciones y lavadores',48,'V'),
        (68,'',40,'Trabajadores agrícolas, pecuarios, agropecuarios con producción destinada al mercado',49,'V'),
        (68,'',42,'Trabajadores agrícolas, pecuarios, agropecuarios, pescadores, cazadores y recolectores',50,'V'),
        (68,'',43,'Trabajadores de la construcción',51,'V'),
        (68,'',44,'Trabajadores de la metalurgia, construcción mecánica y afines',52,'V'),
        (68,'',38,'Trabajadores de los cuidados personales',53,'V'),
        (68,'',36,'Trabajadores de los servicios personales, protección y seguridad',54,'V'),
        (68,'',46,'Trabajadores especializados en electricidad y la electro tecnología',55,'V'),
        (68,'',41,'Trabajadores forestales calificados, cazadores y pescadores',56,'V'),
        (68,'',47,'Trabajadores industria alimentos, tratamiento madera, textiles, confección, cuero y otros oficios',57,'V'),
        (68,'',55,'Vendedores ambulantes de servicios y afines',58,'V'),
        (68,'',37,'Vendedores, demostradores y modelos',59,'V'),
        (69,'',2,'CASADO(A)',1,'V'),
        (69,'',6,'CONCUBINO(A) O UNION LIBRE',2,'V'),
        (69,'',3,'DIVORCIADO(A)',3,'V'),
        (69,'',1,'SOLTERO(A)',4,'V'),
        (69,'',5,'UNION LIBRE',5,'V'),
        (69,'',4,'VIUDO(A)',6,'V'),
        (70,'',1,'Abogada(o)',1,'V'),
        (70,'',2,'Agrónoma(o)',2,'V'),
        (70,'',3,'Agropecuaria(o)',3,'V'),
        (70,'',4,'Antropóloga(o)',4,'V'),
        (70,'',5,'Arqueóloga(o)',5,'V'),
        (70,'',6,'Arquitecta(o)',6,'V'),
        (70,'',7,'Artes Musicales y Dramáticas',7,'V'),
        (70,'',8,'Artes Plásticas ',8,'V'),
        (70,'',9,'Astrofísica(o)',9,'V'),
        (70,'',10,'Astróloga(o)',10,'V'),
        (70,'',11,'Astrónoma(o)',11,'V'),
        (70,'',12,'Atleta',12,'V'),
        (70,'',13,'Auditor(a)',13,'V'),
        (70,'',14,'Auxiliar de Enfermería ',14,'V'),
        (70,'',15,'Azafata(o)',15,'V'),
        (70,'',16,'Bibliotecología y Cs. Información',16,'V'),
        (70,'',17,'Biofísica(o)',17,'V'),
        (70,'',18,'Biógrafa(o)',18,'V'),
        (70,'',19,'Bióloga(o)',19,'V'),
        (70,'',20,'Bioquímica(o)',20,'V'),
        (70,'',21,'Botánica(o)',21,'V'),
        (70,'',22,'Cartógrafa(o)',22,'V'),
        (70,'',23,'Chef/Cocinera(o)',23,'V'),
        (70,'',24,'Climatóloga(o)',24,'V'),
        (70,'',25,'Constructor(a) Civil',25,'V'),
        (70,'',26,'Contador(a) Pública',26,'V'),
        (70,'',27,'Cosmógrafa(o) y Cosmologa(o)',27,'V'),
        (70,'',28,'Demógrafa(o)',28,'V'),
        (70,'',29,'Ecóloga(o)',29,'V'),
        (70,'',30,'Economista',30,'V'),
        (70,'',31,'Electromecánico',31,'V'),
        (70,'',32,'Electrónica y Telecomunicaciones',32,'V'),
        (70,'',34,'Estadística(o)',33,'V'),
        (70,'',35,'Farmacéutica(o)',34,'V'),
        (70,'',36,'Filósofa(o)',35,'V'),
        (70,'',37,'Física(o)',36,'V'),
        (70,'',38,'Fisioterapeuta',37,'V'),
        (70,'',39,'Fotógrafa(o)',38,'V'),
        (70,'',40,'Geógrafa(o)',39,'V'),
        (70,'',41,'Geóloga(o)',40,'V'),
        (70,'',42,'Informática(o)',41,'V'),
        (70,'',43,'Ing. Metalurgica y Materiales',42,'V'),
        (70,'',44,'Ing. Petrolera(o)',43,'V'),
        (70,'',45,'Ing. Quimica(o)',44,'V'),
        (70,'',46,'Ingeniera(o) Agroindustrial ',45,'V'),
        (70,'',52,'Ingeniera(o) Civil',46,'V'),
        (70,'',84,'Ingeniera(o) Comercial ',47,'V'),
        (70,'',47,'Ingeniera(o) de Procesos de Mat. Primas Min. ',48,'V'),
        (70,'',53,'Ingeniera(o) de Sistemas ',49,'V'),
        (70,'',48,'Ingeniera(o) del Medio Ambiente ',50,'V'),
        (70,'',54,'Ingeniera(o) Electrónico',51,'V'),
        (70,'',49,'Ingeniera(o) en Desarrollo Rural ',52,'V'),
        (70,'',50,'Ingeniera(o) Mecatrónica ',53,'V'),
        (70,'',51,'Ingeniera(o) Minera',54,'V'),
        (70,'',33,'Lic. Enfermería',55,'V'),
        (70,'',55,'Lingüística e Idiomas',56,'V'),
        (70,'',56,'Literata(o)',57,'V'),
        (70,'',57,'Matemática(o)',58,'V'),
        (70,'',58,'Mecánica(o) Automotriz',59,'V'),
        (70,'',59,'Mecánica(o) de Aviación',60,'V'),
        (70,'',60,'Mecánica(o) Industrial',61,'V'),
        (70,'',62,'Médico Especialista',62,'V'),
        (70,'',61,'Medico General',63,'V'),
        (70,'',63,'Meteoróloga',64,'V'),
        (70,'',64,'Nutriciónista y Dietética ',65,'V'),
        (70,'',65,'Odontóloga(o)',66,'V'),
        (70,'',66,'Oficial de Policia',67,'V'),
        (70,'',67,'Oficial Militar/Naval/Aeronautico',68,'V'),
        (70,'',68,'Pedagoga(o)',69,'V'),
        (70,'',69,'Periodista',70,'V'),
        (70,'',70,'Piloto ',71,'V'),
        (70,'',71,'Polítologo',72,'V'),
        (70,'',72,'Profesor(a)',73,'V'),
        (70,'',73,'Psicóloga(o)',74,'V'),
        (70,'',74,'Publicista',75,'V'),
        (70,'',75,'Química(o) Farmacéutica(o)',76,'V'),
        (70,'',76,'Química(o) Industrial(o)',77,'V'),
        (70,'',77,'Radióloga(o)',78,'V'),
        (70,'',78,'Secretaria(o)',79,'V'),
        (70,'',85,'SIN PROFESIÓN',80,'V'),
        (70,'',79,'Socióloga(o)',81,'V'),
        (70,'',80,'Topógrafa(o) y Geodesia',82,'V'),
        (70,'',81,'Trabajador(a) Social',83,'V'),
        (70,'',82,'Turismo',84,'V'),
        (70,'',83,'Veterinaria(o)/Zoóloga(o)',85,'V'),
        (71,'',1,'a) Ninguno',1,'V'),
        (71,'',2,'b) Primaria Concluida',2,'V'),
        (71,'',11,'c) Primaria sin concluir',3,'V'),
        (71,'',3,'d) Secundaria Concluida',4,'V'),
        (71,'',12,'e) Secundaria sin Concluir',5,'V'),
        (71,'',5,'f) Bachiller',6,'V'),
        (71,'',6,'g) Técnico Medio',7,'V'),
        (71,'',7,'h) Técnico Superior',8,'V'),
        (71,'',4,'i) Universitario',9,'V'),
        (71,'',8,'j) Egresado Universitario',10,'V'),
        (71,'',9,'k) Licenciatura',11,'V'),
        (71,'',10,'l) Alfabeta',12,'V'),
        (71,'',13,'m) No corresponde',13,'V'),
        (71,'',14,'n) Postgrado',14,'V'),
        (71,'',15,'o) Analfabeta',15,'V'),
        (72,'',2,'Aymara',2,'V'),
        (72,'',43,'Ayoreo-Zamuco',3,'V'),
        (72,'',11,'Baure',4,'V'),
        (72,'',14,'Canichana',5,'V'),
        (72,'',1,'Castellano',6,'V'),
        (72,'',15,'Cavineño',7,'V'),
        (72,'',16,'Cayubaba',8,'V'),
        (72,'',17,'Chácobo',9,'V'),
        (72,'',18,'Chimán',10,'V'),
        (72,'',12,'Chiquitano-bésiro',11,'V'),
        (72,'',19,'Ese ejja',12,'V'),
        (72,'',6,'Extranjero',13,'V'),
        (72,'',4,'Guaraní',14,'V'),
        (72,'',20,'Guarasuawe',15,'V'),
        (72,'',21,'Guarayo',16,'V'),
        (72,'',22,'Itonama',17,'V'),
        (72,'',23,'Leco',18,'V'),
        (72,'',24,'Machajuyai-kallawaya',19,'V'),
        (72,'',25,'Machineri',20,'V'),
        (72,'',26,'Maropa',21,'V'),
        (72,'',13,'Mojeño ',22,'V'),
        (72,'',28,'Mojeño-ignaciano',23,'V'),
        (72,'',27,'Mojeño-trinitario',24,'V'),
        (72,'',29,'Moré',25,'V'),
        (72,'',30,'Mosetén',26,'V'),
        (72,'',31,'Movima',27,'V'),
        (72,'',8,'Nativo y Castellano',28,'V'),
        (72,'',5,'Otro nativo',29,'V'),
        (72,'',32,'Pacawara',30,'V'),
        (72,'',33,'Puquina',31,'V'),
        (72,'',3,'Quechua',32,'V'),
        (72,'',44,'Sin especificar',33,'V'),
        (72,'',34,'Sirionó',34,'V'),
        (72,'',9,'Sólo Castellano',35,'V'),
        (72,'',7,'Sólo nativo',36,'V'),
        (72,'',35,'Tacana',37,'V'),
        (72,'',36,'Tapiete',38,'V'),
        (72,'',37,'Toromona',39,'V'),
        (72,'',38,'Uruchipaya',40,'V'),
        (72,'',39,'Weenhayek',41,'V'),
        (72,'',40,'Yaminawa',42,'V'),
        (72,'',41,'Yuki',43,'V'),
        (72,'',42,'Yuracaré',44,'V'),
        (73,'',7,'Araona',1,'V'),
        (73,'',2,'Aymara',2,'V'),
        (73,'',40,'Ayoreo-Zamuco',3,'V'),
        (73,'',8,'Baure',4,'V'),
        (73,'',11,'Canichana',5,'V'),
        (73,'',1,'Castellano',6,'V'),
        (73,'',12,'Cavineño',7,'V'),
        (73,'',13,'Cayubaba',8,'V'),
        (73,'',14,'Chácobo',9,'V'),
        (73,'',15,'Chimán',10,'V'),
        (73,'',9,'Chiquitano-bésiro',11,'V'),
        (73,'',16,'Ese ejja',12,'V'),
        (73,'',6,'Extranjero',13,'V'),
        (73,'',4,'Guaraní',14,'V'),
        (73,'',17,'Guarasuawe',15,'V'),
        (73,'',18,'Guarayo',16,'V'),
        (73,'',19,'Itonama',17,'V'),
        (73,'',20,'Leco',18,'V'),
        (73,'',21,'Machajuyai-kallawaya',19,'V'),
        (73,'',22,'Machineri',20,'V'),
        (73,'',23,'Maropa',21,'V'),
        (73,'',10,'Mojeño ',22,'V'),
        (73,'',25,'Mojeño-ignaciano',23,'V'),
        (73,'',24,'Mojeño-trinitario',24,'V'),
        (73,'',26,'Moré',25,'V'),
        (73,'',27,'Mosetén',26,'V'),
        (73,'',28,'Movima',27,'V'),
        (73,'',5,'Otro nativo',28,'V'),
        (73,'',29,'Pacawara',29,'V'),
        (73,'',30,'Puquina',30,'V'),
        (73,'',3,'Quechua',31,'V'),
        (73,'',41,'Sin especificar',32,'V'),
        (73,'',31,'Sirionó',33,'V'),
        (73,'',32,'Tacana',34,'V'),
        (73,'',33,'Tapiete',35,'V'),
        (73,'',34,'Toromona',36,'V'),
        (73,'',35,'Uruchipaya',37,'V'),
        (73,'',36,'Weenhayek',38,'V'),
        (73,'',37,'Yaminawa',39,'V'),
        (73,'',38,'Yuki',40,'V'),
        (73,'',39,'Yuracaré',41,'V'),
        (74,'',8,'Araona',1,'V'),
        (74,'',2,'Aymara',2,'V'),
        (74,'',9,'Ayoreo,zamuco',3,'V'),
        (74,'',10,'Baure',4,'V'),
        (74,'',11,'Canichana',5,'V'),
        (74,'',12,'Cavineño',6,'V'),
        (74,'',13,'Cayubaba',7,'V'),
        (74,'',14,'Chácobo',8,'V'),
        (74,'',15,'Chimán,tsimané',9,'V'),
        (74,'',4,'Chiquitano',10,'V'),
        (74,'',16,'Chiquitano,bésiro,napeca,paunaca,moncoca',11,'V'),
        (74,'',17,'Ese ejja,chama',12,'V'),
        (74,'',3,'Guaraní',13,'V'),
        (74,'',18,'Guarayo',14,'V'),
        (74,'',19,'Itonama',15,'V'),
        (74,'',20,'Joaquiniano',16,'V'),
        (74,'',21,'Leco',17,'V'),
        (74,'',22,'Machineri,yine',18,'V'),
        (74,'',5,'Mojeño',19,'V'),
        (74,'',25,'Mojeño (javierano,loretano,otro,sin especificar)',20,'V'),
        (74,'',23,'Mojeño ignaciano',21,'V'),
        (74,'',24,'Mojeño trinitario',22,'V'),
        (74,'',26,'Moré',23,'V'),
        (74,'',27,'Moseten',24,'V'),
        (74,'',28,'Movima',25,'V'),
        (74,'',7,'Ninguno',26,'V'),
        (74,'',6,'Otro nativo',27,'V'),
        (74,'',29,'Pacahuara',28,'V'),
        (74,'',1,'Quechua',29,'V'),
        (74,'',30,'Reyesano,maropa',30,'V'),
        (74,'',39,'Sin especificar',31,'V'),
        (74,'',31,'Sirionó',32,'V'),
        (74,'',32,'Takana',33,'V'),
        (74,'',33,'Tapieté',34,'V'),
        (74,'',34,'Uru (chipaya,iru-ito,murato,pukina)',35,'V'),
        (74,'',35,'Weenhayek,mataco',36,'V'),
        (74,'',36,'Yaminahua',37,'V'),
        (74,'',37,'Yuki',38,'V'),
        (74,'',38,'Yurakaré',39,'V');
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
            direccion=[{"tipo": "personal", "direccion": {"zona": "San Jose Obrero, Alto Koani", "calle": "Calle B", "ciudad": "La Paz", "numero": "341"}}],
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

    

def continua_bd():
    db = next(leer_bd())

    cs = db.query(Centro).filter(Centro.nombre_centro == "San José Natividad").first()

    persona2 = db.query(Persona).filter(Persona.ci == "1234567").first()
    if not persona2:
        persona2 = Persona(
            id_persona=uuid.uuid4(),
            tipo="E",
            ci="1234567",
            paterno="Perez",
            materno="Lopez",
            nombres="Juan Carlos",
            fecha_nacimiento=date(1990, 1, 1),
            sexo="M",
            direccion=[{"tipo": "personal", "direccion": {"zona": "Zona Central", "calle": "Calle A", "ciudad": "La Paz", "numero": "123"}}],
            telefono={"celular": "61234567", "fijo": "987654321"},
            correo={"personal": "jcperez@gmail.com",
                    "trabajo": "jcperez@sanjose.com"},
            usuario_reg="eanavi",  
            ip_reg="127.0.0.1",
        )
        db.add(persona2)
        db.commit()
    
    per = db.query(Persona).filter(Persona.ci == "7852412").first()
    if not per:
        per = Persona(
            id_persona=uuid.uuid4(),
            tipo="E",
            ci="7852412",
            paterno="Lopez",
            materno="Gomez",
            nombres="Maria Elena",
            fecha_nacimiento=date(1985, 5, 20),
            sexo="F",
            direccion=[{"tipo": "personal", "direccion": {"zona": "Zona Sur", "calle": "Calle C", "ciudad": "La Paz", "numero": "456"}}],
            telefono={"celular": "61234567", "fijo": "987654321"},
            correo={"personal": "mlopez@gmail.com",
                    "trabajo": "mlopez@sanjose.com"},
            usuario_reg="eanavi",
            ip_reg="127.0.0.1",
        )
        db.add(per)
        db.commit()

    paciente = db.query(Paciente).filter(
        Paciente.id_persona == per.id_persona).first()
    if not paciente:
        paciente = Paciente(
            id_persona=per.id_persona,
            id_centro=cs.id_centro,
            tipo_sangre = "O+",
            estado_civil = 1,
            ocupacion = 32,
            nivel_estudios = 2,
            idioma_hablado = 1,
            idioma_materno = 1,
            autopertenencia = 1,
            usuario_reg="eanavi",
            ip_reg="127.0.0.1",
        )
        db.add(paciente)
        db.commit()
    
    empleado2 = db.query(Empleado).filter(
        Empleado.id_persona == persona2.id_persona).first()
    if not empleado2:
        empleado2 = Empleado(
            id_persona=persona2.id_persona,
            id_centro=cs.id_centro,
            tipo_empleado='M',
            profesion=24,
            registro_profesional='M-1368',
            cargo="Medico General",

            usuario_reg="eanavi",
            ip_reg="127.0.0.1"

        )
        db.add(empleado2)
        db.commit()

    usuario2 = db.query(Usuario).filter(
        Usuario.nombre_usuario == "jperez").first()
    if not usuario2:
        usuario2 = Usuario(
            id_empleado=empleado2.id_empleado,
            id_rol=2,
            nombre_usuario='jperez',
            clave=generar_clave_encriptata(persona2.ci),

            usuario_reg="eanavi",
            ip_reg="127.0.0.1",
        )
        db.add(usuario2)
        db.commit()   

    db.close()


if __name__ == "__main__":
    preparar_bd()
    configure_mappers()
    ModeloBase.metadata.create_all(bind=engine)
    ParametroBase.metadata.create_all(bind=engine)

    inicio_bd()
    inicia_tablas()
    continua_bd()
    
