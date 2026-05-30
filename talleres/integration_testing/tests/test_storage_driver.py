"""
Pruebas Bottom-Up para TaskStorage.
Driver directo: se prueba Storage de forma aislada, sin Service.
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.storage import TaskStorage


@pytest.fixture
def storage(tmp_path):
    """Driver: crea un TaskStorage apuntando a un archivo temporal."""
    filepath = str(tmp_path / "driver_tasks.json")
    return TaskStorage(filepath)


# ── 1. Creación automática del archivo ──────────────────────────────────────

def test_archivo_no_existente_se_crea_vacio(tmp_path):
    """Si el archivo no existe, Storage lo crea con lista vacía."""
    filepath = str(tmp_path / "nuevo.json")
    assert not os.path.exists(filepath)
    TaskStorage(filepath)
    assert os.path.exists(filepath)
    with open(filepath) as f:
        data = json.load(f)
    assert data == []


# ── 2. Guardar y recuperar una tarea ───────────────────────────────────────

def test_guardar_y_recuperar_una_tarea(storage):
    task = {"title": "Tarea única", "done": False}
    storage.save([task])
    loaded = storage.load()
    assert len(loaded) == 1
    assert loaded[0]["title"] == "Tarea única"
    assert loaded[0]["done"] is False


# ── 3. Guardar y recuperar múltiples tareas ────────────────────────────────

def test_guardar_y_recuperar_multiples_tareas(storage):
    tasks = [
        {"title": "Alfa", "done": False},
        {"title": "Beta", "done": True},
        {"title": "Gamma", "done": False},
    ]
    storage.save(tasks)
    loaded = storage.load()
    assert len(loaded) == 3
    titles = [t["title"] for t in loaded]
    assert "Alfa" in titles
    assert "Beta" in titles
    assert "Gamma" in titles


# ── 4. Título vacío: política explícita ────────────────────────────────────

def test_titulo_vacio_puede_guardarse_pero_es_datos_invalidos(storage):
    """
    Storage acepta cualquier dato (no valida negocio).
    Esta prueba documenta que el control debe estar en Service, no aquí.
    """
    storage.save([{"title": "", "done": False}])
    loaded = storage.load()
    # Storage no rechaza — lo guarda; la validación es responsabilidad de Service
    assert len(loaded) == 1
    assert loaded[0]["title"] == ""


# ── 5. Sobrescritura: save reemplaza el contenido previo ───────────────────

def test_save_sobreescribe_contenido_previo(storage):
    storage.save([{"title": "Vieja", "done": False}])
    storage.save([{"title": "Nueva", "done": False}])
    loaded = storage.load()
    assert len(loaded) == 1
    assert loaded[0]["title"] == "Nueva"


# ── 6. Lista vacía persiste correctamente ──────────────────────────────────

def test_guardar_lista_vacia(storage):
    storage.save([{"title": "Algo", "done": False}])
    storage.save([])
    assert storage.load() == []


# ── 7. Preservación del campo 'done' ───────────────────────────────────────

def test_campo_done_se_preserva_correctamente(storage):
    tasks = [
        {"title": "Pendiente", "done": False},
        {"title": "Completa", "done": True},
    ]
    storage.save(tasks)
    loaded = storage.load()
    done_map = {t["title"]: t["done"] for t in loaded}
    assert done_map["Pendiente"] is False
    assert done_map["Completa"] is True


# ── 8. Archivo inaccesible: fallo de escritura ─────────────────────────────

def test_save_falla_si_ruta_no_existe(tmp_path):
    """Si la ruta del archivo no existe, save lanza excepción."""
    filepath = str(tmp_path / "no_existe" / "tasks.json")
    storage = object.__new__(TaskStorage)
    storage.filepath = filepath  # Bypass del __init__ para no crear el dir
    with pytest.raises(Exception):
        storage.save([{"title": "Test", "done": False}])
