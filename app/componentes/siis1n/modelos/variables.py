from sqlalchemy import Integer, String, CHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.componentes.siis1n.modelos.edad_sqla import TipoEdad
from app.componentes.siis1n.modelos.edad import Edad
from app.componentes.siis1n.modelos.base import ModeloBase


class Variables(ModeloBase):
    __tablename__ = "variables"

    id_variable: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True)
    id_prestacion: Mapped[int] = mapped_column(
        Integer, ForeignKey('prestacion.id_prestacion'), nullable=False)
    for_codigo: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_var: Mapped[str] = mapped_column(String(60), nullable=False)
    tipo: Mapped[int] = mapped_column(Integer, nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    lis_tabla: Mapped[str] = mapped_column(String(20), nullable=False)
    grupo: Mapped[str] = mapped_column(String(30), nullable=False)
