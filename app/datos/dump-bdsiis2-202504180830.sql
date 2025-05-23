PGDMP     1                    }            bdsiis2    14.15    14.15 N    D           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            E           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            F           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            G           1262    16808    bdsiis2    DATABASE     c   CREATE DATABASE bdsiis2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Spanish_Spain.1252';
    DROP DATABASE bdsiis2;
                postgres    false            H           0    0    DATABASE bdsiis2    ACL     .   GRANT ALL ON DATABASE bdsiis2 TO bdsiis1nusr;
                   postgres    false    3399                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
                postgres    false            I           0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                   postgres    false    3            �            1255    17266    buscar_personas(text)    FUNCTION     �	  CREATE FUNCTION public.buscar_personas(criterio text) RETURNS TABLE(id_persona text, tipo character, ci character varying, paterno character varying, materno character varying, nombres character varying, fecha_nacimiento date, sexo character, estado_reg character, usuario_reg character varying, ip_reg character varying)
    LANGUAGE plpgsql
    AS $_$
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
$_$;
 5   DROP FUNCTION public.buscar_personas(criterio text);
       public          bdsiis1nusr    false    3            �            1255    17243    normalizar_cadena(text)    FUNCTION     �   CREATE FUNCTION public.normalizar_cadena(entrada text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN translate(
        unaccent(entrada), 
        'áéíóúÁÉÍÓÚñÑ', 
        'aeiouAEIOUnN'
    );
END;
$$;
 6   DROP FUNCTION public.normalizar_cadena(entrada text);
       public          bdsiis1nusr    false    3            �            1255    17321 *   obtener_lista_por_grupo(character varying)    FUNCTION     �  CREATE FUNCTION public.obtener_lista_por_grupo(criterio character varying) RETURNS TABLE(codigo text, descripcion text)
    LANGUAGE plpgsql
    AS $$
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
            SELECT l.cod_numero::TEXT, l.descripcion::TEXT  -- Conversión explícita
            FROM public.lista l
            WHERE l.id_grupo = v_id_grupo;
        ELSE
            RETURN QUERY
            SELECT l.cod_texto, l.descripcion::TEXT  -- Conversión explícita
            FROM public.lista l
            WHERE l.id_grupo = v_id_grupo;
        END IF;
    ELSE
        RAISE NOTICE 'No se encontraron registros en el grupo con el criterio dado.';
    END IF;
END;
$$;
 J   DROP FUNCTION public.obtener_lista_por_grupo(criterio character varying);
       public          bdsiis1nusr    false    3            �            1259    17196    centro    TABLE     �  CREATE TABLE public.centro (
    id_centro integer NOT NULL,
    codigo_snis integer NOT NULL,
    nombre character varying(120) NOT NULL,
    direccion character varying(40) NOT NULL,
    usuario character varying(40) NOT NULL,
    clave character varying(120) NOT NULL,
    puerto integer NOT NULL,
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.centro;
       public         heap    bdsiis1nusr    false    3            �            1259    17195    centro_id_centro_seq    SEQUENCE     �   CREATE SEQUENCE public.centro_id_centro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.centro_id_centro_seq;
       public          bdsiis1nusr    false    3    213            J           0    0    centro_id_centro_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.centro_id_centro_seq OWNED BY public.centro.id_centro;
          public          bdsiis1nusr    false    212            �            1259    17204    empleado    TABLE     y  CREATE TABLE public.empleado (
    id_empleado integer NOT NULL,
    id_persona uuid NOT NULL,
    tipo_empleado character(1),
    profesion integer NOT NULL,
    registro_profesional character varying(20),
    id_centro integer NOT NULL,
    cargo character varying(120),
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.empleado;
       public         heap    bdsiis1nusr    false    3            �            1259    17203    empleado_id_empleado_seq    SEQUENCE     �   CREATE SEQUENCE public.empleado_id_empleado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.empleado_id_empleado_seq;
       public          bdsiis1nusr    false    3    215            K           0    0    empleado_id_empleado_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.empleado_id_empleado_seq OWNED BY public.empleado.id_empleado;
          public          bdsiis1nusr    false    214            �            1259    17286    grupo    TABLE     �   CREATE TABLE public.grupo (
    id_grupo integer NOT NULL,
    nombre_grupo character varying(40),
    tipo character(1),
    area character(1)
);
    DROP TABLE public.grupo;
       public         heap    bdsiis1nusr    false    3            �            1259    17285    grupo_id_grupo_seq    SEQUENCE     �   CREATE SEQUENCE public.grupo_id_grupo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.grupo_id_grupo_seq;
       public          bdsiis1nusr    false    221    3            L           0    0    grupo_id_grupo_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.grupo_id_grupo_seq OWNED BY public.grupo.id_grupo;
          public          bdsiis1nusr    false    220            �            1259    17307    lista    TABLE     �   CREATE TABLE public.lista (
    id_lista integer NOT NULL,
    id_grupo integer NOT NULL,
    cod_texto character(3),
    cod_numero integer,
    descripcion character varying(120) NOT NULL,
    orden integer NOT NULL
);
    DROP TABLE public.lista;
       public         heap    bdsiis1nusr    false    3            �            1259    17306    lista_id_lista_seq    SEQUENCE     �   CREATE SEQUENCE public.lista_id_lista_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.lista_id_lista_seq;
       public          bdsiis1nusr    false    223    3            M           0    0    lista_id_lista_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.lista_id_lista_seq OWNED BY public.lista.id_lista;
          public          bdsiis1nusr    false    222            �            1259    17268    paciente    TABLE     #  CREATE TABLE public.paciente (
    id_paciente integer NOT NULL,
    id_persona uuid NOT NULL,
    id_centro integer NOT NULL,
    estado_civil character(2),
    ocupacion integer,
    nivel_estudios integer,
    mun_nacimiento integer NOT NULL,
    mun_residencia integer NOT NULL,
    idioma_hablado integer NOT NULL,
    idioma_materno integer NOT NULL,
    autopertenencia integer NOT NULL,
    gestion_comunitaria character varying(120),
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.paciente;
       public         heap    bdsiis1nusr    false    3            �            1259    17267    paciente_id_paciente_seq    SEQUENCE     �   CREATE SEQUENCE public.paciente_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.paciente_id_paciente_seq;
       public          bdsiis1nusr    false    3    219            N           0    0    paciente_id_paciente_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.paciente_id_paciente_seq OWNED BY public.paciente.id_paciente;
          public          bdsiis1nusr    false    218            �            1259    17178    persona    TABLE     �  CREATE TABLE public.persona (
    id_persona uuid NOT NULL,
    tipo character(1) NOT NULL,
    ci character varying(20),
    paterno character varying(60),
    materno character varying(60),
    nombres character varying(120) NOT NULL,
    fecha_nacimiento date NOT NULL,
    sexo character(1) NOT NULL,
    direccion json,
    telefono json,
    correo json,
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.persona;
       public         heap    bdsiis1nusr    false    3            �            1259    17188    rol    TABLE     �   CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(255) NOT NULL,
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.rol;
       public         heap    bdsiis1nusr    false    3            �            1259    17187    rol_id_rol_seq    SEQUENCE     �   CREATE SEQUENCE public.rol_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.rol_id_rol_seq;
       public          bdsiis1nusr    false    3    211            O           0    0    rol_id_rol_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.rol_id_rol_seq OWNED BY public.rol.id_rol;
          public          bdsiis1nusr    false    210            �            1259    17222    usuario    TABLE     ;  CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre_usuario character varying(20) NOT NULL,
    id_empleado integer,
    clave character varying(255) NOT NULL,
    id_rol integer NOT NULL,
    estado_reg character(1),
    usuario_reg character varying(20),
    ip_reg character varying(15)
);
    DROP TABLE public.usuario;
       public         heap    bdsiis1nusr    false    3            �            1259    17221    usuario_id_usuario_seq    SEQUENCE     �   CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.usuario_id_usuario_seq;
       public          bdsiis1nusr    false    217    3            P           0    0    usuario_id_usuario_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;
          public          bdsiis1nusr    false    216            �           2604    17199    centro id_centro    DEFAULT     t   ALTER TABLE ONLY public.centro ALTER COLUMN id_centro SET DEFAULT nextval('public.centro_id_centro_seq'::regclass);
 ?   ALTER TABLE public.centro ALTER COLUMN id_centro DROP DEFAULT;
       public          bdsiis1nusr    false    212    213    213            �           2604    17207    empleado id_empleado    DEFAULT     |   ALTER TABLE ONLY public.empleado ALTER COLUMN id_empleado SET DEFAULT nextval('public.empleado_id_empleado_seq'::regclass);
 C   ALTER TABLE public.empleado ALTER COLUMN id_empleado DROP DEFAULT;
       public          bdsiis1nusr    false    214    215    215            �           2604    17289    grupo id_grupo    DEFAULT     p   ALTER TABLE ONLY public.grupo ALTER COLUMN id_grupo SET DEFAULT nextval('public.grupo_id_grupo_seq'::regclass);
 =   ALTER TABLE public.grupo ALTER COLUMN id_grupo DROP DEFAULT;
       public          bdsiis1nusr    false    221    220    221            �           2604    17310    lista id_lista    DEFAULT     p   ALTER TABLE ONLY public.lista ALTER COLUMN id_lista SET DEFAULT nextval('public.lista_id_lista_seq'::regclass);
 =   ALTER TABLE public.lista ALTER COLUMN id_lista DROP DEFAULT;
       public          bdsiis1nusr    false    222    223    223            �           2604    17271    paciente id_paciente    DEFAULT     |   ALTER TABLE ONLY public.paciente ALTER COLUMN id_paciente SET DEFAULT nextval('public.paciente_id_paciente_seq'::regclass);
 C   ALTER TABLE public.paciente ALTER COLUMN id_paciente DROP DEFAULT;
       public          bdsiis1nusr    false    219    218    219            �           2604    17191 
   rol id_rol    DEFAULT     h   ALTER TABLE ONLY public.rol ALTER COLUMN id_rol SET DEFAULT nextval('public.rol_id_rol_seq'::regclass);
 9   ALTER TABLE public.rol ALTER COLUMN id_rol DROP DEFAULT;
       public          bdsiis1nusr    false    211    210    211            �           2604    17225    usuario id_usuario    DEFAULT     x   ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);
 A   ALTER TABLE public.usuario ALTER COLUMN id_usuario DROP DEFAULT;
       public          bdsiis1nusr    false    217    216    217            7          0    17196    centro 
   TABLE DATA           �   COPY public.centro (id_centro, codigo_snis, nombre, direccion, usuario, clave, puerto, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    213   �k       9          0    17204    empleado 
   TABLE DATA           �   COPY public.empleado (id_empleado, id_persona, tipo_empleado, profesion, registro_profesional, id_centro, cargo, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    215   Vl       ?          0    17286    grupo 
   TABLE DATA           C   COPY public.grupo (id_grupo, nombre_grupo, tipo, area) FROM stdin;
    public          bdsiis1nusr    false    221   um       A          0    17307    lista 
   TABLE DATA           ^   COPY public.lista (id_lista, id_grupo, cod_texto, cod_numero, descripcion, orden) FROM stdin;
    public          bdsiis1nusr    false    223   �m       =          0    17268    paciente 
   TABLE DATA           �   COPY public.paciente (id_paciente, id_persona, id_centro, estado_civil, ocupacion, nivel_estudios, mun_nacimiento, mun_residencia, idioma_hablado, idioma_materno, autopertenencia, gestion_comunitaria, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    219   Dn       3          0    17178    persona 
   TABLE DATA           �   COPY public.persona (id_persona, tipo, ci, paterno, materno, nombres, fecha_nacimiento, sexo, direccion, telefono, correo, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    209   an       5          0    17188    rol 
   TABLE DATA           [   COPY public.rol (id_rol, nombre, descripcion, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    211   &r       ;          0    17222    usuario 
   TABLE DATA           z   COPY public.usuario (id_usuario, nombre_usuario, id_empleado, clave, id_rol, estado_reg, usuario_reg, ip_reg) FROM stdin;
    public          bdsiis1nusr    false    217   nr       Q           0    0    centro_id_centro_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.centro_id_centro_seq', 1, true);
          public          bdsiis1nusr    false    212            R           0    0    empleado_id_empleado_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.empleado_id_empleado_seq', 5, true);
          public          bdsiis1nusr    false    214            S           0    0    grupo_id_grupo_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.grupo_id_grupo_seq', 1, true);
          public          bdsiis1nusr    false    220            T           0    0    lista_id_lista_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.lista_id_lista_seq', 12, true);
          public          bdsiis1nusr    false    222            U           0    0    paciente_id_paciente_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.paciente_id_paciente_seq', 1, false);
          public          bdsiis1nusr    false    218            V           0    0    rol_id_rol_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.rol_id_rol_seq', 1, true);
          public          bdsiis1nusr    false    210            W           0    0    usuario_id_usuario_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 1, true);
          public          bdsiis1nusr    false    216            �           2606    17201    centro centro_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.centro
    ADD CONSTRAINT centro_pkey PRIMARY KEY (id_centro);
 <   ALTER TABLE ONLY public.centro DROP CONSTRAINT centro_pkey;
       public            bdsiis1nusr    false    213            �           2606    17209    empleado empleado_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_pkey PRIMARY KEY (id_empleado);
 @   ALTER TABLE ONLY public.empleado DROP CONSTRAINT empleado_pkey;
       public            bdsiis1nusr    false    215            �           2606    17291    grupo grupo_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.grupo
    ADD CONSTRAINT grupo_pkey PRIMARY KEY (id_grupo);
 :   ALTER TABLE ONLY public.grupo DROP CONSTRAINT grupo_pkey;
       public            bdsiis1nusr    false    221            �           2606    17312    lista lista_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.lista
    ADD CONSTRAINT lista_pkey PRIMARY KEY (id_lista);
 :   ALTER TABLE ONLY public.lista DROP CONSTRAINT lista_pkey;
       public            bdsiis1nusr    false    223            �           2606    17273    paciente paciente_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id_paciente);
 @   ALTER TABLE ONLY public.paciente DROP CONSTRAINT paciente_pkey;
       public            bdsiis1nusr    false    219            �           2606    17184    persona persona_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.persona
    ADD CONSTRAINT persona_pkey PRIMARY KEY (id_persona);
 >   ALTER TABLE ONLY public.persona DROP CONSTRAINT persona_pkey;
       public            bdsiis1nusr    false    209            �           2606    17193    rol rol_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);
 6   ALTER TABLE ONLY public.rol DROP CONSTRAINT rol_pkey;
       public            bdsiis1nusr    false    211            �           2606    17227    usuario usuario_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);
 >   ALTER TABLE ONLY public.usuario DROP CONSTRAINT usuario_pkey;
       public            bdsiis1nusr    false    217            �           1259    17202    ix_centro_id_centro    INDEX     K   CREATE INDEX ix_centro_id_centro ON public.centro USING btree (id_centro);
 '   DROP INDEX public.ix_centro_id_centro;
       public            bdsiis1nusr    false    213            �           1259    17220    ix_empleado_id_empleado    INDEX     S   CREATE INDEX ix_empleado_id_empleado ON public.empleado USING btree (id_empleado);
 +   DROP INDEX public.ix_empleado_id_empleado;
       public            bdsiis1nusr    false    215            �           1259    17292    ix_grupo_id_grupo    INDEX     G   CREATE INDEX ix_grupo_id_grupo ON public.grupo USING btree (id_grupo);
 %   DROP INDEX public.ix_grupo_id_grupo;
       public            bdsiis1nusr    false    221            �           1259    17313    ix_lista_id_lista    INDEX     G   CREATE INDEX ix_lista_id_lista ON public.lista USING btree (id_lista);
 %   DROP INDEX public.ix_lista_id_lista;
       public            bdsiis1nusr    false    223            �           1259    17284    ix_paciente_id_paciente    INDEX     S   CREATE INDEX ix_paciente_id_paciente ON public.paciente USING btree (id_paciente);
 +   DROP INDEX public.ix_paciente_id_paciente;
       public            bdsiis1nusr    false    219            �           1259    17185    ix_persona_ci    INDEX     F   CREATE UNIQUE INDEX ix_persona_ci ON public.persona USING btree (ci);
 !   DROP INDEX public.ix_persona_ci;
       public            bdsiis1nusr    false    209            �           1259    17186    ix_persona_id_persona    INDEX     O   CREATE INDEX ix_persona_id_persona ON public.persona USING btree (id_persona);
 )   DROP INDEX public.ix_persona_id_persona;
       public            bdsiis1nusr    false    209            �           1259    17194    ix_rol_id_rol    INDEX     ?   CREATE INDEX ix_rol_id_rol ON public.rol USING btree (id_rol);
 !   DROP INDEX public.ix_rol_id_rol;
       public            bdsiis1nusr    false    211            �           1259    17238    ix_usuario_id_usuario    INDEX     O   CREATE INDEX ix_usuario_id_usuario ON public.usuario USING btree (id_usuario);
 )   DROP INDEX public.ix_usuario_id_usuario;
       public            bdsiis1nusr    false    217            �           2606    17215     empleado empleado_id_centro_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_id_centro_fkey FOREIGN KEY (id_centro) REFERENCES public.centro(id_centro);
 J   ALTER TABLE ONLY public.empleado DROP CONSTRAINT empleado_id_centro_fkey;
       public          bdsiis1nusr    false    215    3216    213            �           2606    17210 !   empleado empleado_id_persona_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_id_persona_fkey FOREIGN KEY (id_persona) REFERENCES public.persona(id_persona);
 K   ALTER TABLE ONLY public.empleado DROP CONSTRAINT empleado_id_persona_fkey;
       public          bdsiis1nusr    false    215    209    3211            �           2606    17314    lista lista_id_grupo_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.lista
    ADD CONSTRAINT lista_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupo(id_grupo);
 C   ALTER TABLE ONLY public.lista DROP CONSTRAINT lista_id_grupo_fkey;
       public          bdsiis1nusr    false    221    223    3228            �           2606    17279     paciente paciente_id_centro_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.paciente
    ADD CONSTRAINT paciente_id_centro_fkey FOREIGN KEY (id_centro) REFERENCES public.centro(id_centro);
 J   ALTER TABLE ONLY public.paciente DROP CONSTRAINT paciente_id_centro_fkey;
       public          bdsiis1nusr    false    3216    213    219            �           2606    17274 !   paciente paciente_id_persona_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.paciente
    ADD CONSTRAINT paciente_id_persona_fkey FOREIGN KEY (id_persona) REFERENCES public.persona(id_persona);
 K   ALTER TABLE ONLY public.paciente DROP CONSTRAINT paciente_id_persona_fkey;
       public          bdsiis1nusr    false    209    219    3211            �           2606    17228     usuario usuario_id_empleado_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_empleado_fkey FOREIGN KEY (id_empleado) REFERENCES public.empleado(id_empleado);
 J   ALTER TABLE ONLY public.usuario DROP CONSTRAINT usuario_id_empleado_fkey;
       public          bdsiis1nusr    false    217    215    3219            �           2606    17233    usuario usuario_id_rol_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);
 E   ALTER TABLE ONLY public.usuario DROP CONSTRAINT usuario_id_rol_fkey;
       public          bdsiis1nusr    false    217    211    3214            7   g   x�3�442615�tN�+)�WHIUN�)MQ�*M�K�,�W��+��4�4�34��3�34�,�O,(6�+-.�1��9M��9�8S��2�ƚ�s��qqq Ii>      9     x�U��j�@E��W���X��d�R(t��f$�����U6	EB0�{�c-%��Y��ƀeҳ'm̵$x#���(<�uw���e=���W}��V�g
���T����'�[L5��G�E6��Q:��}i�'�z�e2X��Ĺ.XQ�g�.��i�~>iyxY�c�)�KV/�J99�j���J4=X�-��|����{#^��e���\I�B���7"�VM��0��	�R���Yc|/�xk~D����Mi������	�g�      ?      x�3�LI-(����t����� 'L�      A   �   x��;
�0��z�{���v���2��	X�HD��>�4�10v��7�]AA���a''��ff��qYe��,(�R~$F��)��Z��.q���Q�6F�I���J�e�%�6�-���F'��S�rW�p���7"�N~)P      =      x������ � �      3   �  x����n�6���S>�I�"���nt��n�@.M#j䨐Ŕ�4A����PΦq�n`a����|���U�2(���a�@Šr�tmAp^x�@v�Y�D���0N��![A]�1dg�W�OT�e�Y�xɄ���o����
�w��
�z��勺��}z��vqC�Ա����6u��өx`������+F�:ZIM����SW!����j�S���fqw�{v��/�`�L���uG�>Ĉs9����o��v�>l�g�yv�=G��J��0�Uɔ*k�=SV����R���(%��M��b졯�&;�K��b;�.�\p�5=���@��������N ��/�>�t�����M�@C�z��p��v7<� �p�fB�cN/qT��+Y�L7�aJ��U��F-V�H�T���
��![F�H�u��f�Έ��oU�y�u����na��*���S�"�����0P��Vi�܃z�i'!e��& I�f�)9+�ҠQj����ߐ-;��v��q�o�[���Ɍ��zь;4��'¼f)��ǾĦ���fyϦ�Z{S*�hK)�EŜ)%kHB�5wĦ(��� Iw���?��[�u;�ga��4SZ�'&�}�|z�g���a���8G��"��|ٍ!�9���'Q�U�����?���׌FP��b��Y�ӊ�D=�Zh�l9��o�i��GB�0��t
�I�o6ں��t!���c�i��aϧ�$���F3g*	��X�◽���Q\�2[՜��8��!�e�	��U^��U��
�\u�>��"��%$�����W3��3����@���$��!n`�'h�z�W'ݬ��7#�Z#@�q�`~�6�/l�LYS�YQ0g�\S�(�GP�jZR��:�1l �1��K�D��'�]@��D�������C�x�H��X�� ���n؃Q^���T      5   8   x�3�tL����,.)JL�/���QHIUHD
�(y����a�1~@����� ��      ;   `   x�3�LM�K,��4�T1JR14Rɉ2N��5Ջt���O�.MO�����1K�LJu76��ͫ�H	pɴ,�/rt3/�wjw��dd�g ��\1z\\\ ��X     