"""
Pruebas bottom-up del módulo Storage mediante un driver.
No utiliza TaskService.
"""

import json
import os

from src.storage import TaskStorage


class StorageDriver:
    def __init__(self, filepath):
        self.filepath = filepath
        self.storage = TaskStorage(filepath)

    def when_save(self, tasks):
        self.storage.save(tasks)
        return self

    def when_load(self):
        return self.storage.load()

    def then_file_contains(self, expected):
        with open(self.filepath, "r") as f:
            assert json.load(f) == expected


def test_creates_empty_file_when_missing(temp_json_path):
    assert not os.path.exists(temp_json_path)
    driver = StorageDriver(temp_json_path)
    assert driver.when_load() == []
    assert os.path.exists(temp_json_path)


def test_save_and_load_single_task(temp_json_path):
    task = [{"title": "Una tarea", "done": False}]
    driver = StorageDriver(temp_json_path)
    driver.when_save(task)
    assert driver.when_load() == task
    driver.then_file_contains(task)


def test_save_and_load_multiple_tasks(temp_json_path):
    tasks = [
        {"title": "Primera", "done": False},
        {"title": "Segunda", "done": True},
    ]
    driver = StorageDriver(temp_json_path)
    driver.when_save(tasks)
    loaded = driver.when_load()
    assert len(loaded) == 2
    assert loaded[1]["done"] is True


def test_empty_title_allowed_at_storage_level(temp_json_path):
    """Storage persiste vacíos; Service rechaza títulos vacíos."""
    driver = StorageDriver(temp_json_path)
    driver.when_save([{"title": "", "done": False}])
    assert driver.when_load() == [{"title": "", "done": False}]
