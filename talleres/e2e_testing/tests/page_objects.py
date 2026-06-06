from playwright.sync_api import Page


class TaskPage:
    """Page Object para el Gestor de Tareas."""

    def __init__(self, page: Page):
        self._page = page

    @property
    def title_input(self):
        return self._page.locator("[data-testid='input-titulo']")

    @property
    def add_button(self):
        return self._page.locator("[data-testid='btn-agregar']")

    @property
    def task_items(self):
        return self._page.locator("[data-testid='tarea-item']")

    @property
    def empty_message(self):
        return self._page.locator("[data-testid='msg-lista-vacia']")

    def create_task(self, title: str):
        self.title_input.fill(title)
        self.add_button.click()
        self._page.wait_for_selector("[data-testid='tarea-item'], [data-testid='msg-lista-vacia']")

    def task_titles(self) -> list[str]:
        return [text.strip() for text in self._page.locator("[data-testid='tarea-titulo']").all_text_contents()]

    def task_count(self) -> int:
        return self.task_items.count()

    def has_empty_list_message(self) -> bool:
        return self.empty_message.is_visible()

    def empty_list_message_text(self) -> str:
        return self.empty_message.inner_text().strip()

    def _task_item_for_title(self, title: str):
        return self.task_items.filter(has_text=title).first

    def complete_task_by_title(self, title: str):
        item = self._task_item_for_title(title)
        complete_button = item.locator("[data-testid='btn-completar']")
        complete_button.click()
        self._page.wait_for_selector("[data-testid='tarea-item'], [data-testid='msg-lista-vacia']")

    def delete_task_by_title(self, title: str):
        item = self._task_item_for_title(title)
        delete_button = item.locator("[data-testid='btn-eliminar']")
        delete_button.click()
        self._page.wait_for_selector("[data-testid='tarea-item'], [data-testid='msg-lista-vacia']")

    def is_task_completed_by_title(self, title: str) -> bool:
        item = self._task_item_for_title(title)
        badge = item.locator("[data-testid='badge-completada']")
        return badge.count() == 1 and badge.is_visible()
