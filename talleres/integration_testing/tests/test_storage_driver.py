import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage


# Driver simple: probamos storage directo, sin pasar por el servicio.
def test_storage_creates_empty_file_when_missing(tmp_path):
    storage_path = tmp_path / "driver_tasks.json"

    # Si no existe, el storage lo crea vacío.
    storage = TaskStorage(str(storage_path))

    assert storage.load() == []


def test_storage_save_and_load_single_task(tmp_path):
    storage_path = tmp_path / "driver_tasks.json"
    storage = TaskStorage(str(storage_path))

    # Guardamos una tarea y luego la leemos otra vez.
    storage.save([{"title": "Test", "done": False}])

    assert storage.load() == [{"title": "Test", "done": False}]


def test_storage_save_and_load_multiple_tasks(tmp_path):
    storage_path = tmp_path / "driver_tasks.json"
    storage = TaskStorage(str(storage_path))
    tasks = [
        {"title": "Una", "done": False},
        {"title": "Dos", "done": True},
    ]

    # Probamos que varias tareas también quedan bien guardadas.
    storage.save(tasks)

    assert storage.load() == tasks


def test_storage_allows_roundtrip_of_empty_title_policy(tmp_path):
    storage_path = tmp_path / "driver_tasks.json"
    storage = TaskStorage(str(storage_path))
    tasks = [{"title": "", "done": False}]

    # El storage no decide la regla, solo guarda lo que recibe.
    storage.save(tasks)

    with open(storage_path, "r", encoding="utf-8") as file_handle:
        assert json.load(file_handle) == tasks
    assert storage.load() == tasks