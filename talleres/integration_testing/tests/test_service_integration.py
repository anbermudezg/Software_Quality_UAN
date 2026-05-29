import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

# Ruta temporal absoluta para evitar problemas de permisos de escritura (Controlled Folder Access)
TEST_JSON_PATH = os.path.join(tempfile.gettempdir(), "test_tasks.json")

# ==============================================================================
# 🧩 STUBS MANUALES PARA ENFOQUES DE INTEGRACIÓN
# ==============================================================================

class StorageStub:
    def __init__(self, tasks=None):
        self.tasks = tasks if tasks is not None else []
        self.save_called = False
        self.last_saved_tasks = None

    def load(self):
        return self.tasks

    def save(self, tasks):
        self.save_called = True
        self.last_saved_tasks = tasks
        self.tasks = tasks

class FailsStorageStub:
    def load(self):
        return []

    def save(self, tasks):
        raise IOError("Fallo simulado en disco")

class NotifierStub:
    def __init__(self):
        self.send_called = False
        self.last_message = None
        self.should_fail = False

    def send(self, message):
        self.send_called = True
        self.last_message = message
        if self.should_fail:
            raise ConnectionError("No se pudo enviar la notificación")

# ==============================================================================
# 🔼 ENFOQUE TOP-DOWN TESTING
# ==============================================================================

class TestTopDown:
    """
    Valida la lógica de negocio de Service de forma aislada utilizando
    stubs para simular Storage y Notifier sin tocar el disco ni la red.
    """
    def test_add_task_success_calls_dependencies_correctly(self):
        storage = StorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        result = service.add_task("Aprender Top-Down")
        
        assert result is True
        # Verifica la interacción correcta con los stubs
        assert storage.save_called is True
        assert len(storage.last_saved_tasks) == 1
        assert storage.last_saved_tasks[0]["title"] == "Aprender Top-Down"
        assert notifier.send_called is True
        assert notifier.last_message == "Tarea 'Aprender Top-Down' creada"

    def test_add_task_duplicate_does_not_persist_or_notify(self):
        # Stub precargado con una tarea
        storage = StorageStub(tasks=[{"title": "Tarea Duplicada", "done": False}])
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        result = service.add_task("Tarea Duplicada")
        
        assert result is False
        assert storage.save_called is False
        assert notifier.send_called is False

    def test_add_task_empty_title_does_not_persist_or_notify(self):
        storage = StorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        result = service.add_task("   ")
        
        assert result is False
        assert storage.save_called is False
        assert notifier.send_called is False

# ==============================================================================
# 🔀 ENFOQUE SANDWICH TESTING
# ==============================================================================

class TestSandwich:
    """
    Combina módulos reales (Storage en archivo real) con Stubs (Notifier)
    para probar de manera mixta la integración parcial y la persistencia real.
    """
    def setup_method(self):
        # Limpieza previa del archivo físico antes de cada prueba
        if os.path.exists(TEST_JSON_PATH):
            try:
                os.remove(TEST_JSON_PATH)
            except Exception:
                pass

    def teardown_method(self):
        # Limpieza posterior
        if os.path.exists(TEST_JSON_PATH):
            try:
                os.remove(TEST_JSON_PATH)
            except Exception:
                pass

    def test_sandwich_add_task_success_persists_in_real_storage_and_notifies(self):
        storage = TaskStorage(TEST_JSON_PATH)
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        result = service.add_task("Tarea Sandwich Real")
        
        assert result is True
        
        # 1. Verificar persistencia física real leyendo el archivo a través del storage
        loaded_tasks = storage.load()
        assert len(loaded_tasks) == 1
        assert loaded_tasks[0]["title"] == "Tarea Sandwich Real"
        assert loaded_tasks[0]["done"] is False
        
        # 2. Verificar llamada al notifier stub (aislamiento de red)
        assert notifier.send_called is True
        assert notifier.last_message == "Tarea 'Tarea Sandwich Real' creada"

    def test_sandwich_add_task_fails_on_duplicate_and_does_not_persist(self):
        storage = TaskStorage(TEST_JSON_PATH)
        # Pre-guardar una tarea en el almacenamiento real
        storage.save([{"title": "Tarea Duplicada", "done": False}])
        
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        result = service.add_task("Tarea Duplicada")
        assert result is False
        
        # Verificar que no se duplicó
        loaded_tasks = storage.load()
        assert len(loaded_tasks) == 1
        assert notifier.send_called is False

# ==============================================================================
# 🧪 MEJORA DE COBERTURA Y CASOS DE ERROR
# ==============================================================================

class TestIntegrationRobustness:
    """
    Pruebas mejoradas enfocadas en robustez, consistencia transaccional (rollback),
    y casos extremos bajo fallos reales o simulados.
    """
    def setup_method(self):
        if os.path.exists(TEST_JSON_PATH):
            try:
                os.remove(TEST_JSON_PATH)
            except Exception:
                pass

    def teardown_method(self):
        if os.path.exists(TEST_JSON_PATH):
            try:
                os.remove(TEST_JSON_PATH)
            except Exception:
                pass

    def test_storage_failure_propagates_exception_and_does_not_notify(self):
        """Si el almacenamiento físico falla al guardar, se aborta y no se notifica."""
        storage = FailsStorageStub()
        notifier = NotifierStub()
        service = TaskService(storage, notifier)
        
        import pytest
        with pytest.raises(IOError, match="Fallo simulado en disco"):
            service.add_task("Tarea Fallida")
            
        assert notifier.send_called is False

    def test_notifier_failure_triggers_rollback_in_real_storage(self):
        """
        Consistencia Transaccional: Si el notificador falla, se debe deshacer (rollback)
        la inserción de la tarea en el almacenamiento real.
        """
        storage = TaskStorage(TEST_JSON_PATH)
        assert len(storage.load()) == 0  # Inicialmente vacío
        
        notifier = NotifierStub()
        notifier.should_fail = True      # Simular fallo ConnectionError
        
        service = TaskService(storage, notifier)
        
        import pytest
        with pytest.raises(ConnectionError, match="No se pudo enviar la notificación"):
            service.add_task("Tarea con Fallo de Notificación")
            
        # El rollback debe haber restaurado el estado vacío del storage
        loaded_tasks = storage.load()
        assert len(loaded_tasks) == 0

    def test_list_tasks_when_file_does_not_exist(self):
        """El sistema debe ser robusto y retornar lista vacía si el archivo JSON no existe."""
        if os.path.exists(TEST_JSON_PATH):
            os.remove(TEST_JSON_PATH)
            
        storage = TaskStorage(TEST_JSON_PATH)
        service = TaskService(storage, NotifierStub())
        
        assert service.list_tasks() == []
