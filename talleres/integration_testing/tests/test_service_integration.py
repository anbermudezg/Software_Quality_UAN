import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier
from unittest.mock import patch

class TestServiceIntegration:
    def test_add_task_happy_path(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        result = service.add_task("Comprar leche")
        assert result is True
    
    def test_add_task_save(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        service.add_task("Comprar huevos")
        data = storage.load()
        assert len(data) == 1
        assert data[0]['title'] == "Comprar huevos"
        assert data[0]['done'] is False

    def test_complete_task(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        service.add_task("Aprender pytest")
        assert service.complete_task("Aprender pytest") is True

    def test_storage_failure_on_save(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        with patch.object(storage, 'save', side_effect=Exception("Disk error")):
            result = service.add_task("Comprar pan")
            assert result is False
            assert len(storage.load()) == 0
            
            
    def teardown_method(self):
        if os.path.exists("test_tasks.json"):
            os.remove("test_tasks.json")
    
    def test_notifier_failure_on_add_task(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        with patch.object(notifier, 'send', side_effect=Exception("Notification error")):
            result = service.add_task("Comprar pan")
            assert result is False
            data = storage.load()
            assert len(data) == 0  
    
    def test_add_task_empty_title(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        result = service.add_task("   ")
        assert result is False
        assert len(storage.load()) == 0
    
    def test_add_task_duplicate_title(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        service.add_task("Comprar pan")
        result = service.add_task("Comprar pan")
        assert result is False
        assert len(storage.load()) == 1
    
    def test_list_tasks_empty(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        result = service.list_tasks()
        assert result == []

    def test_list_tasks_with_data(self):
        storage = TaskStorage("test_tasks.json")
        notifier = Notifier()
        service = TaskService(storage, notifier)
        service.add_task("Comprar pan")
        result = service.list_tasks()
        assert len(result) == 1
        assert result[0]['title'] == "Comprar pan"
        assert result[0]['done'] is False