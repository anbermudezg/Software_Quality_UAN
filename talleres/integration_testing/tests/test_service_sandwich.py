import sys, os
import tempfile
from unittest.mock import Mock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.storage import TaskStorage
from src.service import TaskService

class TestSandwich:
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.filepath = self.temp_file.name
        self.storage_real = TaskStorage(self.filepath)
        self.notifier_stub = Mock()

    def teardown_method(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_sandwich_agregar_tarea_persiste_en_storage_real(self):
        service = TaskService(self.storage_real, self.notifier_stub)
        service.add_task("Tarea sandwich")
        tareas = self.storage_real.load()
        assert len(tareas) == 1
        assert tareas[0]["title"] == "Tarea sandwich"
        self.notifier_stub.send.assert_called_once()

    def test_sandwich_completar_tarea_persiste_cambio(self):
        service = TaskService(self.storage_real, self.notifier_stub)
        service.add_task("Tarea para completar")
        service.complete_task("Tarea para completar")
        tareas = self.storage_real.load()
        assert tareas[0]["done"] is True