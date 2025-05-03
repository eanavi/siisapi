
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from app.utiles.validar_edad import validar_fecha_de_edad


class Edad:
    anio: int
    mes: int
    dia: int

    def __init__(self, anio: int, mes: int, dia: int):
        validar_fecha_de_edad(anio, mes, dia)
        self.anio = anio
        self.mes = mes
        self.dia = dia

    def __repr__(self):
        return f"Edad(años={self.anio}, meses={self.mes}, dias={self.dia})"

    def __eq__(self, other):
        if not isinstance(other, Edad):
            return NotImplemented

        return self.anio == other.anio and self.mes == other.mes and self.dia == other.dia

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Edad):
            return NotImplemented
        return (self.anio, self.mes, self.dia) < (other.anio, other.mes, other.dia)

    def __le__(self, other):
        if not isinstance(other, Edad):
            return NotImplemented
        return (self.anio, self.mes, self.dia) <= (other.anio, other.mes, other.dia)

    def __str__(self) -> str:
        return f"{self.anio} años, {self.mes} meses, {self.dia} días"

    def __add__(self, otra_edad):
        if not isinstance(otra_edad, Edad):
            return NotImplemented
        total_dias = self.anio * 365 + self.mes * 30 + self.dia + \
            otra_edad.anio * 365 + otra_edad.mes * 30 + otra_edad.dia

        nuevos_dias = total_dias % 30
        total_meses = total_dias // 30
        nuevos_meses = total_meses % 12
        nuevos_anios = total_meses // 12
        return Edad(nuevos_anios, nuevos_meses, nuevos_dias)


def calcular_edad(fecha: date | str) -> Edad:
    """
    Calcula la edad a partir de una fecha dada.
    :param fecha: Fecha en formato 'YYYY-MM-DD'.
    :return: Edad como objeto Edad.
    """
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("La fecha debe estar en formato 'YYYY-MM-DD'.")
    elif not isinstance(fecha, date):
        try:
            fecha = datetime.strptime(fecha, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("La fecha debe estar en formato 'DD/MM/YYYY'.")
    hoy = date.today()

    if hoy < fecha:
        raise ValueError("La fecha de nacimiento no puede ser futura.")

    r = relativedelta(hoy, fecha)
    return Edad(r.years, r.months, r.days)
