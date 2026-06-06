"""
test_tareas_e2e.py — Pruebas E2E mejoradas según el entregable.
"""
import pytest
from playwright.sync_api import expect
from tests.page_objects import TaskPage


class TestCrearTareaFuerte:
    """Pruebas fuertes de creación de tareas."""

    def test_crear_tarea_titulo_aparece_en_lista(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_title = "Tarea de prueba"
        task_page.create_task(task_title)
        # Verificar que el título aparece en la lista
        expect(page.locator("[data-testid='tarea-titulo']").filter(has_text=task_title)).to_be_visible()

    def test_crear_tarea_incrementa_contador(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        initial_count = task_page.get_task_count()
        task_page.create_task("Otra tarea")
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(initial_count + 1)

    def test_crear_tarea_limpiar_input(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.input_titulo.fill("Algun título")
        task_page.btn_agregar.click()
        # Después de agregar, el input debería estar vacío
        expect(task_page.input_titulo).to_be_empty()


class TestCompletarTareaFuerte:
    """Pruebas fuertes de completar tareas."""

    def test_completar_tarea_muestra_badge_y_tachado(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.create_task("Tarea a completar")
        # Obtener el ID de la tarea recién creada (asumimos solo una)
        tarea_items = page.locator("[data-testid='tarea-item']")
        expect(tarea_items).to_have_count(1)
        task_id = tarea_items.get_attribute("data-task-id")
        # Completar la tarea
        task_page.complete_task(task_id)
        # Verificar badge visible
        expect(task_page.badge_completada(task_id)).to_be_visible()
        # Verificar que el título tiene la clase 'done' (tachado)
        titulo = task_page.tarea_titulo(task_id)
        expect(titulo).to_have_class("task-title done")


class TestEliminarTareaFuerte:
    """Pruebas fuertes de eliminar tareas."""

    def test_eliminar_tarea_desaparece_de_lista(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.create_task("Tarea a eliminar")
        tarea_items = page.locator("[data-testid='tarea-item']")
        expect(tarea_items).to_have_count(1)
        task_id = tarea_items.get_attribute("data-task-id")
        # Eliminar la tarea
        task_page.delete_task(task_id)
        # Verificar que el elemento ya no está en el DOM
        expect(task_page.tarea_item(task_id)).not_to_be_attached()
        # Alternativamente, verificar que la lista esté vacía
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(0)


class TestFlujoCompleto:
    """Flujo completo: crear → completar → eliminar."""

    def test_flujo_crear_completar_eliminar(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        # Crear
        task_page.create_task("Flujo completo")
        tarea_items = page.locator("[data-testid='tarea-item']")
        expect(tarea_items).to_have_count(1)
        task_id = tarea_items.get_attribute("data-task-id")
        # Completar
        task_page.complete_task(task_id)
        expect(task_page.badge_completada(task_id)).to_be_visible()
        titulo = task_page.tarea_titulo(task_id)
        expect(titulo).to_have_class("task-title done")
        # Eliminar
        task_page.delete_task(task_id)
        expect(task_page.tarea_item(task_id)).not_to_be_attached()


class TestCasosExtremos:
    """Pruebas de casos extremos y validaciones."""

    def test_titulo_vacio_no_crea_tarea(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.input_titulo.fill("   ")  # solo espacios
        task_page.btn_agregar.click()
        # La lista debe seguir vacía
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(0)
        # Además, el mensaje de lista vacía debería ser visible
        expect(task_page.msg_lista_vacia()).to_be_visible()

    def test_tarea_duplicada_no_se_crea(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.create_task("Tarea única")
        # Intentar crear otra con el mismo título
        task_page.input_titulo.fill("Tarea única")
        task_page.btn_agregar.click()
        # La cantidad de tareas debería seguir siendo 1
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(1)
        # No debería aparecer mensaje de error explícito, pero podemos verificar que no haya duplicados en la lista
        titles = task_page.get_task_titles()
        assert titles.count("Tarea única") == 1

    def test_lista_vacia_muestra_mensaje(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        # No hay tareas inicialmente (porque se limpia en conftest)
        expect(task_page.msg_lista_vacia()).to_be_visible()
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(0)

    def test_multiples_tareas_orden(self, page, live_server):
        task_page = TaskPage(page)
        task_page.goto(live_server)
        task_page.create_task("Primera")
        task_page.create_task("Segunda")
        task_page.create_task("Tercera")
        titles = task_page.get_task_titles()
        assert titles == ["Primera", "Segunda", "Tercera"]
        expect(task_page.lista_tareas.locator("[data-testid='tarea-item']")).to_have_count(3)