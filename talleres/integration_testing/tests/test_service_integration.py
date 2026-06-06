import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

# Stubs para enfoque top-down
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

def make_temp_storage():
    f = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    f.close()
    os.unlink(f.name)
    return TaskStorage(f.name), f.name

class TestServiceIntegration:
    def test_add_task_happy_path(self):
        storage, _ = make_temp_storage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        result = service.add_task("Comprar leche")
        assert result is True
        tasks = storage.load()
        assert len(tasks) == 1
        assert tasks[0]['title'] == "Comprar leche"
        assert notifier.send_called is True
    
    def test_complete_task(self):
        storage, _ = make_temp_storage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        service.add_task("Aprender pytest")
        assert service.complete_task("Aprender pytest") is True

# Enfoque Top-Down
class TestTopDown:
    def test_add_task_stored_correctly(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        result = service.add_task("Comprar leche")
        assert result is True
        assert storage.save_called is True
        assert len(storage.tasks) == 1
        assert storage.tasks[0]['title'] == "Comprar leche"
    
    def test_add_task_notifies_correctly(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        service.add_task("Comprar pan")
        assert notifier.send_called is True
        assert "Comprar pan" in notifier.messages[0]

# Enfoque Sandwich
class TestSandwich:
    def test_service_uses_storage_real(self):
        storage, _ = make_temp_storage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        service.add_task("Tarea sandwich")
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]['title'] == "Tarea sandwich"
    
    def test_service_notifies_with_stub(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        service.add_task("Tarea notificada")
        assert storage.save_called is True
        assert notifier.send_called is True