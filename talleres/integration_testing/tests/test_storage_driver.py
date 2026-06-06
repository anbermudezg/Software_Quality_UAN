# Pruebas bottom-up con driver – prueba del módulo Storage aislado
import sys, os, tempfile, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage

def make_temp_file():
    f = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    f.close()
    os.unlink(f.name)
    return f.name

def test_storage_file_created_when_not_exists():
    path = make_temp_file()
    try:
        storage = TaskStorage(path)
        storage.save([{"title": "Test", "done": False}])
        data = storage.load()
        assert len(data) == 1
    finally:
        if os.path.exists(path): os.unlink(path)

def test_storage_save_and_load():
    path = make_temp_file()
    try:
        storage = TaskStorage(path)
        storage.save([{"title": "Test", "done": False}])
        data = storage.load()
        assert len(data) == 1
        assert data[0]["title"] == "Test"
    finally:
        if os.path.exists(path): os.unlink(path)

def test_storage_multiple_tasks():
    path = make_temp_file()
    try:
        storage = TaskStorage(path)
        storage.save([
            {"title": "Tarea 1", "done": False},
            {"title": "Tarea 2", "done": True},
            {"title": "Tarea 3", "done": False}
        ])
        data = storage.load()
        assert len(data) == 3
    finally:
        if os.path.exists(path): os.unlink(path)

def test_storage_empty_title():
    path = make_temp_file()
    try:
        storage = TaskStorage(path)
        storage.save([{"title": "", "done": False}])
        data = storage.load()
        assert len(data) == 1
        assert data[0]["title"] == ""
    finally:
        if os.path.exists(path): os.unlink(path)