"""
test_tareas_e2e.py — Pruebas E2E iniciales (versión débil).

⚠️ ESTAS PRUEBAS SON INTENCIONALMENTE DÉBILES.
   Pasan aunque el sistema tenga errores graves.
   El estudiante deberá identificar sus limitaciones y mejorarlas.

Ejecutar:
    pytest tests/test_tareas_e2e.py -v
"""

import pytest
from playwright.sync_api import expect
from page_objects import TaskPage

class TestCrearTareaFuerte:
    def test_crear_tarea_visible_en_lista(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        task_page.crear_tarea("Comprar leche")

        # Verifica visibilidad y texto esperado
        expect(task_page.obtener_tarea(0)).to_be_visible()
        expect(task_page.obtener_tarea(0).locator("[data-testid='tarea-titulo']")).to_have_text("Comprar leche")

    def test_crear_multiples_tareas_aumenta_conteo(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        task_page.crear_tarea("Tarea 1")
        task_page.crear_tarea("Tarea 2")

        # Verifica la cantidad exacta en el DOM
        expect(task_page.tarea_items).to_have_count(2)

        expect(task_page.obtener_tarea(0).locator("[data-testid='tarea-titulo']")).to_have_text("Tarea 1")
        expect(task_page.obtener_tarea(1).locator("[data-testid='tarea-titulo']")).to_have_text("Tarea 2")

    def test_input_se_limpia_tras_crear_tarea(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        task_page.crear_tarea("Estudiar E2E")

        # Verifica el estado del formulario
        expect(task_page.input_titulo).to_be_empty()

class TestCompletarTareaFuerte:
    """Verifica el badge y el tachado del titulo."""

    def test_tarea_completada_muestra_badge_y_tachado(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        task_page.crear_tarea("Tarea por completar")
        task_page.completar_tarea(0)

        tarea = task_page.obtener_tarea(0)

        # Verifica el texto del badge (contiene la palabra clave)
        badge = tarea.locator("[data-testid='badge-completada']")
        expect(badge).to_contain_text("Completada")
        
        # Verifica el tachado asegurando que adquiera la clase CSS '.done'
        titulo = tarea.locator("[data-testid='tarea-titulo']")
        expect(titulo).to_have_class("task-title done")
        
class TestEliminarTareaFuerte:
    """Verifica desaparicion de la lista."""      

    def test_tarea_eliminada_desaparece_de_ui(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        task_page.crear_tarea("Tarea temporal")

        expect(task_page.tarea_items).to_have_count(1)
        task_page.eliminar_tarea(0)

        # El contador debe bajar a 0
        expect(task_page.tarea_items).to_have_count(0)

class TestFlujoCompleto:
    """Flujo crear -> completar -> eliminar en un solo test."""

    def test_flujo_crear_completar_eliminar(self, page):
        task_page = TaskPage(page)
        task_page.ir_a_inicio()

        # 1. Crear
        task_page.crear_tarea("Flujo maestro")
        expect(task_page.tarea_items).to_have_count(1)

        # 2. Completar
        task_page.completar_tarea(0)
        badge = task_page.obtener_tarea(0).locator("[data-testid='badge-completada']")
        expect(badge).to_contain_text("Completada")
        
        # 3.Eliminar
        task_page.eliminar_tarea(0)
        expect(task_page.tarea_items).to_have_count(0)
       
class TestCasosExtremos:  
    """Titulo vacio, duplicdos, lista vacia."""     

    def test_lista_vacia_inicialmente(self, page):
        """Verifica el estado de lista vacia"""
        task_page = TaskPage(page)
        task_page.ir_a_inicio()

        # Valida que aparezca el mensaje de la lista vacia
        expect(task_page.msg_vacia).to_be_visible()
        expect(task_page.tarea_items).to_have_count(0)
        
    def test_no_permitir_crear_tarea_con_titulo_vacio(self, page):
        """Verifica el caso de titulo vacio."""
        task_page = TaskPage(page)
        task_page.ir_a_inicio()

        task_page.crear_tarea("")

        # No se debe haber creado nada
        expect(task_page.tarea_items).to_have_count(0)

    def test_control_de_tareas_duplicadas(self, page):
        """Verifica el caso de tareas duplicados."""
        task_page = TaskPage(page)
        task_page.ir_a_inicio()
        
        task_page.crear_tarea("Tarea Duplicada")
        task_page.crear_tarea("Tarea Duplicada")

        # Deben existir 2 tareas con el mismo texto
        expect(task_page.tarea_items).to_have_count(1)
        expect(task_page.obtener_tarea(0).locator("[data-testid='tarea-titulo']")).to_have_text("Tarea Duplicada")