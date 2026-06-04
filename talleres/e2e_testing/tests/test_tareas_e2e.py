from playwright.sync_api import sync_playwright, expect
import pytest
import urllib.request
from page_objects import TaskPage

BASE_URL = "http://localhost:5000"

@pytest.fixture(autouse=True)
def limpiar_estado():
    urllib.request.urlopen(
        urllib.request.Request(f"{BASE_URL}/tasks/clear", method="POST")
    )
    yield
    urllib.request.urlopen(
        urllib.request.Request(f"{BASE_URL}/tasks/clear", method="POST")
    )

class TestTaskPage:
    def test_crear_tarea_aparece_en_lista(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("Estudiar Playwright")
            
            assert tp.contar_tareas() == 1
            assert tp.titulo_de_tarea(0) == "Estudiar Playwright"
            browser.close()

    def test_completar_tarea_muestra_badge(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("Tarea para completar")
            assert not tp.esta_completada(0)
            
            tp.completar_tarea(0)
            assert tp.esta_completada(0)
            browser.close()

    def test_eliminar_tarea_desaparece(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("Tarea para eliminar")
            assert tp.contar_tareas() == 1
            
            tp.eliminar_tarea(0)
            assert tp.contar_tareas() == 0
            assert tp.lista_vacia()
            browser.close()

    def test_flujo_completo_crear_completar_eliminar(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("Flujo completo")
            assert tp.contar_tareas() == 1
            assert tp.titulo_de_tarea(0) == "Flujo completo"
            
            tp.completar_tarea(0)
            assert tp.esta_completada(0)
            
            tp.eliminar_tarea(0)
            assert tp.contar_tareas() == 0
            assert tp.lista_vacia()
            browser.close()

    def test_crear_tarea_con_titulo_vacio(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("")
            
            assert tp.contar_tareas() == 0
            assert tp.lista_vacia()
            browser.close()

    def test_crear_tarea_duplicada(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            tp.crear_tarea("Tarea repetida")
            tp.crear_tarea("Tarea repetida")
            
            assert tp.contar_tareas() == 1
            assert tp.titulo_de_tarea(0) == "Tarea repetida"
            browser.close()

    def test_mensaje_lista_vacia(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            assert tp.lista_vacia()
            assert tp.mensaje_lista_vacia.is_visible()
            assert "No hay tareas" in tp.mensaje_lista_vacia.inner_text()
            
            tp.crear_tarea("Nueva tarea")
            assert not tp.lista_vacia()
            
            tp.eliminar_tarea(0)
            assert tp.lista_vacia()
            browser.close()

    def test_crear_multiples_tareas_verificar_orden(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            tp = TaskPage(page, BASE_URL)
            tp.navegar()
            
            titulos = ["Primera tarea", "Segunda tarea", "Tercera tarea"]
            for titulo in titulos:
                tp.crear_tarea(titulo)
            
            assert tp.contar_tareas() == 3
            
            assert tp.titulo_de_tarea(0) == "Primera tarea"
            assert tp.titulo_de_tarea(1) == "Segunda tarea"
            assert tp.titulo_de_tarea(2) == "Tercera tarea"
            browser.close()