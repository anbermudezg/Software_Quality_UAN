import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService
from src.storage import TaskStorage


# Stub simple para ver si el servicio llamó de verdad a storage.
class StubStorage:
    def __init__(self, initial_tasks=None, fail_on_save=False):
        self._tasks = [dict(task) for task in (initial_tasks or [])]
        self.fail_on_save = fail_on_save
        self.load_calls = 0
        self.save_calls = []

    def load(self):
        self.load_calls += 1
        return [dict(task) for task in self._tasks]

    def save(self, tasks):
        self.save_calls.append([dict(task) for task in tasks])
        if self.fail_on_save:
            raise IOError("Fallo simulado de almacenamiento")
        self._tasks = [dict(task) for task in tasks]


class StubNotifier:
    def __init__(self, fail=False):
        self.fail = fail
        self.messages = []

    def send(self, message):
        self.messages.append(message)
        if self.fail:
            raise ConnectionError("Fallo simulado de notificación")


# Pruebas con partes falsas para mirar la lógica del servicio.
class TestTopDown:
    def test_add_task_uses_storage_and_notifier(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task("Comprar leche")

        assert result is True
        assert storage.load_calls == 1
        assert storage.save_calls == [[{"title": "Comprar leche", "done": False}]]
        assert storage._tasks == [{"title": "Comprar leche", "done": False}]
        assert notifier.messages == ["Tarea 'Comprar leche' creada"]

    def test_add_task_duplicate_returns_false_without_writing(self):
        storage = StubStorage(initial_tasks=[{"title": "Comprar leche", "done": False}])
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task("Comprar leche")

        assert result is False
        assert storage.save_calls == []
        assert notifier.messages == []
        assert storage._tasks == [{"title": "Comprar leche", "done": False}]

    def test_add_task_rejects_empty_title(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        # Si llega vacío, no debería seguir.
        with pytest.raises(ValueError, match="El título no puede estar vacío"):
            service.add_task("   ")

        assert storage.load_calls == 0
        assert storage.save_calls == []
        assert notifier.messages == []

    def test_add_task_rolls_back_when_notifier_fails(self):
        storage = StubStorage()
        notifier = StubNotifier(fail=True)
        service = TaskService(storage, notifier)

        # Si falla la notificación, la tarea no se queda a medias.
        with pytest.raises(ConnectionError, match="Fallo simulado de notificación"):
            service.add_task("Revisar rollback")

        assert storage.save_calls == [
            [{"title": "Revisar rollback", "done": False}],
            []
        ]
        assert storage._tasks == []
        assert notifier.messages == ["Tarea 'Revisar rollback' creada"]

    def test_add_task_propagates_storage_failure(self):
        storage = StubStorage(fail_on_save=True)
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        # Si storage falla, no hay manera de seguir.
        with pytest.raises(IOError, match="Fallo simulado de almacenamiento"):
            service.add_task("Fallo de persistencia")

        assert storage._tasks == []
        assert len(storage.save_calls) == 1
        assert notifier.messages == []

    def test_complete_task(self):
        storage = StubStorage(initial_tasks=[{"title": "Aprender pytest", "done": False}])
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        assert service.complete_task("Aprender pytest") is True
        assert storage._tasks == [{"title": "Aprender pytest", "done": True}]


# Aquí probamos storage real, pero sin mandar notificaciones reales.
class TestSandwich:
    def test_add_task_persists_with_real_storage(self, tmp_path):
        storage_path = tmp_path / "tasks.json"
        storage = TaskStorage(str(storage_path))
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task("Integración real")

        assert result is True
        assert storage.load() == [{"title": "Integración real", "done": False}]
        assert notifier.messages == ["Tarea 'Integración real' creada"]

    def test_add_task_rolls_back_with_real_storage_if_notifier_fails(self, tmp_path):
        storage_path = tmp_path / "tasks.json"
        storage = TaskStorage(str(storage_path))
        notifier = StubNotifier(fail=True)
        service = TaskService(storage, notifier)

        # Aunque el storage sea real, si el notifier cae, se prueba el rollback.
        with pytest.raises(ConnectionError, match="Fallo simulado de notificación"):
            service.add_task("Rollback real")

        assert storage.load() == []
        assert notifier.messages == ["Tarea 'Rollback real' creada"]