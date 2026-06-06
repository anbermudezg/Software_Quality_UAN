from tests.page_objects import TaskPage


class TestCrearTareaFuerte:
    def test_crear_tarea_muestra_titulo_en_lista(self, page):
        task_page = TaskPage(page)
        titulo = "Tarea fuerte"

        task_page.create_task(titulo)

        assert task_page.task_titles() == [titulo]
        assert not task_page.has_empty_list_message()


class TestCompletarTareaFuerte:
    def test_completar_tarea_muestra_badge_y_estado_completado(self, page):
        task_page = TaskPage(page)
        titulo = "Tarea completa"

        task_page.create_task(titulo)
        task_page.complete_task_by_title(titulo)

        assert task_page.is_task_completed_by_title(titulo)
        assert titulo in task_page.task_titles()


class TestEliminarTareaFuerte:
    def test_eliminar_tarea_desaparece_de_lista(self, page):
        task_page = TaskPage(page)
        titulo = "Tarea a eliminar"

        task_page.create_task(titulo)
        task_page.delete_task_by_title(titulo)

        assert titulo not in task_page.task_titles()
        assert task_page.task_count() == 0
        assert task_page.has_empty_list_message()


class TestFlujoCompleto:
    def test_crear_completar_eliminar_tarea(self, page):
        task_page = TaskPage(page)
        titulo = "Flujo completo"

        task_page.create_task(titulo)
        assert titulo in task_page.task_titles()

        task_page.complete_task_by_title(titulo)
        assert task_page.is_task_completed_by_title(titulo)

        task_page.delete_task_by_title(titulo)
        assert titulo not in task_page.task_titles()
        assert task_page.has_empty_list_message()


class TestCasosExtremos:
    def test_crear_tarea_con_titulo_vacio_no_agrega_nada(self, page):
        task_page = TaskPage(page)

        task_page.create_task("")

        assert task_page.task_count() == 0
        assert task_page.has_empty_list_message()

    def test_crear_tarea_con_espacios_vacios_no_agrega_nada(self, page):
        task_page = TaskPage(page)

        task_page.create_task("   ")

        assert task_page.task_count() == 0
        assert task_page.has_empty_list_message()

    def test_crear_tarea_duplicada_no_duplica_la_lista(self, page):
        task_page = TaskPage(page)
        titulo = "Tarea duplicada"

        task_page.create_task(titulo)
        task_page.create_task(titulo)

        assert task_page.task_count() == 1
        assert task_page.task_titles() == [titulo]

    def test_lista_vacia_muestra_mensaje(self, page):
        task_page = TaskPage(page)

        assert task_page.task_count() == 0
        assert task_page.has_empty_list_message()
        assert task_page.empty_list_message_text() == "No hay tareas. ¡Agrega una!"

    def test_crear_multiples_tareas_preserva_el_orden(self, page):
        task_page = TaskPage(page)
        titulos = ["Tarea uno", "Tarea dos", "Tarea tres"]

        for titulo in titulos:
            task_page.create_task(titulo)

        assert task_page.task_titles() == titulos
