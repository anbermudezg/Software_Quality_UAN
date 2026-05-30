"""
Pruebas de integración: top-down (stubs), sandwich y escenarios de error.
"""

from src.storage import TaskStorage
from src.service import TaskService


class StorageStub:
    def __init__(self, initial_tasks=None):
        self.tasks = list(initial_tasks or [])
        self.load_calls = 0
        self.save_calls = 0
        self.last_saved = None

    def load(self):
        self.load_calls += 1
        return list(self.tasks)

    def save(self, tasks):
        self.save_calls += 1
        self.tasks = list(tasks)
        self.last_saved = list(tasks)


class NotifierStub:
    def __init__(self, fail=False):
        self.messages = []
        self.send_calls = 0
        self.fail = fail

    def send(self, message):
        self.send_calls += 1
        self.messages.append(message)
        if self.fail:
            raise ConnectionError("No se pudo enviar la notificación")


class FailingStorageStub(StorageStub):
    def save(self, tasks):
        raise IOError("Error de escritura simulado")


class TestTopDown:
    def test_add_task_calls_storage_and_notifier(self):
        storage = StorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Estudiar integración") is True
        assert storage.save_calls == 1
        assert storage.last_saved == [{"title": "Estudiar integración", "done": False}]
        assert notifier.send_calls == 1
        assert notifier.messages == ["Tarea 'Estudiar integración' creada"]

    def test_duplicate_does_not_save_or_notify(self):
        storage = StorageStub([{"title": "Duplicada", "done": False}])
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Duplicada") is False
        assert storage.save_calls == 0
        assert notifier.send_calls == 0

    def test_empty_title_rejected(self):
        storage = StorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("") is False
        assert service.add_task("   ") is False
        assert storage.save_calls == 0

    def test_storage_failure_does_not_notify(self):
        storage = FailingStorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Fallo disco") is False
        assert notifier.send_calls == 0

    def test_notifier_failure_reverts_storage(self):
        storage = StorageStub()
        notifier = NotifierStub(fail=True)
        service = TaskService(storage, notifier)

        assert service.add_task("Inconsistente") is False
        assert storage.save_calls == 2
        assert storage.tasks == []


class TestSandwich:
    def test_add_task_persists_with_real_storage(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Comprar pan") is True
        assert storage.load() == [{"title": "Comprar pan", "done": False}]
        assert notifier.messages == ["Tarea 'Comprar pan' creada"]

    def test_complete_task_updates_real_storage(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        service.add_task("Ejercicio")
        assert service.complete_task("Ejercicio") is True
        assert storage.load()[0]["done"] is True


class TestServiceIntegration:
    def test_add_task_persists_and_notifies(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Comprar leche") is True
        assert storage.load() == [{"title": "Comprar leche", "done": False}]
        assert notifier.send_calls == 1

    def test_complete_task(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        service.add_task("Aprender pytest")
        assert service.complete_task("Aprender pytest") is True
        assert storage.load()[0]["done"] is True

    def test_duplicate_not_persisted(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("Única") is True
        assert service.add_task("Única") is False
        assert len(storage.load()) == 1

    def test_empty_title_rejected(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        assert service.add_task("") is False
        assert storage.load() == []

    def test_list_tasks_empty_file(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        service = TaskService(storage, NotifierStub())

        assert service.list_tasks() == []

    def test_storage_save_failure(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)

        def failing_save(tasks):
            raise IOError("fallo simulado")

        storage.save = failing_save
        assert service.add_task("No guardada") is False
        assert storage.load() == []
        assert notifier.send_calls == 0

    def test_notifier_failure_keeps_storage_consistent(self, temp_json_path):
        storage = TaskStorage(temp_json_path)
        notifier = NotifierStub(fail=True)
        service = TaskService(storage, notifier)

        assert service.add_task("Fallo notif") is False
        assert storage.load() == []
