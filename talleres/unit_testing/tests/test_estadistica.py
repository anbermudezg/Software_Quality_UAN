import pytest
from src.estadistica import calcular_promedio

def test_valores_reales():
    assert calcular_promedio([1, 2, 3]) == 2.0
    assert  calcular_promedio([5, 10]) == 7.5
    assert calcular_promedio([0, 0, 0]) == 0.0

def test_valores_negativos():
    assert calcular_promedio([-1, -2, -3]) == -2.0
    assert calcular_promedio([-5, -10]) == -7.5

def test_valores_mixtos():
    assert calcular_promedio([-1, 0, 1]) == 0.0
    assert calcular_promedio([-5, 0, 5]) == 0.0
    assert calcular_promedio([-2, 2, 2]) == 0.6666666666666666
    
def test_un_solo_valor():
    assert calcular_promedio([5]) == 5.0
    assert calcular_promedio([-3]) == -3.0
    assert calcular_promedio([0]) == 0.0

def test_implementaciones_incorrectas():
    assert calcular_promedio([1, 2, 3]) != 3.14
    assert calcular_promedio([5, 10]) != 0.0
    assert calcular_promedio([-1, -2, -3]) != 0.0
    
def test_lista_vacia_retorna_none():
    assert calcular_promedio([]) is None

def test_no_lanza_excepcion():
    try:
        calcular_promedio([5])
    except Exception:
        pytest.fail("No debería lanzar excepción")