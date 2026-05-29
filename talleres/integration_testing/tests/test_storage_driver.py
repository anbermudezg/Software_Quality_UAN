"""
Driver bottom-up para probar TaskStorage de forma completamente aislada.
No importa ni usa TaskService en ningún momento.
"""
import sys
import os
import tempfile
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.storage import TaskStorage


# ─── Fixture: archivo temporal limpio por test ───────────────────────────────

@pytest.fixture
def tmp_path_json(tmp_path):
    """Devuelve la ruta de un archivo JSON temporal (aún no creado)."""
    return str(tmp_path / "tasks_test.json")


# ─── Pruebas Bottom-Up ───────────────────────────────────────────────────────

class TestTaskStorageDriver:

    # 1. Archivo no existe → debe crearse con lista vacía
    def test_archivo_creado_si_no_existe(self, tmp_path_json):
        assert not os.path.exists(tmp_path_json)
        storage = TaskStorage(tmp_path_json)
        assert os.path.exists(tmp_path_json)
        with open(tmp_path_json) as f:
            content = json.load(f)
        assert content == []

    # 2. Guardar y recuperar una sola tarea
    def test_guardar_y_recuperar_una_tarea(self, tmp_path_json):
        storage = TaskStorage(tmp_path_json)
        storage.save([{"title": "Primera tarea", "done": False}])
        result = storage.load()
        assert len(result) == 1
        assert result[0]["title"] == "Primera tarea"
        assert result[0]["done"] is False

    # 3. Guardar y recuperar múltiples tareas
    def test_guardar_y_recuperar_multiples_tareas(self, tmp_path_json):
        storage = TaskStorage(tmp_path_json)
        tareas = [
            {"title": "Tarea 1", "done": False},
            {"title": "Tarea 2", "done": True},
            {"title": "Tarea 3", "done": False},
        ]
        storage.save(tareas)
        result = storage.load()
        assert len(result) == 3
        titles = [t["title"] for t in result]
        assert "Tarea 1" in titles
        assert "Tarea 2" in titles
        assert "Tarea 3" in titles

    # 4. Título vacío – política: Storage lo acepta (responsabilidad de Service)
    def test_titulo_vacio_es_aceptado_por_storage(self, tmp_path_json):
        """
        TaskStorage no valida contenido; acepta título vacío.
        La validación de negocio le corresponde a TaskService.
        """
        storage = TaskStorage(tmp_path_json)
        storage.save([{"title": "", "done": False}])
        result = storage.load()
        assert len(result) == 1
        assert result[0]["title"] == ""

    # 5. Sobrescritura: save reemplaza el contenido anterior
    def test_save_sobrescribe_contenido_anterior(self, tmp_path_json):
        storage = TaskStorage(tmp_path_json)
        storage.save([{"title": "Vieja", "done": False}])
        storage.save([{"title": "Nueva", "done": False}])
        result = storage.load()
        assert len(result) == 1
        assert result[0]["title"] == "Nueva"

    # 6. Lista vacía: save([]) deja el archivo con lista vacía
    def test_guardar_lista_vacia(self, tmp_path_json):
        storage = TaskStorage(tmp_path_json)
        storage.save([{"title": "X", "done": False}])
        storage.save([])
        result = storage.load()
        assert result == []

    # 7. Los datos persisten entre instancias distintas
    def test_persistencia_entre_instancias(self, tmp_path_json):
        storage1 = TaskStorage(tmp_path_json)
        storage1.save([{"title": "Persistente", "done": False}])
        storage2 = TaskStorage(tmp_path_json)
        result = storage2.load()
        assert result[0]["title"] == "Persistente"

    # 8. Load no modifica el archivo
    def test_load_no_modifica_archivo(self, tmp_path_json):
        storage = TaskStorage(tmp_path_json)
        storage.save([{"title": "Inmutable", "done": False}])
        mtime_before = os.path.getmtime(tmp_path_json)
        import time; time.sleep(0.05)
        storage.load()
        mtime_after = os.path.getmtime(tmp_path_json)
        assert mtime_before == mtime_after
