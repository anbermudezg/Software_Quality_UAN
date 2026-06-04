"""
Pruebas de integración - Enfoque Sandwich (Parte 4.3)
Combina el componente real TaskStorage con un Stub de Notifier.
"""

import sys
import os
import pytest

# Asegurar que el path detecte la carpeta 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService
from src.storage import TaskStorage

# Stub manual para el Notifier (Aísla la red simulada)
class NotifierSandwichStub:
    def __init__(self):
        self.last_message = None
        self.send_called_count = 0

    def send(self, message):
        self.last_message = message
        self.send_called_count += 1


class TestSandwichIntegration:
    SANDWICH_FILE = "test_sandwich_tasks.json"

    @pytest.fixture(autouse=True)
    def clean_test_environment(self):
        """Fixture para limpiar el archivo JSON temporal antes y después de cada test."""
        if os.path.exists(self.SANDWICH_FILE):
            os.remove(self.SANDWICH_FILE)
        yield
        if os.path.exists(self.SANDWICH_FILE):
            os.remove(self.SANDWICH_FILE)

    def test_sandwich_flow_success(self):
        """1. Verifica que Service persiste en el Storage real y el Notifier recibe la llamada."""
        # Configuración "Sandwich": Storage REAL + Notifier STUB
        real_storage = TaskStorage(self.SANDWICH_FILE)
        notifier_stub = NotifierSandwichStub()
        service = TaskService(real_storage, notifier_stub)

        # Acción
        result = service.add_task("Validar enfoque Sandwich")

        # Validaciones
        assert result is True
        
        # A) Validar que el Notifier Stub capturó la llamada de red de forma segura
        assert notifier_stub.send_called_count == 1
        assert notifier_stub.last_message == "Tarea 'Validar enfoque Sandwich' creada"
        
        # B) Validar que el Storage REAL guardó físicamente el archivo en el disco
        assert os.path.exists(self.SANDWICH_FILE) is True
        tasks_in_disk = real_storage.load()
        assert len(tasks_in_disk) == 1
        assert tasks_in_disk[0]["title"] == "Validar enfoque Sandwich"
        assert tasks_in_disk[0]["done"] is False

    def test_sandwich_duplicate_prevents_notification(self):
        """2. Verifica que una tarea duplicada no altera el Storage real ni notifica."""
        real_storage = TaskStorage(self.SANDWICH_FILE)
        notifier_stub = NotifierSandwichStub()
        service = TaskService(real_storage, notifier_stub)

        # Pre-cargar una tarea en la base de datos real
        real_storage.save([{"title": "Tarea Repetida", "done": False}])

        # Intentar agregar el duplicado
        result = service.add_task("Tarea Repetida")

        # Validaciones
        assert result is False
        
        # El stub del notificador debió quedarse en 0 llamadas (no gasta red)
        assert notifier_stub.send_called_count == 0
        
        # El storage real debió mantener únicamente la tarea original sin duplicar
        assert len(real_storage.load()) == 1