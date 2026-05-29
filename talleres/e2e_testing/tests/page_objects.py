"""Page Objects para la suite E2E del gestor de tareas."""

from playwright.sync_api import Page, expect


class TaskPage:
    def __init__(self, page: Page):
        self.page = page

    def create_task(self, title: str):
        # Lleno el formulario y envío la tarea como lo haría un usuario.
        self.page.get_by_test_id("input-titulo").fill(title)
        self.page.get_by_test_id("btn-agregar").click()

    def task_items(self):
        return self.page.get_by_test_id("tarea-item")

    def task_titles(self):
        return self.page.get_by_test_id("tarea-titulo")

    def task_title(self, title: str):
        return self.task_titles().filter(has_text=title)

    def task_item(self, title: str):
        return self.task_items().filter(has_text=title)

    def complete_task(self, title: str):
        # Busco la tarea exacta y presiono completar.
        self.task_item(title).get_by_test_id("btn-completar").click()

    def delete_task(self, title: str):
        # Igual, pero ahora para borrarla.
        self.task_item(title).get_by_test_id("btn-eliminar").click()

    def expect_task_visible(self, title: str):
        expect(self.task_item(title)).to_have_count(1)
        expect(self.task_title(title)).to_have_text(title)

    def expect_task_hidden(self, title: str):
        expect(self.task_item(title)).to_have_count(0)

    def expect_completed(self, title: str):
        # Verifico que la tarea cambió de estado de verdad.
        item = self.task_item(title)
        expect(item).to_have_count(1)
        expect(item.get_by_test_id("badge-completada")).to_be_visible()
        expect(item.get_by_test_id("tarea-titulo")).to_have_class("task-title done")

    def expect_empty_state(self):
        # Cuando no hay tareas, la pantalla debe mostrar el mensaje vacío.
        expect(self.page.get_by_test_id("msg-lista-vacia")).to_be_visible()
        expect(self.task_items()).to_have_count(0)

    def expect_task_titles(self, titles: list[str]):
        expect(self.task_titles()).to_have_text(titles)