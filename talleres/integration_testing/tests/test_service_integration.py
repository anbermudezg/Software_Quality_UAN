from unittest.mock import MagicMock
from src.service import TaskService
import os
from unittest.mock import MagicMock
from src.storage import TaskStorage
from src.service import TaskService

class TestTopDown:
    def test_service_logic_with_stubs(self):
        # 1. Crear STUBS para los módulos inferiores
        stub_storage = MagicMock()
        stub_notifier = MagicMock()
        
        # Configuramos el stub de almacenamiento para que devuelva una lista vacía al cargar
        stub_storage.load.return_value = []
        
        # 2. Instanciar el servicio con los stubs
        service = TaskService(storage=stub_storage, notifier=stub_notifier)
        
        # 3. Actuar
        result = service.add_task("Diseñar arquitectura")
        
        # 4. Asertar lógica del servicio
        assert result is True
        
        # 5. VERIFICAR INTEGRACIÓN: ¿Se llamó a los módulos inferiores con los parámetros correctos?
        stub_storage.save.assert_called_once_with([{"title": "Diseñar arquitectura", "done": False}])
        stub_notifier.send.assert_called_once_with("Tarea 'Diseñar arquitectura' creada")

    def test_service_duplicate_task_top_down(self):
        stub_storage = MagicMock()
        stub_notifier = MagicMock()
        
        # El stub simula que la tarea ya existe
        stub_storage.load.return_value = [{"title": "Repetida", "done": False}]
        
        service = TaskService(storage=stub_storage, notifier=stub_notifier)
        result = service.add_task("Repetida")
        
        # Validar que frena el flujo y NO guarda ni notifica
        assert result is False
        stub_storage.save.assert_not_called()
        stub_notifier.send.assert_not_called()
        
class TestSandwichApproach:
    
    def test_sandwich_integration_happy_path(self, tmp_path):
        # 1. Componente Real (Almacenamiento temporal en disco)
        db_file = str(tmp_path / "sandwich_tasks.json")
        real_storage = TaskStorage(db_file)
        
        # 2. Componente Stub (Aislamos el peligroso random del Notifier y la red)
        stub_notifier = MagicMock()
        
        # 3. Componente Central bajo prueba
        service = TaskService(storage=real_storage, notifier=stub_notifier)
        
        # Ejecución
        result = service.add_task("Hacer mercado")
        
        # ASERCIONES INTEGRADAS:
        assert result is True
        # Verifica que el almacenamiento REAL persistió el dato en el disco duro
        assert os.path.exists(db_file)
        assert len(real_storage.load()) == 1
        assert real_storage.load()[0]["title"] == "Hacer mercado"
        
        # Verifica que el notificador STUB recibió la señal correcta sin activar código real
        stub_notifier.send.assert_called_once_with("Tarea 'Hacer mercado' creada")

    def test_sandwich_complete_task_persistence(self, tmp_path):
        db_file = str(tmp_path / "sandwich_tasks.json")
        real_storage = TaskStorage(db_file)
        stub_notifier = MagicMock()
        
        service = TaskService(storage=real_storage, notifier=stub_notifier)
        
        # Añadir tarea e inmediatamente completarla
        service.add_task("Estudiar para examen")
        result_complete = service.complete_task("Estudiar para examen")
        
        # Verificar la persistencia del cambio de estado real en el JSON
        assert result_complete is True
        assert real_storage.load()[0]["done"] is True