"""
Driver de pruebas de integración - Enfoque Bottom-Up (Parte 4.2 y Parte 5)
Prueba de manera aislada el componente TaskStorage ante escenarios normales y extremos.
"""

import sys
import os
import pytest

# Asegurar que el path detecte la carpeta 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage

# Nombre del archivo JSON temporal que usaremos exclusivamente para pruebas
TEST_FILE = "test_driver_storage.json"

@pytest.fixture(autouse=True)
def clean_test_environment():
    """Fixture para asegurar un entorno limpio antes y después de cada test."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


class TestStorageDriver:

    def test_file_does_not_exist_initialization(self):
        """1. Archivo no existe: debe crearse automáticamente con una lista vacía."""
        storage = TaskStorage(TEST_FILE)
        assert os.path.exists(TEST_FILE) is True
        
        data = storage.load()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_save_and_load_single_task(self):
        """2. Guardar y recuperar una única tarea de forma correcta."""
        storage = TaskStorage(TEST_FILE)
        task_structure = [{"title": "Lavar la ropa", "done": False}]
        
        storage.save(task_structure)
        
        loaded_data = storage.load()
        assert len(loaded_data) == 1
        assert loaded_data[0]["title"] == "Lavar la ropa"
        assert loaded_data[0]["done"] is False

    def test_save_and_load_multiple_tasks(self):
        """3. Guardar y recuperar múltiples tareas manteniendo consistencia y orden."""
        storage = TaskStorage(TEST_FILE)
        tasks_structure = [
            {"title": "Estudiar Calidad UAN", "done": False},
            {"title": "Cocinar el almuerzo", "done": True},
            {"title": "Hacer calistenia", "done": False}
        ]
        
        storage.save(tasks_structure)
        
        loaded_data = storage.load()
        assert len(loaded_data) == 3
        assert loaded_data[0]["title"] == "Estudiar Calidad UAN"
        assert loaded_data[1]["done"] is True
        assert loaded_data[2]["title"] == "Hacer calistenia"

    def test_save_empty_title_policy(self):
        """4. Título vacío: El storage lo permite por ser un JSON válido."""
        storage = TaskStorage(TEST_FILE)
        corrupted_task = [{"title": "", "done": False}]
        
        storage.save(corrupted_task)
        
        loaded_data = storage.load()
        assert len(loaded_data) == 1
        assert loaded_data[0]["title"] == "" 

    # =========================================================================
    # CASOS EXTREMOS DE PERSISTENCIA - PARTE 5
    # =========================================================================

    def test_file_is_empty_corrupted_policy(self):
        """Parte 5: Caso extremo donde el archivo JSON existe pero está totalmente vacío (0 bytes)."""
        # Forzar la creación de un archivo físico en blanco sin formato JSON válido
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write("") 
            
        storage = TaskStorage(TEST_FILE)
        
        # Gracias a la programación defensiva en storage.py, el capturador JSONDecodeError
        # debe evitar que la app explote y retornar un arreglo funcional vacío []
        loaded_data = storage.load()
        assert isinstance(loaded_data, list)
        assert len(loaded_data) == 0