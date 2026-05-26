# -*- coding: utf-8 -*-
import pytest
from page_objects import TaskPage

class TestCrearTareaFuerte:
    def test_titulo_aparece_en_lista(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Comprar leche")
        tp.esperar_tarea_visible("Comprar leche")

    def test_contador_aumenta_al_crear(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Tarea uno")
        tp.crear_tarea("Tarea dos")
        assert tp.contar_tareas() == 2

    def test_multiples_tareas_visibles(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Alfa")
        tp.crear_tarea("Beta")
        tp.crear_tarea("Gamma")
        tp.esperar_tarea_visible("Alfa")
        tp.esperar_tarea_visible("Beta")
        tp.esperar_tarea_visible("Gamma")

    def test_mensaje_vacio_desaparece_al_crear(self, page):
        tp = TaskPage(page)
        tp.esperar_lista_vacia()
        tp.crear_tarea("Nueva tarea")
        tp.esperar_tarea_visible("Nueva tarea")

class TestCompletarTareaFuerte:
    def test_badge_completada_aparece(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Estudiar")
        tp.completar_tarea("Estudiar")
        tp.esperar_badge_completada("Estudiar")

    def test_titulo_tiene_clase_done(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Leer libro")
        tp.completar_tarea("Leer libro")
        tp.esperar_badge_completada("Leer libro")
        assert tp.titulo_tachado("Leer libro")

    def test_tarea_completada_sigue_en_lista(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Hacer ejercicio")
        tp.completar_tarea("Hacer ejercicio")
        tp.esperar_tarea_visible("Hacer ejercicio")

    def test_completar_no_afecta_otras_tareas(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Tarea A")
        tp.crear_tarea("Tarea B")
        tp.completar_tarea("Tarea A")
        tp.esperar_badge_completada("Tarea A")
        assert not tp.tarea_completada("Tarea B")

class TestEliminarTareaFuerte:
    def test_tarea_desaparece_al_eliminar(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Borrar esto")
        tp.eliminar_tarea("Borrar esto")
        tp.esperar_tarea_oculta("Borrar esto")

    def test_contador_disminuye_al_eliminar(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Una")
        tp.crear_tarea("Dos")
        tp.eliminar_tarea("Una")
        assert tp.contar_tareas() == 1

    def test_eliminar_no_afecta_otras(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Quedar")
        tp.crear_tarea("Eliminar")
        tp.eliminar_tarea("Eliminar")
        tp.esperar_tarea_visible("Quedar")

    def test_lista_vacia_tras_eliminar_ultima(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Unica tarea")
        tp.eliminar_tarea("Unica tarea")
        tp.esperar_lista_vacia()

class TestFlujoCompleto:
    def test_crear_completar_eliminar(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Flujo completo")
        tp.esperar_tarea_visible("Flujo completo")
        tp.completar_tarea("Flujo completo")
        tp.esperar_badge_completada("Flujo completo")
        assert tp.titulo_tachado("Flujo completo")
        tp.eliminar_tarea("Flujo completo")
        tp.esperar_tarea_oculta("Flujo completo")
        tp.esperar_lista_vacia()

class TestCasosExtremos:
    def test_titulo_vacio_no_crea_tarea(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("")
        tp.esperar_lista_vacia()

    def test_tareas_duplicadas_no_se_repiten(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Duplicada")
        tp.crear_tarea("Duplicada")
        assert tp.contar_tareas() == 1

    def test_lista_vacia_al_inicio(self, page):
        tp = TaskPage(page)
        tp.esperar_lista_vacia()

    def test_orden_de_creacion_se_mantiene(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Primera")
        tp.crear_tarea("Segunda")
        items = page.locator('[data-testid="tarea-titulo"]').all_text_contents()
        assert items[0].strip() == "Primera"
        assert items[1].strip() == "Segunda"

    def test_caracteres_especiales(self, page):
        tp = TaskPage(page)
        tp.crear_tarea("Tarea especial: cafe")
        tp.esperar_tarea_visible("Tarea especial: cafe")
