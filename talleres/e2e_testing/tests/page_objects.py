from playwright.sync_api import Page, expect

class TaskPage:
    """Page Object para el Gestor de Tareas."""

    def __init__(self, page: Page, base_url: str = "http://localhost:5000"):
        self._page = page
        self._base_url = base_url

    def navegar(self):
        self._page.goto(self._base_url)

    @property
    def input_titulo(self):
        return self._page.locator("[data-testid='input-titulo']")

    @property
    def btn_agregar(self):
        return self._page.locator("[data-testid='btn-agregar']")

    @property
    def lista_tareas(self):
        return self._page.locator("[data-testid='tarea-item']")

    @property
    def mensaje_lista_vacia(self):
        return self._page.locator("[data-testid='msg-lista-vacia']")

    def crear_tarea(self, titulo: str):
        self.input_titulo.fill(titulo)
        self.btn_agregar.click()
        self._page.wait_for_load_state("networkidle")

    def completar_tarea(self, indice: int = 0):
        self._page.locator("[data-testid='btn-completar']").nth(indice).click()
        self._page.wait_for_load_state("networkidle")

    def eliminar_tarea(self, indice: int = 0):
        self._page.locator("[data-testid='btn-eliminar']").nth(indice).click()
        self._page.wait_for_load_state("networkidle")

    def contar_tareas(self) -> int:
        return self.lista_tareas.count()

    def titulo_de_tarea(self, indice: int = 0) -> str:
        return self._page.locator("[data-testid='tarea-titulo']").nth(indice).inner_text()

    def esta_completada(self, indice: int = 0) -> bool:
        return self._page.locator("[data-testid='badge-completada']").nth(indice).is_visible()

    def lista_vacia(self) -> bool:
        return self.mensaje_lista_vacia.is_visible()