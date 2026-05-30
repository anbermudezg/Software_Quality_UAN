"""
Pruebas de integración para TaskService.
Incluye enfoques Top-Down (stubs) y Sandwich (stub + módulo real).
"""
import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.storage import TaskStorage
from src.service import TaskService
from src.notifier import Notifier


# ─────────────────────────────────────────────
# Stubs
# ─────────────────────────────────────────────

class StubStorage:
    """Stub de TaskStorage: registra llamadas y trabaja en memoria."""

    def __init__(self, initial=None):
        self._tasks = list(initial or [])
        self.load_count = 0
        self.save_count = 0
        self.last_saved = None

    def load(self):
        self.load_count += 1
        return list(self._tasks)

    def save(self, tasks):
        self.save_count += 1
        self.last_saved = list(tasks)
        self._tasks = list(tasks)


class StubNotifier:
    """Stub de Notifier: registra mensajes enviados, nunca falla."""

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class FailingStorageStub(StubStorage):
    """Stub de Storage que lanza IOError al guardar."""

    def save(self, tasks):
        raise IOError("Disco lleno simulado")


class FailingNotifierStub(StubNotifier):
    """Stub de Notifier que lanza ConnectionError al enviar."""

    def send(self, message):
        raise ConnectionError("Sin conexión simulada")


# ─────────────────────────────────────────────
# Fixture: archivo temporal para tests con Storage real
# ─────────────────────────────────────────────

@pytest.fixture
def tmp_storage(tmp_path):
    filepath = str(tmp_path / "tasks.json")
    return TaskStorage(filepath)


# ─────────────────────────────────────────────
# Clase 1: Top-Down (Service + stubs de Storage y Notifier)
# ─────────────────────────────────────────────

class TestTopDown:
    """
    Enfoque Top-Down: se prueba Service de forma aislada.
    Storage y Notifier son stubs que registran las interacciones.
    """

    def _make_service(self, initial=None, notifier=None):
        storage = StubStorage(initial)
        notifier = notifier or StubNotifier()
        service = TaskService(storage, notifier)
        return service, storage, notifier

    # ── Verificación de interacciones reales ──────────────────────────────

    def test_add_task_llama_a_storage_save(self):
        """Service debe persistir la tarea: si no llama a save, la prueba falla."""
        service, storage, notifier = self._make_service()
        service.add_task("Estudiar")
        assert storage.save_count == 1, (
            "add_task no llamó a storage.save — la tarea no se persistió"
        )

    def test_add_task_llama_a_notifier_send(self):
        """Service debe notificar tras agregar; si no lo hace, la prueba falla."""
        service, storage, notifier = self._make_service()
        service.add_task("Estudiar")
        assert len(notifier.messages) == 1, (
            "add_task no llamó a notifier.send — la notificación no se envió"
        )

    def test_add_task_parametros_correctos_en_storage(self):
        """El contenido guardado debe incluir la tarea con título y done=False."""
        service, storage, _ = self._make_service()
        service.add_task("Revisar PR")
        assert storage.last_saved == [{"title": "Revisar PR", "done": False}]

    def test_add_task_parametros_correctos_en_notifier(self):
        """El mensaje enviado al notifier debe mencionar el título de la tarea."""
        service, _, notifier = self._make_service()
        service.add_task("Deploy a producción")
        assert "Deploy a producción" in notifier.messages[0]

    # ── Comportamiento funcional ───────────────────────────────────────────

    def test_add_task_retorna_true_en_tarea_nueva(self):
        service, _, _ = self._make_service()
        assert service.add_task("Nueva tarea") is True

    def test_add_task_retorna_false_en_duplicado(self):
        existing = [{"title": "Ya existe", "done": False}]
        service, _, _ = self._make_service(initial=existing)
        assert service.add_task("Ya existe") is False

    def test_add_task_duplicado_no_llama_save(self):
        """Un duplicado no debe persistirse."""
        existing = [{"title": "Duplicada", "done": False}]
        service, storage, _ = self._make_service(initial=existing)
        service.add_task("Duplicada")
        assert storage.save_count == 0

    def test_add_task_duplicado_no_llama_notifier(self):
        """Un duplicado no debe generar notificación."""
        existing = [{"title": "Duplicada", "done": False}]
        service, _, notifier = self._make_service(initial=existing)
        service.add_task("Duplicada")
        assert len(notifier.messages) == 0

    def test_complete_task_existente(self):
        existing = [{"title": "Tarea X", "done": False}]
        service, _, _ = self._make_service(initial=existing)
        assert service.complete_task("Tarea X") is True

    def test_complete_task_no_existente(self):
        service, _, _ = self._make_service()
        assert service.complete_task("No existe") is False

    def test_list_tasks_retorna_lo_que_storage_carga(self):
        existing = [{"title": "A", "done": False}, {"title": "B", "done": True}]
        service, _, _ = self._make_service(initial=existing)
        assert service.list_tasks() == existing

    # ── Título vacío ───────────────────────────────────────────────────────

    def test_add_task_titulo_vacio_no_debe_persistirse(self):
        """
        Política explícita: título vacío no debe guardarse.
        Si el sistema actual lo permite, esta prueba documenta el fallo.
        """
        service, storage, _ = self._make_service()
        result = service.add_task("")
        # Aceptamos que retorne True o False, pero no debe guardarse una tarea sin título
        if result:
            saved = storage.last_saved or []
            titles = [t["title"] for t in saved]
            assert "" not in titles, (
                "Se guardó una tarea con título vacío — comportamiento no deseable"
            )

    # ── Escenarios de error ────────────────────────────────────────────────

    def test_fallo_en_storage_propaga_excepcion(self):
        """Si storage.save lanza IOError, add_task debe propagarlo."""
        storage = FailingStorageStub()
        notifier = StubNotifier()
        service = TaskService(storage, notifier)
        with pytest.raises(IOError):
            service.add_task("Tarea problemática")

    def test_fallo_en_notifier_propaga_excepcion(self):
        """Si notifier.send lanza ConnectionError, add_task debe propagarlo."""
        storage = StubStorage()
        notifier = FailingNotifierStub()
        service = TaskService(storage, notifier)
        with pytest.raises(ConnectionError):
            service.add_task("Tarea con notifier roto")

    def test_consistencia_tras_fallo_en_notifier(self):
        """
        Si el notifier falla DESPUÉS de que storage guardó,
        la tarea queda en storage (comportamiento actual del sistema).
        Esta prueba documenta y valida ese comportamiento explícitamente.
        """
        storage = StubStorage()
        notifier = FailingNotifierStub()
        service = TaskService(storage, notifier)
        try:
            service.add_task("Tarea consistencia")
        except ConnectionError:
            pass
        # La tarea quedó guardada aunque la notificación falló
        tasks = storage.load()
        titles = [t["title"] for t in tasks]
        assert "Tarea consistencia" in titles, (
            "La tarea debe quedar guardada aun cuando el notifier falla "
            "(comportamiento actual; cambiar si se implementa rollback)"
        )


# ─────────────────────────────────────────────
# Clase 2: Sandwich (Service + Storage real + StubNotifier)
# ─────────────────────────────────────────────

class TestSandwich:
    """
    Enfoque Sandwich: Storage es el módulo REAL (escribe en disco);
    Notifier es un stub para no enviar correos reales.
    Se valida que la persistencia ocurra correctamente.
    """

    def test_add_task_persiste_en_disco(self, tmp_storage):
        notifier = StubNotifier()
        service = TaskService(tmp_storage, notifier)
        service.add_task("Tarea en disco")
        tasks = tmp_storage.load()
        assert any(t["title"] == "Tarea en disco" for t in tasks)

    def test_add_task_notifier_recibe_mensaje_correcto(self, tmp_storage):
        notifier = StubNotifier()
        service = TaskService(tmp_storage, notifier)
        service.add_task("Notificación real")
        assert len(notifier.messages) == 1
        assert "Notificación real" in notifier.messages[0]

    def test_complete_task_persiste_cambio_en_disco(self, tmp_storage):
        notifier = StubNotifier()
        service = TaskService(tmp_storage, notifier)
        service.add_task("Tarea a completar")
        service.complete_task("Tarea a completar")
        tasks = tmp_storage.load()
        tarea = next(t for t in tasks if t["title"] == "Tarea a completar")
        assert tarea["done"] is True

    def test_dos_tareas_distintas_ambas_persisten(self, tmp_storage):
        notifier = StubNotifier()
        service = TaskService(tmp_storage, notifier)
        service.add_task("Primera")
        service.add_task("Segunda")
        tasks = tmp_storage.load()
        titles = [t["title"] for t in tasks]
        assert "Primera" in titles
        assert "Segunda" in titles

    def test_duplicado_no_persiste_segunda_vez(self, tmp_storage):
        notifier = StubNotifier()
        service = TaskService(tmp_storage, notifier)
        service.add_task("Duplicada")
        service.add_task("Duplicada")
        tasks = tmp_storage.load()
        assert len([t for t in tasks if t["title"] == "Duplicada"]) == 1
