create type edad as (
	anio integer, 
	mes integer, 
	dia integer
);


CREATE EXTENSION unaccent;

-- DROP FUNCTION public.buscar_personas(text);

CREATE OR REPLACE FUNCTION public.buscar_personas(criterio text)
 RETURNS TABLE(id_persona text, tipo character, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, sexo character, estado_reg character, usuario_reg character varying, ip_reg character varying)
 LANGUAGE plpgsql
AS $function$
DECLARE
    aux TEXT[];
BEGIN
    IF criterio ~ '^\d+$' THEN
        RETURN QUERY
        SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
               p.estado_reg, p.usuario_reg, p.ip_reg
        FROM public.persona p
        WHERE p.ci LIKE '%' || criterio || '%';
    ELSIF criterio ~ '^(0[1-9]|[12][0-9]|3[01])[-\/](0[1-9]|1[0-2])[-\/](\d{4})$' THEN
        RETURN QUERY
        SELECT p.id_persona::text, p.tipo, p.ci, p.paterno, p.materno, p.nombres, p.fecha_nacimiento, p.sexo,
               p.estado_reg, p.usuario_reg, p.ip_reg
        FROM public.persona p
        WHERE p.fecha_nacimiento = CAST(criterio AS DATE);
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
        );
    END IF;
END;
$function$
;

-- DROP FUNCTION public.calcular_edad_pg(date);

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


-- DROP FUNCTION public.es_dia_valido(int4, int4, int4);

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


-- DROP FUNCTION public.fn_usuario(varchar);

CREATE OR REPLACE FUNCTION public.fn_usuario(p_nombre_usuario character varying)
 RETURNS TABLE(nombre_usuario character varying, clave character varying, centro_salud character varying, id_centro integer, usuario character varying, clave_centro character varying, direccion character varying, puerto integer, nombre_rol character varying)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        u.nombre_usuario,
        u.clave,
        c.nombre AS centro_salud,
		c.id_centro,
        c.usuario,
        c.clave,
        c.direccion,
        c.puerto,
		r.nombre as nombre_rol
    FROM usuario u
    INNER JOIN empleado e ON u.id_empleado = e.id_empleado
    INNER JOIN centro c ON e.id_centro = c.id_centro
	inner join rol r on u.id_rol = r.id_rol
    WHERE u.nombre_usuario = p_nombre_usuario;
END;
$function$
;


CREATE OR REPLACE FUNCTION public.fn_nombre_usuario(p_nombre_usuario character varying)
 RETURNS TABLE(nombre_persona character varying, rol character varying, cargo character varying)
 LANGUAGE plpgsql
AS $function$
BEGIN
    select p.nombres, coalesce(p.paterno, '') || ' ' || coalesce(p.materno, '') || ', ' || coalesce(p.nombres ) as nombre_persona, r.nombre as nombre_rol, e.cargo 
	from persona as p 
		inner join empleado as e on p.id_persona = e.id_persona
		inner join usuario as u on e.id_empleado  = u.id_empleado
		inner join rol as r on u.id_rol = r.id_rol
	where u.nombre_usuario = p_nombre_usuario;
END;
$function$
;

-- DROP FUNCTION public.normalizar_cadena(text);

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
            SELECT l.cod_texto codigo, l.descripcion::TEXT descripcion  -- Conversión explícita
            FROM public.lista l
            WHERE l.id_grupo = v_id_grupo;
        END IF;
    ELSE
        RAISE NOTICE 'No se encontraron registros en el grupo con el criterio dado.';
    END IF;
END;
$function$
;


-- DROP FUNCTION public.fn_obtener_menu_por_rol(varchar);

CREATE OR REPLACE FUNCTION public.fn_obtener_menu_por_rol(
    p_nombre_rol varchar(60)
)
RETURNS TABLE (
    nombre_menu varchar(120),
    ruta varchar(255),
    icono varchar(50),
    orden int4,
    metodo varchar[]
)
LANGUAGE plpgsql
AS $$
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
$$;