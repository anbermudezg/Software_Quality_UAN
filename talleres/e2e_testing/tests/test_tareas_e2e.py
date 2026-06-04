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
from tests.page_objects import TaskPage

class TestPaginaPrincipal:
    """Pruebas débiles de la página principal."""

    def test_pagina_carga(self, page):
        """Verifica que la página responde (solo código HTTP 200)."""
        # Esta prueba pasa aunque la página esté completamente rota
        # siempre que no lance un error 500
        assert page.url is not None

    def test_titulo_visible(self, page):
        """Verifica que el título de la página existe."""
        # Aserción débil: solo verifica que el elemento existe, no su contenido
        title = page.locator("[data-testid='page-title']")
        assert title.count() >= 0  # Siempre pasa, incluso si no existe


class TestCrearTarea:
    """Pruebas débiles de creación de tareas."""

    def test_formulario_presente(self, page):
        """Verifica que el formulario existe en la página."""
        form = page.locator("[data-testid='form-nueva-tarea']")
        # Aserción débil: no verifica que el formulario funcione
        assert form.count() >= 0

    def test_agregar_tarea_no_lanza_error(self, page):
        """Verifica que agregar una tarea no lanza excepción de red."""
        page.fill("[data-testid='input-titulo']", "Mi tarea")
        page.click("[data-testid='btn-agregar']")
        # No verifica que la tarea realmente aparezca en la lista


class TestCompletarTarea:
    """Pruebas débiles de completar tareas."""

    def test_completar_tarea_no_lanza_error(self, page):
        """Verifica que el flujo completar no lanza error de red."""
        # Primero creamos una tarea
        page.fill("[data-testid='input-titulo']", "Tarea a completar")
        page.click("[data-testid='btn-agregar']")
        page.wait_for_load_state("networkidle")

        # Intentamos completarla (sin verificar el resultado)
        btn = page.locator("[data-testid='btn-completar']").first
        if btn.count() > 0:
            btn.click()
            page.wait_for_load_state("networkidle")
        # No verifica que la tarea quede marcada como completada


class TestCrearTareaFuerte:
    """Pruebas robustas utilizando expect() para verificar el estado de la UI."""

    def test_crear_tarea_exitoso(self, page):
        """Verifica que la tarea aparece en la lista tras crearla."""
        titulo_tarea = "Tarea Robusta"
        
        page.fill("[data-testid='input-titulo']", titulo_tarea)
        page.click("[data-testid='btn-agregar']")
        
        # Verificamos que el título aparece en la lista con expect()
        tarea_item = page.locator("[data-testid='tarea-titulo']").first
        expect(tarea_item).to_have_text(titulo_tarea)

    def test_completar_tarea_exitoso(self, page):
        """Verifica que al completar, el badge de 'Completada' aparece."""
        page.fill("[data-testid='input-titulo']", "Tarea a completar")
        page.click("[data-testid='btn-agregar']")
        
        # Completamos la tarea
        page.click("[data-testid='btn-completar']")
        
        # Verificamos la aparición del badge de estado
        badge = page.locator("[data-testid='badge-completada']")
        expect(badge).to_be_visible()
        expect(badge).to_contain_text("✓ Completada")

    def test_eliminar_tarea_exitoso(self, page):
        """Verifica que la tarea desaparece de la lista tras eliminarla."""
        page.fill("[data-testid='input-titulo']", "Tarea a eliminar")
        page.click("[data-testid='btn-agregar']")
        
        # Aseguramos que existe antes de eliminar
        expect(page.locator("[data-testid='tarea-item']")).to_have_count(1)
        
        # Eliminamos
        page.click("[data-testid='btn-eliminar']")
        
        # Verificamos que la lista está vacía
        expect(page.locator("[data-testid='tarea-item']")).to_have_count(0)
        
class TestFlujoTareaFuerte:
    """Pruebas robustas usando el Page Object Model (POM)."""

    def test_flujo_completo_usuario(self, page, live_server):
        """Escenario: Crear -> Completar -> Verificar -> Eliminar."""
        tp = TaskPage(page, live_server)
        tp.navegar()
        
        # 1. Crear tarea
        titulo = "Tarea de Flujo Completo"
        tp.crear_tarea(titulo)
        assert tp.contar_tareas() == 1
        assert tp.titulo_de_tarea(0) == titulo
        
        # 2. Completar tarea
        tp.completar_tarea(0)
        assert tp.esta_completada(0)
        
        # 3. Eliminar tarea
        tp.eliminar_tarea(0)
        
        # 4. Verificar que desapareció
        assert tp.contar_tareas() == 0
        assert tp.lista_vacia()
        
class TestCasosExtemos:
    def test_crear_tarea_titulo_vacio(self, page, live_server):
        """Verifica que no se crea una tarea con título vacío."""
        tp = TaskPage(page, live_server)
        tp.navegar()
        
        # Intentamos crear con título vacío
        tp.crear_tarea("")
        
        # Verificamos que la lista sigue vacía
        assert tp.contar_tareas() == 0
        assert tp.lista_vacia()

    def test_crear_tareas_duplicadas(self, page, live_server):
        """Verifica que el sistema permite tareas con el mismo título."""
        tp = TaskPage(page, live_server)
        tp.navegar()
        
        tp.crear_tarea("Estudiar")
        tp.crear_tarea("Estudiar")
        
        assert tp.contar_tareas() == 2
        assert tp.titulo_de_tarea(0) == "Estudiar"
        assert tp.titulo_de_tarea(1) == "Estudiar"

    def test_lista_muestra_mensaje_vacio(self, page, live_server):
        """Verifica el estado inicial de lista vacía."""
        tp = TaskPage(page, live_server)
        tp.navegar()
        
        # Verificamos visibilidad del mensaje
        assert tp.lista_vacia()
        expect(page.locator("[data-testid='msg-lista-vacia']")).to_have_text("No hay tareas")

    def test_orden_de_tareas(self, page, live_server):
        """Verifica que las tareas mantienen el orden de inserción."""
        tp = TaskPage(page, live_server)
        tp.navegar()
        
        titulos = ["Primero", "Segundo", "Tercero"]
        for t in titulos:
            tp.crear_tarea(t)
            
        # Verificamos que el orden coincide
        assert tp.titulos_de_todas_las_tareas() == titulos