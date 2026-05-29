import sys, os
import tempfile
import json
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier

class TestServiceIntegrationImproved:
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.filepath = self.temp_file.name
        self.storage_real = TaskStorage(self.filepath)
        self.notifier_stub = Mock()
        self.service = TaskService(self.storage_real, self.notifier_stub)

    def teardown_method(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    # Prueba que detecta la modificacion maliciosa (Parte 3)
    def test_detecta_que_add_task_usa_storage_real(self):
        service_con_storage_real = TaskService(self.storage_real, self.notifier_stub)
        service_con_storage_real.add_task("Tarea detectada")
        
        # Verifica que realmente se guardo en el archivo
        with open(self.filepath, 'r') as f:
            contenido = f.read()
            assert "Tarea detectada" in contenido

    # Escenario de error: fallo en storage.save
    def test_fallo_en_storage_no_guarda_tarea(self):
        storage_con_fallo = Mock()
        storage_con_fallo.load.return_value = []
        storage_con_fallo.save.side_effect = IOError("Disco lleno")
        
        service = TaskService(storage_con_fallo, self.notifier_stub)
        result = service.add_task("Tarea que fallara")
        
        assert result is False
        self.notifier_stub.send.assert_not_called()

    # Escenario de error: fallo en notifier (ConnectionError)
    def test_fallo_en_notifier_tarea_si_se_guarda(self):
        self.notifier_stub.send.side_effect = ConnectionError("Error de red")
        
        result = self.service.add_task("Tarea con fallo en notificacion")
        
        # Decisión tomada: la tarea SI se guarda aunque falle notifier
        assert result is True
        tareas = self.storage_real.load()
        assert len(tareas) == 1
        assert tareas[0]["title"] == "Tarea con fallo en notificacion"

    # Caso extremo: titulo vacio
    def test_titulo_vacio_debe_ser_rechazado(self):
        result = self.service.add_task("")
        assert result is False
        tareas = self.storage_real.load()
        assert len(tareas) == 0

    def test_titulo_con_solo_espacios_debe_ser_rechazado(self):
        result = self.service.add_task("   ")
        assert result is False
        tareas = self.storage_real.load()
        assert len(tareas) == 0

    # Caso extremo: tareas duplicadas
    def test_tarea_duplicada_retorna_false_y_no_duplica(self):
        result1 = self.service.add_task("Tarea unica")
        result2 = self.service.add_task("Tarea unica")
        
        assert result1 is True
        assert result2 is False
        tareas = self.storage_real.load()
        assert len(tareas) == 1

    # Caso extremo: listar tareas cuando archivo esta vacio
    def test_listar_tareas_cuando_archivo_vacio(self):
        tareas = self.service.list_tasks()
        assert tareas == []

    # Caso extremo: listar tareas cuando archivo no existe
    def test_listar_tareas_cuando_archivo_no_existe(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        tareas = self.service.list_tasks()
        assert tareas == []

    # Prueba de consistencia: cuando notifier falla, la tarea queda guardada
    # Esto verifica el comportamiento esperado definido
    def test_consistencia_si_notifier_falla_tarea_persiste(self):
        self.notifier_stub.send.side_effect = Exception("Fallo")
        
        self.service.add_task("Tarea consistente")
        
        tareas = self.storage_real.load()
        assert len(tareas) == 1
        assert tareas[0]["title"] == "Tarea consistente"