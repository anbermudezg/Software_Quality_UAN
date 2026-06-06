"""
Page Object Model for the Tasks application.
"""
from __future__ import annotations

from playwright.sync_api import expect


class TaskPage:
    def __init__(self, page):
        self.page = page

    # Locators
    @property
    def page_title(self):
        return self.page.locator("[data-testid='page-title']")

    @property
    def form_nueva_tarea(self):
        return self.page.locator("[data-testid='form-nueva-tarea']")

    @property
    def input_titulo(self):
        return self.page.locator("[data-testid='input-titulo']")

    @property
    def btn_agregar(self):
        return self.page.locator("[data-testid='btn-agregar']")

    @property
    def lista_tareas(self):
        return self.page.locator("[data-testid='lista-tareas']")

    def tarea_item(self, task_id: str):
        return self.page.locator(f"[data-testid='tarea-item'][data-task-id='{task_id}']")

    def tarea_titulo(self, task_id: str):
        return self.page.locator(f"[data-testid='tarea-item'][data-task-id='{task_id}'] [data-testid='tarea-titulo']")

    def badge_completada(self, task_id: str):
        return self.page.locator(f"[data-testid='tarea-item'][data-task-id='{task_id}'] [data-testid='badge-completada']")

    def btn_completar(self, task_id: str):
        return self.page.locator(f"[data-testid='tarea-item'][data-task-id='{task_id}'] [data-testid='btn-completar']")

    def btn_eliminar(self, task_id: str):
        return self.page.locator(f"[data-testid='tarea-item'][data-task-id='{task_id}'] [data-testid='btn-eliminar']")

    def msg_lista_vacia(self):
        return self.page.locator("[data-testid='msg-lista-vacia']")

    # Actions
    def goto(self, base_url):
        self.page.goto(base_url)

    def create_task(self, title: str):
        self.input_titulo.fill(title)
        self.btn_agregar.click()
        # Wait for the task to appear (optional, but we can wait for the list to update)
        self.page.wait_for_load_state("networkidle")

    def complete_task(self, task_id: str):
        self.btn_completar(task_id).click()
        self.page.wait_for_load_state("networkidle")

    def delete_task(self, task_id: str):
        self.btn_eliminar(task_id).click()
        self.page.wait_for_load_state("networkidle")

    def clear_tasks(self, base_url):
        # Use the clear endpoint via request
        self.page.request.post(f"{base_url}/tasks/clear")

    # Getters / Assertions helpers
    def get_task_count(self):
        return self.lista_tareas.locator("[data-testid='tarea-item']").count()

    def get_task_titles(self):
        return self.page.locator("[data-testid='tarea-titulo']").all_inner_texts()

    def is_task_completed(self, task_id: str) -> bool:
        titulo = self.tarea_titulo(task_id)
        return titulo.evaluate("el => el.classList.contains('done')")

    def badge_visible(self, task_id: str) -> bool:
        return self.badge_completada(task_id).is_visible()

    def empty_message_visible(self) -> bool:
        return self.msg_lista_vacia().is_visible()

    def wait_for_task(self, task_id: str):
        self.tarea_item(task_id).wait_for(state="attached")