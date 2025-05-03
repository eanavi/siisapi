def validar_fecha_de_edad(anio: int, mes: int, dia: int) -> None:
    if not isinstance(anio, int) or anio < 0:
        raise ValueError("Los años deben ser un número entero no negativo.")
    if not isinstance(mes, int) or not 0 <= mes <= 12:
        raise ValueError("Los meses deben ser un número entero entre 0 y 12.")

    # Determinar días máximos del mes
    if mes == 2:
        max_dias = 29 if (anio % 4 == 0 and (
            anio % 100 != 0 or anio % 400 == 0)) else 28
    elif mes in [4, 6, 9, 11]:
        max_dias = 30
    else:
        max_dias = 31

    if not isinstance(dia, int) or dia < 0 or dia > max_dias:
        raise ValueError(
            f"Los días deben ser un número entero entre 0 y {max_dias}.")
