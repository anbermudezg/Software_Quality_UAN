"""
test_tareas_e2e.py — Suite completa de pruebas E2E para el Gestor de Tareas.

Incluye:
  - TestPaginaPrincipal   : pruebas débiles originales (se conservan para contraste)
  - TestCrearTareaFuerte  : aserciones sobre estado real de la UI
  - TestCompletarTareaFuerte : verifica badge y estado visual
  - TestEliminarTareaFuerte  : verifica desaparición de la lista
  - TestFlujoCompleto     : flujo crear → completar → eliminar
  - TestCasosExtremos     : título vacío, duplicados, lista vacía, orden

Ejecutar:
    pytest tests/test_tareas_e2e.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.page_objects import TaskPage


# ─────────────────────────────────────────────────────────────────────────────
# Fixture: TaskPage lista para usar en cada test
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def task_page(page, live_server):
    """Devuelve un TaskPage ya navegado a la página principal."""
    tp = TaskPage(page, live_server)
    tp.goto()
    return tp


# ─────────────────────────────────────────────────────────────────────────────
# Pruebas débiles originales (conservadas para contraste con el informe)
# ─────────────────────────────────────────────────────────────────────────────

class TestPaginaPrincipal:
    """Pruebas débiles de la página principal — versión original intacta."""

    def test_pagina_carga(self, page):
        assert page.url is not None

    def test_titulo_visible(self, page):
        title = page.locator("[data-testid='page-title']")
        assert title.count() >= 0


class TestCrearTarea:
    """Pruebas débiles de creación — versión original intacta."""

    def test_formulario_presente(self, page):
        form = page.locator("[data-testid='form-nueva-tarea']")
        assert form.count() >= 0

    def test_agregar_tarea_no_lanza_error(self, page):
        page.fill("[data-testid='input-titulo']", "Mi tarea")
        page.click("[data-testid='btn-agregar']")


class TestCompletarTarea:
    """Pruebas débiles de completar — versión original intacta."""

    def test_completar_tarea_no_lanza_error(self, page):
        page.fill("[data-testid='input-titulo']", "Tarea a completar")
        page.click("[data-testid='btn-agregar']")
        page.wait_for_load_state("networkidle")
        btn = page.locator("[data-testid='btn-completar']").first
        if btn.count() > 0:
            btn.click()
            page.wait_for_load_state("networkidle")


# ─────────────────────────────────────────────────────────────────────────────
# Parte 4 y 5 — Pruebas fuertes con Page Object
# ─────────────────────────────────────────────────────────────────────────────

class TestCrearTareaFuerte:
    """
    Pruebas robustas de creación de tareas.
    Verifican estado real de la UI, no solo ausencia de errores.
    Detectan el sabotaje de la Parte 3.
    """

    def test_tarea_aparece_en_lista_tras_crearla(self, task_page):
        """Al crear una tarea, su título debe ser visible en la lista."""
        task_page.crear_tarea("Comprar leche")
        assert task_page.titulo_visible("Comprar leche"), (
            "La tarea creada no aparece en la lista — posible sabotaje en create_task"
        )

    def test_lista_aumenta_en_uno_tras_crear_tarea(self, task_page):
        """El contador de tareas debe incrementarse en 1."""
        antes = task_page.contar_tareas()
        task_page.crear_tarea("Estudiar Playwright")
        assert task_page.contar_tareas() == antes + 1

    def test_tarea_creada_no_esta_completada_por_defecto(self, task_page):
        """Una tarea recién creada no debe tener el badge de completada."""
        task_page.crear_tarea("Tarea nueva")
        assert not task_page.tarea_esta_completada("Tarea nueva")

    def test_input_queda_vacio_tras_crear_tarea(self, task_page):
        """El campo de texto debe quedar limpio después de enviar el formulario."""
        task_page.crear_tarea("Limpiar input")
        valor = task_page.input_titulo.input_value()
        assert valor == "", "El input no quedó vacío tras crear la tarea"

    def test_mensaje_lista_vacia_desaparece_al_crear_tarea(self, task_page):
        """Si la lista estaba vacía, el mensaje debe desaparecer al agregar una tarea."""
        assert task_page.lista_esta_vacia()
        task_page.crear_tarea("Primera tarea")
        assert not task_page.lista_esta_vacia()


class TestCompletarTareaFuerte:
    """
    Pruebas robustas de completar tareas.
    Verifican badge visual y estado del título.
    """

    def test_badge_completada_aparece_tras_completar(self, task_page):
        """Al completar una tarea, debe aparecer el badge '✓ Completada'."""
        task_page.crear_tarea("Tarea para completar")
        task_page.completar_tarea("Tarea para completar")
        assert task_page.tarea_esta_completada("Tarea para completar"), (
            "El badge '✓ Completada' no apareció tras completar la tarea"
        )

    def test_boton_completar_desaparece_tras_completar(self, task_page):
        """Una vez completada, el botón Completar no debe seguir visible."""
        task_page.crear_tarea("Sin botón")
        task_page.completar_tarea("Sin botón")
        item = task_page._get_item_by_title("Sin botón")
        assert item.locator("[data-testid='btn-completar']").count() == 0

    def test_tarea_completada_permanece_en_lista(self, task_page):
        """Completar una tarea no la elimina de la lista."""
        task_page.crear_tarea("Permanece")
        task_page.completar_tarea("Permanece")
        assert task_page.tarea_existe("Permanece")


class TestEliminarTareaFuerte:
    """
    Pruebas robustas de eliminación de tareas.
    Verifican desaparición real de la UI.
    """

    def test_tarea_desaparece_tras_eliminarla(self, task_page):
        """Al eliminar una tarea, debe desaparecer de la lista."""
        task_page.crear_tarea("Tarea a eliminar")
        task_page.eliminar_tarea("Tarea a eliminar")
        assert not task_page.tarea_existe("Tarea a eliminar"), (
            "La tarea sigue apareciendo en la lista tras eliminarla"
        )

    def test_lista_disminuye_en_uno_tras_eliminar(self, task_page):
        """El contador de tareas debe decrementarse en 1."""
        task_page.crear_tarea("Tarea X")
        task_page.crear_tarea("Tarea Y")
        antes = task_page.contar_tareas()
        task_page.eliminar_tarea("Tarea X")
        assert task_page.contar_tareas() == antes - 1

    def test_otras_tareas_no_se_ven_afectadas_al_eliminar(self, task_page):
        """Eliminar una tarea no debe afectar a las demás."""
        task_page.crear_tarea("Queda")
        task_page.crear_tarea("Se va")
        task_page.eliminar_tarea("Se va")
        assert task_page.tarea_existe("Queda")

    def test_lista_vacia_tras_eliminar_unica_tarea(self, task_page):
        """Al eliminar la única tarea, debe aparecer el mensaje de lista vacía."""
        task_page.crear_tarea("Última")
        task_page.eliminar_tarea("Última")
        assert task_page.lista_esta_vacia()


class TestFlujoCompleto:
    """
    Flujo completo de usuario: crear → completar → verificar → eliminar → verificar.
    Representa un escenario E2E real de extremo a extremo.
    """

    def test_ciclo_de_vida_completo_de_una_tarea(self, task_page):
        """Crea, completa y elimina una tarea verificando cada estado."""
        # 1. Crear
        task_page.crear_tarea("Ciclo completo")
        assert task_page.titulo_visible("Ciclo completo"), "La tarea no apareció tras crearla"
        assert not task_page.tarea_esta_completada("Ciclo completo")

        # 2. Completar
        task_page.completar_tarea("Ciclo completo")
        assert task_page.tarea_esta_completada("Ciclo completo"), "El badge no apareció"

        # 3. Eliminar
        task_page.eliminar_tarea("Ciclo completo")
        assert not task_page.tarea_existe("Ciclo completo"), "La tarea sigue en la lista"

        # 4. Lista vacía
        assert task_page.lista_esta_vacia()

    def test_multiples_tareas_flujo_independiente(self, task_page):
        """Crea varias tareas, completa una, elimina otra, verifica aislamiento."""
        task_page.crear_tarea("Alpha")
        task_page.crear_tarea("Beta")
        task_page.crear_tarea("Gamma")

        task_page.completar_tarea("Beta")
        task_page.eliminar_tarea("Alpha")

        assert not task_page.tarea_existe("Alpha")
        assert task_page.tarea_esta_completada("Beta")
        assert task_page.tarea_existe("Gamma")
        assert not task_page.tarea_esta_completada("Gamma")


# ─────────────────────────────────────────────────────────────────────────────
# Parte 6 — Casos extremos
# ─────────────────────────────────────────────────────────────────────────────

class TestCasosExtremos:
    """
    Casos límite: título vacío, duplicados, lista vacía, orden de inserción.
    """

    def test_lista_vacia_al_inicio(self, task_page):
        """La página debe mostrar el mensaje de lista vacía cuando no hay tareas."""
        assert task_page.lista_esta_vacia(), (
            "Se esperaba el mensaje 'No hay tareas' con la lista vacía"
        )

    def test_titulo_vacio_no_agrega_tarea(self, task_page):
        """Intentar crear una tarea con título vacío no debe agregar nada."""
        antes = task_page.contar_tareas()
        task_page.crear_tarea("")
        assert task_page.contar_tareas() == antes, (
            "Se agregó una tarea con título vacío"
        )

    def test_titulo_solo_espacios_no_agrega_tarea(self, task_page):
        """Un título compuesto solo de espacios no debe crear tarea."""
        antes = task_page.contar_tareas()
        task_page.crear_tarea("   ")
        assert task_page.contar_tareas() == antes

    def test_tarea_duplicada_no_se_agrega_dos_veces(self, task_page):
        """Intentar crear una tarea duplicada no debe duplicarla en la lista."""
        task_page.crear_tarea("Duplicada")
        task_page.crear_tarea("Duplicada")
        items = task_page.page.locator(
            "[data-testid='tarea-item']:has([data-testid='tarea-titulo']:text-is('Duplicada'))"
        )
        assert items.count() == 1, (
            f"La tarea duplicada aparece {items.count()} veces en la lista"
        )

    def test_orden_de_insercion_se_preserva(self, task_page):
        """Las tareas deben aparecer en el orden en que fueron creadas."""
        task_page.crear_tarea("Primera")
        task_page.crear_tarea("Segunda")
        task_page.crear_tarea("Tercera")
        orden = task_page.titulos_en_orden()
        assert orden == ["Primera", "Segunda", "Tercera"], (
            f"El orden esperado es ['Primera', 'Segunda', 'Tercera'] pero se obtuvo {orden}"
        )

    def test_multiples_tareas_todas_visibles(self, task_page):
        """Al crear varias tareas, todas deben estar visibles simultáneamente."""
        titulos = ["Alfa", "Beta", "Gamma", "Delta"]
        for t in titulos:
            task_page.crear_tarea(t)
        assert task_page.contar_tareas() == len(titulos)
        for t in titulos:
            assert task_page.titulo_visible(t), f"'{t}' no está visible en la lista"
