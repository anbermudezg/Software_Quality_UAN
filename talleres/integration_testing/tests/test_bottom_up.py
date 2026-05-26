import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.storage import TaskStorage

@pytest.fixture
def storage(tmp_path):
    filepath = str(tmp_path / "tasks_test.json")
    return TaskStorage(filepath)


class TestBottomUp:

    def test_archivo_se_crea_vacio(self, storage):
        tareas = storage.load()
        assert tareas == []

    def test_guardar_y_cargar(self, storage):
        tareas = [{"title": "Tarea 1", "done": False}]
        storage.save(tareas)
        assert storage.load() == tareas

    def test_multiples_tareas(self, storage):
        tareas = [
            {"title": "Alfa", "done": False},
            {"title": "Beta", "done": True},
        ]
        storage.save(tareas)
        resultado = storage.load()
        assert len(resultado) == 2
        assert resultado[1]['done'] is True

    def test_sobrescribir_tareas(self, storage):
        storage.save([{"title": "Original", "done": False}])
        storage.save([{"title": "Nuevo", "done": False}])
        resultado = storage.load()
        assert len(resultado) == 1
        assert resultado[0]['title'] == "Nuevo"

    def test_guardar_lista_vacia(self, storage):
        storage.save([])
        assert storage.load() == []

    def test_persistencia_en_disco(self, storage):
        storage.save([{"title": "Persistida", "done": False}])
        with open(storage.filepath, 'r') as f:
            contenido = json.load(f)
        assert contenido[0]['title'] == "Persistida"