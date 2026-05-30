"""
test_tareas_e2e.py — Pruebas E2E iniciales (versión débil).

⚠️ ESTAS PRUEBAS SON INTENCIONALMENTE DÉBILES.
   Pasan aunque el sistema tenga errores graves.
   El estudiante deberá identificar sus limitaciones y mejorarlas.

Ejecutar:
    pytest tests/test_tareas_e2e.py -v
"""

# import pytest


# class TestPaginaPrincipal:
#     """Pruebas débiles de la página principal."""

#     def test_pagina_carga(self, page):
#         """Verifica que la página responde (solo código HTTP 200)."""
#         # Esta prueba pasa aunque la página esté completamente rota
#         # siempre que no lance un error 500
#         assert page.url is not None

#     def test_titulo_visible(self, page):
#         """Verifica que el título de la página existe."""
#         # Aserción débil: solo verifica que el elemento existe, no su contenido
#         title = page.locator("[data-testid='page-title']")
#         assert title.count() >= 0  # Siempre pasa, incluso si no existe


# class TestCrearTarea:
#     """Pruebas débiles de creación de tareas."""

#     def test_formulario_presente(self, page):
#         """Verifica que el formulario existe en la página."""
#         form = page.locator("[data-testid='form-nueva-tarea']")
#         # Aserción débil: no verifica que el formulario funcione
#         assert form.count() >= 0

#     def test_agregar_tarea_no_lanza_error(self, page):
#         """Verifica que agregar una tarea no lanza excepción de red."""
#         page.fill("[data-testid='input-titulo']", "Mi tarea")
#         page.click("[data-testid='btn-agregar']")
#         # No verifica que la tarea realmente aparezca en la lista


# class TestCompletarTarea:
#     """Pruebas débiles de completar tareas."""

#     def test_completar_tarea_no_lanza_error(self, page):
#         """Verifica que el flujo completar no lanza error de red."""
#         # Primero creamos una tarea
#         page.fill("[data-testid='input-titulo']", "Tarea a completar")
#         page.click("[data-testid='btn-agregar']")
#         page.wait_for_load_state("networkidle")

#         # Intentamos completarla (sin verificar el resultado)
#         btn = page.locator("[data-testid='btn-completar']").first
#         if btn.count() > 0:
#             btn.click()
#             page.wait_for_load_state("networkidle")
#         # No verifica que la tarea quede marcada como completada

# testings fuertes en page_objects.py

import pytest
from tests.page_objects import TaskPage


@pytest.fixture
def task_page(page, live_server):
    tp = TaskPage(page, live_server)
    tp.ir_a_inicio()
    return tp


class TestCrearTareaFuerte:

    def test_tarea_aparece_en_lista(self, task_page):
        task_page.crear_tarea("Comprar leche")
        assert task_page.tarea_existe("Comprar leche")

    def test_multiples_tareas_aparecen(self, task_page):
        task_page.crear_tarea("Tarea uno")
        task_page.crear_tarea("Tarea dos")
        assert task_page.tarea_existe("Tarea uno")
        assert task_page.tarea_existe("Tarea dos")

    def test_titulo_correcto_en_lista(self, task_page):
        task_page.crear_tarea("Estudiar para el examen")
        titulos = task_page.obtener_titulos()
        assert "Estudiar para el examen" in titulos


class TestCompletarTareaFuerte:

    def test_badge_aparece_al_completar(self, task_page):
        task_page.crear_tarea("Tarea para completar")
        task_page.completar_tarea("Tarea para completar")
        assert task_page.tarea_completada("Tarea para completar")

    def test_boton_completar_desaparece(self, task_page):
        task_page.crear_tarea("Otra tarea")
        task_page.completar_tarea("Otra tarea")
        item = task_page.page.locator(
            "[data-testid='tarea-item']:has([data-testid='tarea-titulo']:has-text('Otra tarea'))"
        )
        assert item.locator("[data-testid='btn-completar']").count() == 0


class TestEliminarTareaFuerte:

    def test_tarea_desaparece_al_eliminar(self, task_page):
        task_page.crear_tarea("Tarea a eliminar")
        task_page.eliminar_tarea("Tarea a eliminar")
        assert not task_page.tarea_existe("Tarea a eliminar")

    def test_lista_vacia_tras_eliminar_unica(self, task_page):
        task_page.crear_tarea("Unica tarea")
        task_page.eliminar_tarea("Unica tarea")
        assert task_page.lista_vacia()


class TestFlujoCompleto:

    def test_crear_completar_eliminar(self, task_page):
        task_page.crear_tarea("Flujo completo")
        assert task_page.tarea_existe("Flujo completo")

        task_page.completar_tarea("Flujo completo")
        assert task_page.tarea_completada("Flujo completo")

        task_page.eliminar_tarea("Flujo completo")
        assert not task_page.tarea_existe("Flujo completo")


class TestCasosExtremos:

    def test_titulo_vacio_no_agrega_tarea(self, task_page):
        task_page.crear_tarea("")
        assert task_page.lista_vacia()

    def test_duplicado_no_se_agrega(self, task_page):
        task_page.crear_tarea("Tarea duplicada")
        task_page.crear_tarea("Tarea duplicada")
        titulos = task_page.obtener_titulos()
        assert titulos.count("Tarea duplicada") == 1

    def test_mensaje_lista_vacia_visible(self, task_page):
        assert task_page.lista_vacia()