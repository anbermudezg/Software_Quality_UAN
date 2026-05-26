import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService

class StorageStub:
    def __init__(self):
        self._tasks = []

    def load(self):
        return self._tasks

    def save(self, tasks):
        self._tasks = tasks

class NotifierStub:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)

class NotifierFalloStub:
    def send(self, message):
        raise ConnectionError("Fallo simulado")


class TestTopDown:

    def test_add_task_guarda_en_storage(self):
        storage = StorageStub()
        service = TaskService(storage, NotifierStub())
        service.add_task("Tarea de prueba")
        tareas = storage.load()
        assert len(tareas) == 1
        assert tareas[0]['title'] == "Tarea de prueba"

    def test_add_task_envia_notificacion(self):
        notifier = NotifierStub()
        service = TaskService(StorageStub(), notifier)
        service.add_task("Tarea notificada")
        assert len(notifier.messages) == 1
        assert "Tarea notificada" in notifier.messages[0]

    def test_add_task_duplicado_retorna_false(self):
        storage = StorageStub()
        service = TaskService(storage, NotifierStub())
        service.add_task("Duplicada")
        result = service.add_task("Duplicada")
        assert result is False
        assert len(storage.load()) == 1

    def test_add_task_titulo_vacio(self):
        storage = StorageStub()
        service = TaskService(storage, NotifierStub())
        service.add_task("")
        tareas = storage.load()
        assert len(tareas) == 0

    def test_fallo_notifier_no_revierte_storage(self):
        storage = StorageStub()
        service = TaskService(storage, NotifierFalloStub())
        try:
            service.add_task("Tarea con fallo")
        except ConnectionError:
            pass
        assert len(storage.load()) == 1

    def test_complete_task_marca_como_hecha(self):
        storage = StorageStub()
        service = TaskService(storage, NotifierStub())
        service.add_task("Completar esto")
        result = service.complete_task("Completar esto")
        assert result is True
        assert storage.load()[0]['done'] is True

    def test_complete_task_inexistente(self):
        service = TaskService(StorageStub(), NotifierStub())
        assert service.complete_task("No existe") is False