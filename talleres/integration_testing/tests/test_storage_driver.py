import os
import pytest
from src.storage import TaskStorage

class TestStorageDriver:
    
    # Usamos tmp_path de pytest para que cree un archivo JSON único y temporal por test
    @pytest.fixture
    def temp_storage(self, tmp_path):
        db_file = tmp_path / "tasks.json"
        return TaskStorage(str(db_file)), str(db_file)

    def test_file_does_not_exist_creates_empty_list(self, temp_storage):
        storage, filepath = temp_storage
        # Caso 1: El archivo debe existir y contener una lista vacía al inicializarse
        assert os.path.exists(filepath)
        assert storage.load() == []

    def test_save_and_load_single_task(self, temp_storage):
        storage, _ = temp_storage
        task_data = [{"title": "Lavar platos", "done": False}]
        
        # Caso 2: Guardar y recuperar una tarea
        storage.save(task_data)
        assert storage.load() == task_data

    def test_save_and_load_multiple_tasks(self, temp_storage):
        storage, _ = temp_storage
        tasks_data = [
            {"title": "Tarea 1", "done": False},
            {"title": "Tarea 2", "done": True},
            {"title": "Tarea 3", "done": False}
        ]
        
        # Caso 3: Guardar y recuperar múltiples tareas
        storage.save(tasks_data)
        assert len(storage.load()) == 3
        assert storage.load()[1]["title"] == "Tarea 2"

    def test_save_empty_title_policy(self, temp_storage):
        storage, _ = temp_storage
        invalid_data = [{"title": "", "done": False}]
        
        # Caso 4: Política definida -> El almacenamiento acepta cadenas vacías 
        # porque su única responsabilidad es serializar JSON, no la lógica de negocio.
        storage.save(invalid_data)
        loaded_data = storage.load()
        assert loaded_data[0]["title"] == ""