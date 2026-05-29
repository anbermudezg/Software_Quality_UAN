"""
test_tareas_e2e.py — Pruebas E2E completas del Gestor de Tareas.

Incluye:
  - Pruebas iniciales débiles (originales, para demostrar sus limitaciones)
  - TestCrearTareaFuerte   : aserciones sobre la UI tras crear
  - TestCompletarTareaFuerte: verifica badge y tachado
  - TestEliminarTareaFuerte : verifica desaparición de la lista
  - TestFlujoCompleto       : crear → completar → verificar → eliminar → verificar
  - TestCasosExtremos       : vacío, duplicados, lista vacía, orden

Ejecutar:
    pytest tests/test_tareas_e2e.py -v
"""

import pytest
from playwright.sync_api import expect
from tests.page_objects import TaskPage


# ─────────────────────────────────────────────────────────────────────────────
# Fixture: TaskPage lista para usar en cada test
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def task_page(page, live_server):
    tp = TaskPage(page, live_server)
    tp.goto()
    return tp


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas originales (débiles) — conservadas para análisis de la Parte 2/3
# ─────────────────────────────────────────────────────────────────────────────

class TestPaginaPrincipal:
    """Pruebas débiles de la página principal."""

    def test_pagina_carga(self, page):
        assert page.url is not None

    def test_titulo_visible(self, page):
        title = page.locator("[data-testid='page-title']")
        assert title.count() >= 0


class TestCrearTarea:
    """Pruebas débiles de creación de tareas."""

    def test_formulario_presente(self, page):
        form = page.locator("[data-testid='form-nueva-tarea']")
        assert form.count() >= 0

    def test_agregar_tarea_no_lanza_error(self, page):
        page.fill("[data-testid='input-titulo']", "Mi tarea")
        page.click("[data-testid='btn-agregar']")


class TestCompletarTarea:
    """Pruebas débiles de completar tareas."""

    def test_completar_tarea_no_lanza_error(self, page):
        page.fill("[data-testid='input-titulo']", "Tarea a completar")
        page.click("[data-testid='btn-agregar']")
        page.wait_for_load_state("networkidle")

        btn = page.locator("[data-testid='btn-completar']").first
        if btn.count() > 0:
            btn.click()
            page.wait_for_load_state("networkidle")


# ─────────────────────────────────────────────────────────────────────────────
# Parte 4 — TestCrearTareaFuerte
# ─────────────────────────────────────────────────────────────────────────────

class TestCrearTareaFuerte:
    """Verifica que crear una tarea produce cambios reales y visibles en la UI."""

    def test_tarea_aparece_en_la_lista(self, task_page):
        """El título debe aparecer en la lista tras crear la tarea."""
        task_page.crear_tarea("Preparar informe")
        assert task_page.tarea_existe("Preparar informe"), \
            "La tarea no apareció en la lista después de crearla"

    def test_lista_aumenta_en_uno(self, task_page):
        """El número de ítems en la lista debe incrementarse."""
        task_page.crear_tarea("Tarea conteo 1")
        task_page.crear_tarea("Tarea conteo 2")
        items = task_page.page.locator("[data-testid='tarea-item']")
        expect(items).to_have_count(2)

    def test_nueva_tarea_no_tiene_badge_completada(self, task_page):
        """Una tarea recién creada no debe mostrar el badge de completada."""
        task_page.crear_tarea("Tarea sin completar")
        assert not task_page.tarea_esta_completada("Tarea sin completar"), \
            "Una tarea nueva no debería aparecer como completada"

    def test_input_queda_vacio_tras_crear(self, task_page):
        """El campo de texto debe limpiarse después de enviar el formulario."""
        task_page.crear_tarea("Limpiar input")
        expect(task_page.input_titulo).to_have_value("")

    def test_deteccion_sabotaje_add_task(self, task_page):
        """
        CRÍTICO: falla si create_task no llama a repo.add().
        Detecta el sabotaje de la Parte 3.
        """
        task_page.crear_tarea("Tarea saboteada")
        assert task_page.tarea_existe("Tarea saboteada"), \
            "create_task no persistió la tarea — posible sabotaje en app.py"


# ─────────────────────────────────────────────────────────────────────────────
# Parte 4 — TestCompletarTareaFuerte
# ─────────────────────────────────────────────────────────────────────────────

class TestCompletarTareaFuerte:

    def test_badge_completada_aparece(self, task_page):
        """Tras completar, debe mostrarse el badge '✓ Completada'."""
        task_page.crear_tarea("Estudiar Playwright")
        task_page.completar_tarea("Estudiar Playwright")
        assert task_page.tarea_esta_completada("Estudiar Playwright"), \
            "El badge '✓ Completada' no apareció tras completar la tarea"

    def test_boton_completar_desaparece(self, task_page):
        """Después de completar, el botón 'Completar' no debe estar visible."""
        task_page.crear_tarea("Revisar PR")
        task_page.completar_tarea("Revisar PR")
        item = task_page._item_por_titulo("Revisar PR")
        expect(item.locator("[data-testid='btn-completar']")).to_have_count(0)

    def test_titulo_tachado_al_completar(self, task_page):
        """El título debe tener la clase CSS 'done' al completar la tarea."""
        task_page.crear_tarea("Tarea tachada")
        task_page.completar_tarea("Tarea tachada")
        item = task_page._item_por_titulo("Tarea tachada")
        titulo = item.locator("[data-testid='tarea-titulo']")
        expect(titulo).to_have_class("task-title done")


# ─────────────────────────────────────────────────────────────────────────────
# Parte 4 — TestEliminarTareaFuerte
# ─────────────────────────────────────────────────────────────────────────────

class TestEliminarTareaFuerte:

    def test_tarea_desaparece_al_eliminar(self, task_page):
        """Tras eliminar, la tarea no debe aparecer en la lista."""
        task_page.crear_tarea("Tarea a borrar")
        task_page.eliminar_tarea("Tarea a borrar")
        assert not task_page.tarea_existe("Tarea a borrar"), \
            "La tarea sigue visible después de eliminarla"

    def test_lista_vacia_tras_eliminar_unica(self, task_page):
        """Al eliminar la única tarea, debe aparecer el mensaje de lista vacía."""
        task_page.crear_tarea("Única tarea")
        task_page.eliminar_tarea("Única tarea")
        assert task_page.lista_esta_vacia(), \
            "No apareció el mensaje de lista vacía tras eliminar la única tarea"

    def test_otras_tareas_no_se_ven_afectadas(self, task_page):
        """Eliminar una tarea no debe afectar a las demás."""
        task_page.crear_tarea("Tarea A")
        task_page.crear_tarea("Tarea B")
        task_page.crear_tarea("Tarea C")
        task_page.eliminar_tarea("Tarea B")
        assert task_page.tarea_existe("Tarea A")
        assert not task_page.tarea_existe("Tarea B")
        assert task_page.tarea_existe("Tarea C")


# ─────────────────────────────────────────────────────────────────────────────
# Parte 5 — TestFlujoCompleto
# ─────────────────────────────────────────────────────────────────────────────

class TestFlujoCompleto:
    """Flujo completo: crear → completar → verificar → eliminar → verificar."""

    def test_ciclo_vida_completo(self, task_page):
        titulo = "Ciclo de vida completo"

        # 1. Crear
        task_page.crear_tarea(titulo)
        assert task_page.tarea_existe(titulo), "La tarea no fue creada"

        # 2. Completar
        task_page.completar_tarea(titulo)
        assert task_page.tarea_esta_completada(titulo), \
            "La tarea no quedó marcada como completada"

        # 3. Verificar badge
        item = task_page._item_por_titulo(titulo)
        expect(item.locator("[data-testid='badge-completada']")).to_be_visible()

        # 4. Eliminar
        task_page.eliminar_tarea(titulo)
        assert not task_page.tarea_existe(titulo), \
            "La tarea sigue en la lista después de eliminarla"

        # 5. Verificar lista vacía
        assert task_page.lista_esta_vacia(), \
            "La lista no muestra el mensaje de vacía tras eliminar la única tarea"


# ─────────────────────────────────────────────────────────────────────────────
# Parte 6 — TestCasosExtremos
# ─────────────────────────────────────────────────────────────────────────────

class TestCasosExtremos:

    def test_titulo_vacio_no_crea_tarea(self, task_page):
        """Enviar el formulario con título vacío no debe agregar ninguna tarea."""
        task_page.crear_tarea("")
        assert task_page.lista_esta_vacia(), \
            "Se creó una tarea con título vacío"

    def test_titulo_solo_espacios_no_crea_tarea(self, task_page):
        """Título con solo espacios tampoco debe crear tarea."""
        task_page.crear_tarea("   ")
        assert task_page.lista_esta_vacia(), \
            "Se creó una tarea con título de solo espacios"

    def test_tarea_duplicada_no_se_agrega(self, task_page):
        """Intentar agregar la misma tarea dos veces no debe duplicarla."""
        task_page.crear_tarea("Tarea única")
        task_page.crear_tarea("Tarea única")
        items = task_page.page.locator("[data-testid='tarea-item']")
        expect(items).to_have_count(1)

    def test_mensaje_lista_vacia_visible_al_inicio(self, task_page):
        """Con estado limpio, debe mostrarse el mensaje 'No hay tareas'."""
        assert task_page.lista_esta_vacia(), \
            "No se mostró el mensaje de lista vacía con el estado inicial limpio"

    def test_orden_de_creacion_se_mantiene(self, task_page):
        """Las tareas deben aparecer en el orden en que fueron creadas."""
        titulos = ["Primera", "Segunda", "Tercera"]
        for t in titulos:
            task_page.crear_tarea(t)
        assert task_page.titulos_en_orden() == titulos, \
            "El orden de las tareas en la lista no coincide con el de creación"

    def test_multiples_tareas_independientes(self, task_page):
        """Crear varias tareas no debe mezclar ni corromper sus estados."""
        task_page.crear_tarea("Alpha")
        task_page.crear_tarea("Beta")
        task_page.crear_tarea("Gamma")
        task_page.completar_tarea("Beta")
        assert not task_page.tarea_esta_completada("Alpha")
        assert task_page.tarea_esta_completada("Beta")
        assert not task_page.tarea_esta_completada("Gamma")
