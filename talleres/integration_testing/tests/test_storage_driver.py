# Prueba bottom-up (driver) para el módulo de almacenamiento TaskStorage
# Implementado por: Jovany Gutierrez Vergara (Código: 12242217515).

import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage

# Ruta absoluta temporal para el archivo de pruebas
TEST_DRIVER_PATH = os.path.join(tempfile.gettempdir(), "test_driver.json")

def setup_function():
    # Limpieza previa antes de cada test para asegurar aislamiento
    if os.path.exists(TEST_DRIVER_PATH):
        try:
            os.remove(TEST_DRIVER_PATH)
        except Exception:
            pass

def teardown_function():
    # Limpieza posterior después de cada test
    if os.path.exists(TEST_DRIVER_PATH):
        try:
            os.remove(TEST_DRIVER_PATH)
        except Exception:
            pass

# ==============================================================================
# 🔽 ENFOQUE BOTTOM-UP TESTING (DRIVERS DIRECTOS)
# ==============================================================================

def test_storage_file_does_not_exist_creates_empty_list():
    """
    Caso 1: Si el archivo JSON no existe en disco, al inicializar el driver
    debe crearse físicamente un archivo que contenga una lista vacía [].
    """
    assert not os.path.exists(TEST_DRIVER_PATH)
    
    # Inicialización del almacenamiento
    storage = TaskStorage(TEST_DRIVER_PATH)
    
    # Verificar que el archivo fue creado y contiene una lista vacía
    assert os.path.exists(TEST_DRIVER_PATH)
    data = storage.load()
    assert isinstance(data, list)
    assert len(data) == 0

def test_storage_save_and_retrieve_single_task():
    """
    Caso 2: Guardar una única tarea en el archivo y recuperarla.
    Verifica la serialización y deserialización correcta del Driver.
    """
    storage = TaskStorage(TEST_DRIVER_PATH)
    task_list = [{"title": "Aprender Bottom-Up", "done": False}]
    
    storage.save(task_list)
    
    loaded_data = storage.load()
    assert len(loaded_data) == 1
    assert loaded_data[0]["title"] == "Aprender Bottom-Up"
    assert loaded_data[0]["done"] is False

def test_storage_save_and_retrieve_multiple_tasks():
    """
    Caso 3: Guardar y recuperar múltiples tareas en el archivo, asegurando
    que se mantiene la estructura de datos, orden e integridad de la colección.
    """
    storage = TaskStorage(TEST_DRIVER_PATH)
    task_list = [
        {"title": "Tarea 1", "done": False},
        {"title": "Tarea 2", "done": True},
        {"title": "Tarea 3", "done": False}
    ]
    
    storage.save(task_list)
    
    loaded_data = storage.load()
    assert len(loaded_data) == 3
    assert loaded_data[0]["title"] == "Tarea 1"
    assert loaded_data[1]["done"] is True
    assert loaded_data[2]["title"] == "Tarea 3"

def test_storage_attempt_save_empty_title():
    """
    Caso 4: Intento de guardar un título vacío.
    
    DEFINICIÓN DE LA POLÍTICA:
    Como buena práctica de arquitectura de software (Clean Architecture), el módulo
    TaskStorage representa la capa de infraestructura y persistencia de bajo nivel.
    Su única responsabilidad es serializar y deserializar colecciones hacia el archivo.
    Por lo tanto, la política elegida es que la capa de Storage es AGNOSTICA a las reglas
    de negocio y permite guardar cualquier título (incluido vacío o con espacios), delegando
    esta validación exclusivamente a la capa de lógica de negocio (TaskService).
    
    Este test verifica que el Driver funciona correctamente persistiendo los datos de
    infraestructura sin bloquearlos, garantizando que el diseño está correctamente desacoplado.
    """
    storage = TaskStorage(TEST_DRIVER_PATH)
    task_list = [{"title": "", "done": False}]
    
    # El almacenamiento debe persistir con éxito
    storage.save(task_list)
    
    loaded_data = storage.load()
    assert len(loaded_data) == 1
    assert loaded_data[0]["title"] == ""
