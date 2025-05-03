/*
procedimiento para determinar el tipo de datos de la tabla 

use BDestadistica
select a.cua_codigo, a.cua_descripcion, c.COL_CODIGO, c.COL_DESCRIPCION, c.COL_TIPO, c.COL_AUXILIAR, c.rel_codigo, c.*
from se_cuaderno a inner join SE_FORMULARIO as f on a.CUA_CODIGO = f.CUA_CODIGO
					inner join SE_COLUMNAS as c on f.COL_CODIGO = c.COL_CODIGO
where (a.cua_estado = 'A') and (a.cua_codigo in (1, 2, 3, 4, 5, 7, 10, 14)) --and (c.COL_VIGENCIA = 'S')
order by a.CUA_CODIGO, f.FOR_COL_POSI
**********************************************************

ALTER FUNCTION [dbo].[fn_se_datos_sel] (@i_col_tipo int, @i_emp_codigo int, @i_dat_data float,@i_auxiliar char(200),@i_rel_codigo int, @i_for_codigo int=null)   
RETURNS varchar(5000) AS
**/

--USE [BDestadistica]
GO
/****** Object:  StoredProcedure [dbo].[spBuscaPersona]    Script Date: 29/04/2025 9:16:46 ******/
SET ANSI_NULLS OFF
GO
SET QUOTED_IDENTIFIER OFF
GO
ALTER PROCEDURE [dbo].[spBuscaPersona](
	@criterio varchar(220)
)
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	declare @EsNumero Bit = 0;
	declare @EsFecha Bit = 0;

	if ISNUMERIC(@criterio) = 1
		set @EsNumero = 1;

	begin try
		if ISDATE(@criterio) = 1
			set @EsFecha = 1;
	end try
	begin catch
		set @EsFecha = 0;
	end catch

	if @EsNumero = 1
	begin
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where h.HCL_NUMCI like '%' +  @criterio + '%';
	end
	if @EsFecha = 1
	begin
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where h.HCL_FECNAC = cast(@criterio as datetime);
	end
	----------------------------- si estamos aqui es un texto -------------------------
	declare @tablaSpl table(numero int, splitdata nvarchar(60));

	insert into @tablaSpl(numero, splitdata) 
	select numero, splitdata from dbo.fnSplitCadena(@criterio, ' ');

	declare @nfilas int;

	select @nfilas = count(*) from @tablaSpl;

	declare @primera nvarchar(60), @segunda nvarchar(60), @tercera nvarchar(60), @cuarta nvarchar(60);
	select @primera = (select upper(splitdata) from @tablaSpl where numero = 1),
		   @segunda = (select upper(splitdata) from @tablaSpl where numero = 2),
		   @tercera = (select upper(splitdata) from @tablaSpl where numero = 3), 
		   @cuarta = (select upper(splitdata) from @tablaSpl where numero = 4);


	if @nfilas = 1
	begin
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where dbo.fn_normalizar_cadena(h.HCL_APPAT) LIKE '%' + dbo.fn_normalizar_cadena(@primera)+ '%';
	end
	else if (@nfilas = 2)
	begin 
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where dbo.fn_normalizar_cadena(h.HCL_nombre) LIKE '%' + dbo.fn_normalizar_cadena(@primera) + '%' 
			and dbo.fn_normalizar_cadena(h.hcl_appat) like '%' + dbo.fn_normalizar_cadena(@segunda) + '%';
	end
	else if (@nfilas = 3)
	begin
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where dbo.fn_normalizar_cadena(h.HCL_nombre) LIKE '%' + dbo.fn_normalizar_cadena(@primera) + '%' 
			and dbo.fn_normalizar_cadena(h.hcl_appat) like '%' + dbo.fn_normalizar_cadena(@segunda) + '%' 
			and dbo.fn_normalizar_cadena(h.hcl_apmat) like '%' + dbo.fn_normalizar_cadena(@tercera) + '%';
	end
	else if (@nfilas = 4)
	begin
		select h.codestabl, h.hcl_codigo, h.hcl_numci, h.hcl_appat, h.hcl_apmat, h.hcl_nombre,
			case HCL_SEXO when 1 then 'M' when 2 then 'F' else 'N' end as sexo, h.hcl_fecnac,  
			h.hcl_direcc, h.hcl_teldom, z.zon_descripcion, d.dep_codigo, d.dep_nombre, p.prov_codigo, 
			p.prov_nombre, m.codmunicip, m.nommunicip
		from SE_HC h inner join SE_ZONA z on h.zon_codigo = z.zon_codigo
					 inner join SE_DEPARTAMENTO as d on h.DEP_CODIGO_RES = d.DEP_CODIGO
					 inner join SE_PROVINCIA as p on h.PRO_CODIGO_RES = p.PROV_CODIGO 
					 inner join BDsnis.dbo.t_municipio as m on h.MUN_CODIGO_RES = m.codmunicip 
		where (dbo.fn_normalizar_cadena(upper(h.HCL_nombre)) LIKE '%' + dbo.fn_normalizar_cadena(@primera) + ' ' + dbo.fn_normalizar_cadena(@segunda) + '%') 
		and (dbo.fn_normalizar_cadena(upper(h.hcl_appat)) like '%' + dbo.fn_normalizar_cadena(@tercera) + '%') 
		and (dbo.fn_normalizar_cadena(upper(h.hcl_apmat)) like '%' + dbo.fn_normalizar_cadena(@cuarta) + '%');	
	end
END

--USE [BDestadistica]
GO
/****** Object:  UserDefinedFunction [dbo].[fn_normalizar_cadena]    Script Date: 29/04/2025 9:18:14 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER FUNCTION [dbo].[fn_normalizar_cadena](@entrada NVARCHAR(MAX))
RETURNS NVARCHAR(MAX)
AS
BEGIN
    DECLARE @normalizada NVARCHAR(MAX);

    SET @normalizada = @entrada;

    -- Reemplazar caracteres acentuados
    SET @normalizada = REPLACE(@normalizada, 'á', 'a');
    SET @normalizada = REPLACE(@normalizada, 'é', 'e');
    SET @normalizada = REPLACE(@normalizada, 'í', 'i');
    SET @normalizada = REPLACE(@normalizada, 'ó', 'o');
    SET @normalizada = REPLACE(@normalizada, 'ú', 'u');
    SET @normalizada = REPLACE(@normalizada, 'Á', 'A');
    SET @normalizada = REPLACE(@normalizada, 'É', 'E');
    SET @normalizada = REPLACE(@normalizada, 'Í', 'I');
    SET @normalizada = REPLACE(@normalizada, 'Ó', 'O');
    SET @normalizada = REPLACE(@normalizada, 'Ú', 'U');
    SET @normalizada = REPLACE(@normalizada, 'ñ', 'n');
    SET @normalizada = REPLACE(@normalizada, 'Ñ', 'N');

    RETURN @normalizada;
END;


