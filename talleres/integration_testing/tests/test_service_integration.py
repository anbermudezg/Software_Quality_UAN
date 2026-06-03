import sys, os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService


# stubs medio chafa para simular storage y notificador
class StubStorage:
    def __init__(self, initial=None, raise_on_save=False):
        self.saved = None
        self.calls = []
        self._data = initial or []
        self.raise_on_save = raise_on_save

    def load(self):
        self.calls.append(('load', None))
        return list(self._data)

    def save(self, tasks):
        self.calls.append(('save', tasks))
        if self.raise_on_save:
            raise RuntimeError('Storage failure')
        self.saved = list(tasks)
        self._data = list(tasks)


class StubNotifier:
    def __init__(self, raise_on_send=False):
        self.sent = []
        self.raise_on_send = raise_on_send

    def send(self, message):
        if self.raise_on_send:
            raise ConnectionError('Notifier failure')
        self.sent.append(message)


class TestTopDown:
    def test_add_task_calls_storage_and_notifier(self):
        # caso normal, guarda y manda notif
        storage = StubStorage(initial=[{'title': 'Tarea previa', 'done': False}])
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task('Comprar leche')

        assert result is True
        assert storage.calls == [
            ('load', None),
            ('save', [
                {'title': 'Tarea previa', 'done': False},
                {'title': 'Comprar leche', 'done': False},
            ]),
        ]
        assert notifier.sent == ["Tarea 'Comprar leche' creada"]
        assert storage.saved == [
            {'title': 'Tarea previa', 'done': False},
            {'title': 'Comprar leche', 'done': False},
        ]

    def test_add_task_duplicate_does_not_save_or_notify(self):
        # si ya existe no guardes ni notifiques
        storage = StubStorage(initial=[{'title': 'Duplicada', 'done': False}])
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task('Duplicada')

        assert result is False
        assert storage.calls == [('load', None)]
        assert storage.saved is None
        assert notifier.sent == []

    def test_add_task_rejects_empty_title(self):
        # titulo vacio no se debe aceptar
        storage = StubStorage(initial=[{'title': 'Tarea previa', 'done': False}])
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task('')

        assert result is False
        assert storage.calls == []
        assert storage.saved is None
        assert notifier.sent == []

    def test_storage_failure_prevents_notification(self):
        # si storage falla no deberia llamar a notifier
        storage = StubStorage(initial=[], raise_on_save=True)
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        with pytest.raises(RuntimeError, match='Storage failure'):
            service.add_task('Tarea fallida')

        assert storage.calls == [
            ('load', None),
            ('save', [{'title': 'Tarea fallida', 'done': False}]),
        ]
        assert notifier.sent == []

    def test_notifier_failure_rolls_back_storage(self):
        # si el notifier explota, se deshace lo guardado
        storage = StubStorage(initial=[{'title': 'Existente', 'done': False}])
        notifier = StubNotifier(raise_on_send=True)
        service = TaskService(storage, notifier)

        with pytest.raises(ConnectionError, match='Notifier failure'):
            service.add_task('Nueva tarea')

        assert storage.calls == [
            ('load', None),
            ('save', [
                {'title': 'Existente', 'done': False},
                {'title': 'Nueva tarea', 'done': False},
            ]),
            ('save', [{'title': 'Existente', 'done': False}]),
        ]
        assert notifier.sent == []
        assert storage.saved == [{'title': 'Existente', 'done': False}]


class TestSandwich:
    def test_service_persists_task_and_notifies(self, tmp_path):
        # prueba con storage real y notifier fake
        storage_path = tmp_path / 'sandwich_tasks.json'
        storage = TaskStorage(str(storage_path))
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task('Estudiar integración')

        assert result is True
        assert notifier.sent == ["Tarea 'Estudiar integración' creada"]
        assert storage.load() == [{'title': 'Estudiar integración', 'done': False}]

    def test_service_does_not_notify_when_duplicate(self, tmp_path):
        storage_path = tmp_path / 'sandwich_tasks.json'
        storage = TaskStorage(str(storage_path))
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        service.add_task('Revisar pruebas')
        result = service.add_task('Revisar pruebas')

        assert result is False
        assert notifier.sent == ["Tarea 'Revisar pruebas' creada"]
        assert storage.load() == [{'title': 'Revisar pruebas', 'done': False}]

    def test_service_rejects_empty_title_with_real_storage(self, tmp_path):
        storage_path = tmp_path / 'sandwich_tasks.json'
        storage = TaskStorage(str(storage_path))
        notifier = StubNotifier()
        service = TaskService(storage, notifier)

        result = service.add_task('')

        assert result is False
        assert notifier.sent == []
        assert storage.load() == []

    def test_list_tasks_returns_empty_when_file_missing(self, tmp_path):
        storage_path = tmp_path / 'missing_sandwich.json'
        service = TaskService(TaskStorage(str(storage_path)), StubNotifier())

        assert service.list_tasks() == []

    def test_list_tasks_returns_empty_when_file_is_empty(self, tmp_path):
        storage_path = tmp_path / 'empty_sandwich.json'
        storage_path.write_text('[]')
        service = TaskService(TaskStorage(str(storage_path)), StubNotifier())

        assert service.list_tasks() == []
