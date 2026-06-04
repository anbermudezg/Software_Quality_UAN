from unittest.mock import Mock
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.service import TaskService

class TestTopDown:
    def test_add_task_exitoso_llama_storage_y_notifier(self):
        storage_stub = Mock()
        notifier_stub = Mock()
        storage_stub.load.return_value = []
        service = TaskService(storage_stub, notifier_stub)
        result = service.add_task("Comprar pan")
        assert result is True
        storage_stub.load.assert_called_once()
        storage_stub.save.assert_called_once_with([{"title": "Comprar pan", "done": False}])
        notifier_stub.send.assert_called_once_with("Tarea 'Comprar pan' creada")

    def test_add_task_duplicado_no_guarda(self):
        storage_stub = Mock()
        notifier_stub = Mock()
        storage_stub.load.return_value = [{"title": "Comprar pan", "done": False}]
        service = TaskService(storage_stub, notifier_stub)
        result = service.add_task("Comprar pan")
        assert result is False
        storage_stub.save.assert_not_called()
        notifier_stub.send.assert_not_called()

    def test_add_task_si_falla_notifier_aun_guarda(self):
        storage_stub = Mock()
        notifier_stub = Mock()
        storage_stub.load.return_value = []
        notifier_stub.send.side_effect = Exception("Error de red")
        service = TaskService(storage_stub, notifier_stub)
        result = service.add_task("Tarea importante")
        assert result is True
        storage_stub.save.assert_called_once()

    def test_complete_task_exitoso_marca_done(self):
        storage_stub = Mock()
        notifier_stub = Mock()
        storage_stub.load.return_value = [{"title": "Tarea 1", "done": False}]
        service = TaskService(storage_stub, notifier_stub)
        result = service.complete_task("Tarea 1")
        assert result is True
        storage_stub.save.assert_called_once_with([{"title": "Tarea 1", "done": True}])

    def test_complete_task_tarea_no_existe(self):
        storage_stub = Mock()
        notifier_stub = Mock()
        storage_stub.load.return_value = [{"title": "Tarea 1", "done": False}]
        service = TaskService(storage_stub, notifier_stub)
        result = service.complete_task("Tarea inexistente")
        assert result is False
        storage_stub.save.assert_not_called()