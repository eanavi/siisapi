-- Consulta para obtener la estructura de las tablas de los formularios
-- Se utiliza para la carga de datos en la tabla de estadistica
use BDestadistica

select c.CUA_CODIGO, l.COL_CODIGO,f.FOR_CODIGO, c.CUA_DESCRIPCION, l.COL_DESCRIPCION, l.COL_TIPO, g.lis_descripcion, l.COL_AUXILIAR, l.rel_codigo, r.lis_tabla, f.GRS_CODIGO
from SE_CUADERNO as c  
	inner join SE_FORMULARIO as f on c.CUA_CODIGO = f.CUA_CODIGO
	inner join SE_COLUMNAS as l on f.COL_CODIGO = l.COL_CODIGO
	left join ad_RelacionaTablas as r on l.rel_codigo = r.rel_codigo
	left join ad_listagenerica as g on l.COL_TIPO = g.lis_codigo
where c.CUA_CODIGO in (1, 2, 3, 4, 5, 6, 7, 10, 14) and g.lis_tabla = 'se_tipo_dato' and l.COL_VIGENCIA = 'N'
order by c.CUA_CODIGO, f.FOR_COL_POSI

