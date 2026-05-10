from src.ordenador import ordenar

def test_vacio():
    assert ordenar([]) == []
    
def test_desordenado_largo():
    assert ordenar([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]) == [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]

def test_un_elemento():
    assert ordenar([5]) == [5]

def test_ya_ordenado():
    assert ordenar([1, 2, 3]) == [1, 2, 3]

def test_otro_ordenado():
    assert ordenar([5, 4, 6]) == [4, 5, 6]

def test_con_repetidos():
    assert ordenar([3, 1, 2, 1]) == [1, 1, 2, 3]

def test_con_negativos():
    assert ordenar([-1, -3, -2]) == [-3, -2, -1]

def test_con_mezcla():
    assert ordenar([3, -1, 2, -2]) == [-2, -1, 2, 3]
    
def test_no_modifica_lista_original():
    lista = [3, 1, 2]
    ordenar(lista)
    assert lista == [3, 1, 2] 