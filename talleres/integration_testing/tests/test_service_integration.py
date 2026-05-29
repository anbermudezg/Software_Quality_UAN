"""
Pruebas de integración para TaskService.
Implementa enfoques Top-Down y Sandwich con stubs.
"""
import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier


# ─────────────────────────────────────────────
# Stubs reutilizables
# ─────────────────────────────────────────────

class StubStorage:
    """Stub de TaskStorage: almacena tareas en memoria."""

    def __init__(self):
        self._tasks = []
        self.save_called_with = None
        self.load_call_count = 0

    def load(self):
        self.load_call_count += 1
        return list(self._tasks)

    def save(self, tasks):
        self.save_called_with = list(tasks)
        self._tasks = list(tasks)


class StubStorageRaisesOnSave:
    """Stub que lanza IOError al intentar guardar."""

    def __init__(self):
        self._tasks = []

    def load(self):
        return list(self._tasks)

    def save(self, tasks):
        raise IOError("Fallo simulado de escritura en disco")


class StubNotifier:
    """Stub de Notifier: registra mensajes sin efecto real."""

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class StubNotifierRaises:
    """Stub que lanza ConnectionError al enviar."""

    def send(self, message):
        raise ConnectionError("Fallo simulado de red")


# ─────────────────────────────────────────────
# Parte 4.1 – Enfoque Top-Down
# ─────────────────────────────────────────────

class TestTopDown:
    """
    Prueba Service en aislamiento usando stubs de Storage y Notifier.
    Valida la lógica interna sin depender de implementaciones reales.
    """

    def setup_method(self):
        self.storage = StubStorage()
        self.notifier = StubNotifier()
        self.service = TaskService(self.storage, self.notifier)

    # ── add_task básico ──────────────────────────────────────────────

    def test_add_task_retorna_true_y_persiste(self):
        result = self.service.add_task("Estudiar pytest")
        assert result is True
        # Verifica que storage.save fue llamado con la tarea correcta
        assert self.storage.save_called_with is not None
        titles = [t["title"] for t in self.storage.save_called_with]
        assert "Estudiar pytest" in titles

    def test_add_task_envia_notificacion(self):
        self.service.add_task("Comprar leche")
        assert len(self.notifier.messages) == 1
        assert "Comprar leche" in self.notifier.messages[0]

    def test_add_task_duplicado_retorna_false(self):
        self.service.add_task("Tarea X")
        result = self.service.add_task("Tarea X")
        assert result is False

    def test_add_task_duplicado_no_persiste_segunda_vez(self):
        self.service.add_task("Tarea X")
        first_save = list(self.storage.save_called_with)
        self.service.add_task("Tarea X")
        # save_called_with no debe haber cambiado (no se llamó save de nuevo)
        assert self.storage.save_called_with == first_save

    def test_add_task_titulo_vacio_rechazado(self):
        """
        Política definida: título vacío debe retornar False y no persistir.
        Detecta el error de integración documentado en service.py.
        """
        result = self.service.add_task("")
        assert result is False
        assert self.storage.save_called_with is None  # nunca se guardó

    # ── complete_task ────────────────────────────────────────────────

    def test_complete_task_existente(self):
        self.service.add_task("Lavar platos")
        result = self.service.complete_task("Lavar platos")
        assert result is True
        task = next(t for t in self.storage.save_called_with if t["title"] == "Lavar platos")
        assert task["done"] is True

    def test_complete_task_inexistente(self):
        result = self.service.complete_task("No existe")
        assert result is False

    # ── list_tasks ───────────────────────────────────────────────────

    def test_list_tasks_vacio(self):
        tasks = self.service.list_tasks()
        assert tasks == []

    def test_list_tasks_despues_de_agregar(self):
        self.service.add_task("T1")
        self.service.add_task("T2")
        tasks = self.service.list_tasks()
        titles = [t["title"] for t in tasks]
        assert "T1" in titles
        assert "T2" in titles

    # ── Detección de la versión saboteada (Parte 3 / 5) ──────────────

    def test_add_task_realmente_usa_storage(self):
        """
        CRÍTICO: falla si add_task devuelve True sin llamar a storage.save.
        Detecta la modificación maliciosa de la Parte 3.
        """
        self.service.add_task("Verificar integración")
        assert self.storage.save_called_with is not None, (
            "add_task no llamó a storage.save — posible sabotaje"
        )

    def test_add_task_realmente_usa_notifier(self):
        """
        CRÍTICO: falla si add_task devuelve True sin llamar a notifier.send.
        Detecta la modificación maliciosa de la Parte 3.
        """
        self.service.add_task("Verificar notificación")
        assert len(self.notifier.messages) > 0, (
            "add_task no llamó a notifier.send — posible sabotaje"
        )

    # ── Fallos simulados ─────────────────────────────────────────────

    def test_fallo_en_storage_propaga_excepcion(self):
        """Service no captura IOError de storage → excepción propagada."""
        broken_storage = StubStorageRaisesOnSave()
        service = TaskService(broken_storage, self.notifier)
        with pytest.raises(IOError):
            service.add_task("Tarea que no se guarda")

    def test_fallo_en_notifier_propaga_excepcion(self):
        """Service no captura ConnectionError de notifier → excepción propagada."""
        noisy_notifier = StubNotifierRaises()
        service = TaskService(self.storage, noisy_notifier)
        with pytest.raises(ConnectionError):
            service.add_task("Tarea con notifier roto")

    def test_consistencia_si_notifier_falla_tarea_ya_guardada(self):
        """
        Si notifier falla, la tarea YA fue guardada (service no revierte).
        Esto documenta el comportamiento actual (no se considera correcto,
        pero se verifica explícitamente para detectar cambios futuros).
        """
        noisy_notifier = StubNotifierRaises()
        service = TaskService(self.storage, noisy_notifier)
        try:
            service.add_task("Tarea inconsistente")
        except ConnectionError:
            pass
        # La tarea quedó guardada aunque la notificación falló
        saved_titles = [t["title"] for t in self.storage._tasks]
        assert "Tarea inconsistente" in saved_titles


# ─────────────────────────────────────────────
# Parte 4.3 – Enfoque Sandwich
# ─────────────────────────────────────────────

class TestSandwich:
    """
    Combina Storage real (archivo temporal) con Notifier stub.
    Valida que Service persiste correctamente en disco.
    """

    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)          # TaskStorage crea el archivo si no existe
        self.storage = TaskStorage(self.tmp.name)
        self.notifier = StubNotifier()
        self.service = TaskService(self.storage, self.notifier)

    def teardown_method(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_tarea_persiste_en_disco(self):
        """Storage real: la tarea debe sobrevivir una recarga desde archivo."""
        self.service.add_task("Persistir en JSON")
        storage2 = TaskStorage(self.tmp.name)
        tasks = storage2.load()
        titles = [t["title"] for t in tasks]
        assert "Persistir en JSON" in titles

    def test_notifier_stub_recibe_mensaje_correcto(self):
        """Notifier stub confirma que Service llama send con el mensaje esperado."""
        self.service.add_task("Notificar sandwich")
        assert any("Notificar sandwich" in m for m in self.notifier.messages)

    def test_dos_tareas_distintas_en_disco(self):
        self.service.add_task("Tarea A")
        self.service.add_task("Tarea B")
        tasks = TaskStorage(self.tmp.name).load()
        titles = [t["title"] for t in tasks]
        assert "Tarea A" in titles
        assert "Tarea B" in titles

    def test_duplicado_no_escribe_en_disco(self):
        self.service.add_task("Única")
        self.service.add_task("Única")
        tasks = TaskStorage(self.tmp.name).load()
        assert len([t for t in tasks if t["title"] == "Única"]) == 1
