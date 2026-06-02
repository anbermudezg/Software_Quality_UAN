import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

class StubStorage:
    def __init__(self):
        self.data = []

    def load(self):
        return self.data

    def save(self, tasks):
        self.data = tasks

class StubNotifier:
    def __init__(self):
        self.send_called = False
    
    def send(self, message):
        self.send_called = True 


class TestTopDown:
    def test_add_task_with_stub_notifier(self):
        storage = StubStorage()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        result = service.add_task("Comprar pan")
        assert result is True
        assert len(storage.load()) == 1
        assert storage.load()[0]['title'] == "Comprar pan"
        assert notifier.send_called is True