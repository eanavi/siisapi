from typing import List, Any

def paginacion(items:List[Any], pagina:int=1, tamanio:int=10):
    """
    Funcion que realiza la paginacion de los items
    :param items: List[Any] : Lista de items a paginar
    :param pagina: int : Numero de pagina a mostrar
    :param tamanio: int : Tamaño de la pagina
    :return: List[Any] : Lista de items paginados
    """
    total = len(items)
    inicio = (pagina - 1) * tamanio
    fin = inicio + tamanio

    return {
        "total": total,
        "pagina": pagina,
        "tamanio": tamanio,
        "items": items[inicio:fin]
    } 