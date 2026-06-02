# Prueba básica bottom-up (driver) – versión inicial débil
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage

def test_storage_save_and_load():
    storage = TaskStorage("test_driver.json")
    storage.save([{"title": "Test", "done": False}])
    data = storage.load()
    assert len(data) == 1 
    assert data[0]['title'] == "Test"
    assert data[0]['done'] is False

def test_storage_load_empty():
    storage = TaskStorage("test_driver_empty.json")
    data = storage.load()
    assert data == []
    assert isinstance(data, list)

def test_storage_overwrite():
    storage = TaskStorage("test_driver_overwrite.json")
    storage.save([{"title": "First", "done": False}])
    storage.save([{"title": "Second", "done": True}])
    data = storage.load()
    assert len(data) == 1
    assert data[0]['title'] == "Second"
    assert data[0]['done'] is True

def teardown_module():
    """Limpia los archivos de prueba después de la ejecución."""
    for filename in ["test_driver.json", "test_driver_empty.json", "test_driver_overwrite.json"]:
        if os.path.exists(filename):
            os.remove(filename)