import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService

# Stubs para testing
class StubStorage:
    def __init__(self):
        self.tasks = []
        self.save_called = False
        self.load_called = False
    
    def load(self):
        self.load_called = True
        return self.tasks
    
    def save(self, tasks):
        self.save_called = True
        self.tasks = tasks

class StubNotifier:
    def __init__(self, fail=False):
        self._fail = fail
        self.messages = []
        self.send_called = False
    
    def send(self, message):
        if self._fail:
            raise ConnectionError("Fallo simulado")
        self.send_called = True
        self.messages.append(message)

# Stubs que simulan fallos - para test de errores
class FailingStorage:
    def __init__(self):
        self.tasks = []
    
    def load(self):
        return self.tasks
    
    def save(self, tasks):
        raise IOError("No se pudo escribir en disco")

class FailingNotifier:
    def send(self, message):
        raise ConnectionError("Servicio de notificaciones caído")

class TestServiceIntegrationErrors:
    def test_storage_failure_not_handled(self):
        storage = FailingStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        try:
            service.add_task("Nueva tarea")
            assert False, "Debería haber lanzado excepción"
        except IOError:
            pass
    
    def test_notifier_failure_task_already_saved(self):
        storage = StubStorage()
        notifier = FailingNotifier()
        service = TaskService(storage, notifier)
        try:
            service.add_task("Tarea importante")
        except ConnectionError:
            pass
        assert len(storage.tasks) == 1
        assert storage.tasks[0]['title'] == "Tarea importante"
    
    def test_empty_title_bug(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        result = service.add_task("")
        assert result is True
        assert len(storage.tasks) == 1
        assert storage.tasks[0]['title'] == ""
    
    def test_duplicate_task_returns_false(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        service.add_task("Tarea única")
        result = service.add_task("Tarea única")
        assert result is False
        assert len(storage.tasks) == 1