"""
Pruebas E2E robustas para el gestor de tareas.

Estas pruebas verifican comportamiento observable de la UI y del estado
persistido, no solo que las acciones no fallen.
"""

import pytest
from playwright.sync_api import expect

from tests.page_objects import TaskPage


@pytest.fixture
def task_page(page):
    # Uso un Page Object para no repetir locators en cada prueba.
    return TaskPage(page)


class TestCrearTareaFuerte:
    def test_crear_tarea_la_muestra_en_la_lista(self, task_page):
        # Creo la tarea y reviso que sí aparezca en pantalla.
        task_page.create_task("Mi tarea importante")

        task_page.expect_task_visible("Mi tarea importante")

    def test_crear_tarea_conserva_el_texto_en_pantalla(self, task_page):
        task_page.create_task("Revisar el reporte")

        expect(task_page.task_title("Revisar el reporte")).to_have_text("Revisar el reporte")

    def test_crear_varias_tareas_respeta_el_orden(self, task_page):
        titles = ["Primera tarea", "Segunda tarea", "Tercera tarea"]

        # Agrego varias tareas para comprobar que se muestran en el orden correcto.
        for title in titles:
            task_page.create_task(title)

        task_page.expect_task_titles(titles)


class TestCompletarTareaFuerte:
    def test_completar_tarea_muestra_badge_y_tachado(self, task_page):
        # Primero la creo y luego verifico que quede marcada como completada.
        task_page.create_task("Tarea a completar")

        task_page.complete_task("Tarea a completar")

        task_page.expect_completed("Tarea a completar")


class TestEliminarTareaFuerte:
    def test_eliminar_tarea_la_remueve_de_la_lista(self, task_page):
        # La idea es comprobar que al borrar, ya no se vea en la lista.
        task_page.create_task("Tarea a eliminar")

        task_page.delete_task("Tarea a eliminar")

        task_page.expect_task_hidden("Tarea a eliminar")
        task_page.expect_empty_state()


class TestFlujoCompleto:
    def test_flujo_crear_completar_y_eliminar(self, task_page):
        title = "Flujo completo de usuario"

        # Este test junta el recorrido completo de la tarea.
        task_page.create_task(title)
        task_page.expect_task_visible(title)

        task_page.complete_task(title)
        task_page.expect_completed(title)

        task_page.delete_task(title)
        task_page.expect_task_hidden(title)
        task_page.expect_empty_state()


class TestCasosExtremos:
    def test_crear_tarea_con_titulo_vacio_no_agrega_elementos(self, task_page):
        # Si el título viene vacío, no debería aparecer nada nuevo.
        task_page.create_task("")

        task_page.expect_empty_state()

    def test_crear_tareas_duplicadas_solo_deja_una(self, task_page):
        # Pruebo que la app no repita tareas con el mismo nombre.
        task_page.create_task("Duplicada")
        task_page.create_task("Duplicada")

        task_page.expect_task_visible("Duplicada")
        expect(task_page.task_items()).to_have_count(1)

    def test_lista_vacia_muestra_mensaje_de_estado(self, task_page):
        task_page.expect_empty_state()

    def test_crear_multiples_tareas_y_verificar_orden(self, task_page):
        titles = ["Armar informe", "Enviar correo", "Cerrar taller"]

        for title in titles:
            task_page.create_task(title)

        task_page.expect_task_titles(titles)
