import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService

class StubNotifier:
	def __init__(self):
		self.send_called = False
	
	def send(self, message):
		self.send_called = True

class TestSandwich:
    def setup_method(self):
    	self.storage = TaskStorage("test_sandwich.json")
    	self.notifier = StubNotifier()
    	self.service = TaskService(self.storage, self.notifier)
    
    def test_add_task_with_stub_notifier(self):
        result = self.service.add_task("Comprar pan")
        assert result is True
        assert len(self.storage.load()) == 1
        assert self.storage.load()[0]['title'] == "Comprar pan"
        assert self.notifier.send_called is True
    
    def teardown_method(self):
        if os.path.exists("test_sandwich.json"):
            os.remove("test_sandwich.json")
    
    def test_complete_task_persists(self):
        self.service.add_task("Aprender pytest")
        assert self.service.complete_task("Aprender pytest") is True
        tasks = self.storage.load()
        assert len(tasks) == 1
        assert tasks[0]['title'] == "Aprender pytest"
        assert tasks[0]['done'] is True