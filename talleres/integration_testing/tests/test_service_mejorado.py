import os
import pytest
from unittest.mock import MagicMock
from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

class TestRobustIntegration:

    @pytest.fixture
    def setup_system(self, tmp_path):
        """Fixture para obtener instancias limpias y reales con un entorno aislado."""
        db_file = str(tmp_path / "robust_tasks.json")
        storage = TaskStorage(db_file)
        notifier = Notifier()
        service = TaskService(storage, notifier)
        return service, storage, db_file

    # 1. DETECCIÓN DE LA MODIFICACIÓN MALICIOSA
    
    def test_add_task_detects_malicious_bypass(self, setup_system):
        """
        Este test fallará inmediatamente con la tranpa de add_task
        """
        service, storage, _ = setup_system
        
        result = service.add_task("Verificar persistencia")
        
        assert result is True
        # Si add_task solo devuelve True sin guardar, la siguiente línea hará fallar el test:
        tasks_in_disk = storage.load()
        assert len(tasks_in_disk) == 1
        assert tasks_in_disk[0]["title"] == "Verificar persistencia"

    # 2. ESCENARIOS DE ERROR (EXCEPCIONES)
    
    def test_storage_save_throws_io_error(self, setup_system):
        """Simula un fallo catastrófico en el almacenamiento como el disco lleno."""
        service, _, _ = setup_system
        
        # Forzamos al storage real a lanzar un IOError al intentar salvar
        service.storage.save = MagicMock(side_effect=IOError("Disco lleno o sin permisos"))
        
        # El servicio debería propagar el error o manejarlo 
        with pytest.raises(IOError):
            service.add_task("Guardar en disco roto")

    def test_notifier_throws_connection_error(self, setup_system):
        """Simula que el notificador pierde conexión con el servidor SMTP/API."""
        service, _, _ = setup_system
        
        # Forzamos al notifier real a lanzar un ConnectionError
        service.notifier.send = MagicMock(side_effect=ConnectionError("No se pudo enviar la notificación"))
        
        # El código actual de Service no maneja este error, por lo que la excepción se propaga
        with pytest.raises(ConnectionError):
            service.add_task("Notificación fallida")

    # 3. CONSISTENCIA DE ESTADO (TRANSACCIONALIDAD)
    
    def test_consistency_when_notifier_fails(self, setup_system):
        """
        ANÁLISIS DE CONSISTENCIA: Si el notificador falla, el sistema ideal DEBERÍA revertir
        la operación (Rollback) para mantener consistencia.
        """
        service, storage, _ = setup_system
        service.notifier.send = MagicMock(side_effect=ConnectionError("Fallo de red"))
        
        # Ejecutamos esperando que falle por la excepción
        with pytest.raises(ConnectionError):
            service.add_task("Tarea fantasma")
            
        # VALIDACIÓN DE CONSISTENCIA: Si la operación falló, la tarea NO debió quedar guardada.
        assert len(storage.load()) == 0

    # 4. CASOS EXTREMOS Y DE NEGOCIO
    def test_add_task_empty_title_policy(self, setup_system):
        """
        POLÍTICA DEFINIDA: El servicio debe rechazar títulos vacíos devolviendo False
        o lanzando un ValueError.
        """
        service, storage, _ = setup_system
        
        result = service.add_task("")
        
        assert result is False
        assert len(storage.load()) == 0

    def test_add_duplicate_tasks(self, setup_system):
        """Valida que no se dupliquen tareas y que devuelva False correctamente."""
        service, storage, _ = setup_system
        
        # Primer intento exitoso
        assert service.add_task("Estudiar Integración") is True
        # Segundo intento duplicado
        assert service.add_task("Estudiar Integración") is False
        
        # Verificar que en el almacenamiento físico solo exista UNA instancia
        assert len(storage.load()) == 1

    def test_list_tasks_when_file_is_empty(self, setup_system):
        """Valida el comportamiento de listado cuando no hay datos previos."""
        service, _, _ = setup_system
        
        # Al inicializarse el entorno temporal, la lista debe ser vacía de manera segura
        tasks = service.list_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) == 0