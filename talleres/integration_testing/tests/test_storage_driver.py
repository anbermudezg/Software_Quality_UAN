import sys, os
import tempfile
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.storage import TaskStorage

class TestStorageDriver:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.filepath = self.temp_file.name

    def teardown_method(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_archivo_no_existe_se_crea_con_lista_vacia(self):
        storage = TaskStorage(self.filepath)
        datos = storage.load()
        assert datos == []
        assert os.path.exists(self.filepath)

    def test_guardar_y_recuperar_una_tarea(self):
        storage = TaskStorage(self.filepath)
        tareas = [{"title": "Estudiar", "done": False}]
        storage.save(tareas)
        cargadas = storage.load()
        assert len(cargadas) == 1
        assert cargadas[0]["title"] == "Estudiar"

    def test_guardar_y_recuperar_multiples_tareas(self):
        storage = TaskStorage(self.filepath)
        tareas = [
            {"title": "Tarea 1", "done": False},
            {"title": "Tarea 2", "done": True}
        ]
        storage.save(tareas)
        cargadas = storage.load()
        assert len(cargadas) == 2

    def test_guardar_titulo_vacio(self):
        storage = TaskStorage(self.filepath)
        tareas = [{"title": "", "done": False}]
        storage.save(tareas)
        cargadas = storage.load()
        assert cargadas[0]["title"] == ""