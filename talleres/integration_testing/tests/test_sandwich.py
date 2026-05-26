import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.service import TaskService
from src.storage import TaskStorage

class NotifierStub:
    def __init__(self):
        self.llamado = False
        self.messages = []

    def send(self, message):
        self.llamado = True
        self.messages.append(message)

class NotifierFalloStub:
    def send(self, message):
        raise ConnectionError("Sin red")


class TestSandwich:

    @pytest.fixture
    def setup(self, tmp_path):
        filepath = str(tmp_path / "sandwich_tasks.json")
        storage = TaskStorage(filepath)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        return service, storage, notifier

    def test_tarea_persiste_en_archivo_real(self, setup):
        service, storage, _ = setup
        service.add_task("Tarea persistente")
        tareas = storage.load()
        assert any(t['title'] == "Tarea persistente" for t in tareas)

    def test_notifier_stub_fue_llamado(self, setup):
        service, _, notifier = setup
        service.add_task("Notificar esto")
        assert notifier.llamado is True

    def test_fallo_notifier_deja_tarea_guardada(self, tmp_path):
        filepath = str(tmp_path / "fallo.json")
        storage = TaskStorage(filepath)
        service = TaskService(storage, NotifierFalloStub())
        try:
            service.add_task("Tarea con fallo")
        except ConnectionError:
            pass
        tareas = storage.load()
        assert len(tareas) == 1

    def test_complete_task_con_storage_real(self, setup):
        service, storage, _ = setup
        service.add_task("Completar real")
        service.complete_task("Completar real")
        tareas = storage.load()
        assert tareas[0]['done'] is True

    def test_duplicado_con_storage_real(self, setup):
        service, storage, _ = setup
        service.add_task("Única")
        service.add_task("Única")
        assert len(storage.load()) == 1