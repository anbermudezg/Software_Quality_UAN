"""
page_objects.py — Page Object Model para el Gestor de Tareas.

Encapsula todos los locators y acciones sobre la UI en una sola clase,
desacoplando los tests del HTML concreto.
"""

from playwright.sync_api import Page, expect


class TaskPage:
    """
    Representa la página principal del gestor de tareas.
    Todos los locators usan data-testid para máxima estabilidad.
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

        # ── Locators ────────────────────────────────────────────────
        self.input_titulo    = page.locator("[data-testid='input-titulo']")
        self.btn_agregar     = page.locator("[data-testid='btn-agregar']")
        self.lista_tareas    = page.locator("[data-testid='lista-tareas']")
        self.msg_lista_vacia = page.locator("[data-testid='msg-lista-vacia']")
        self.page_title      = page.locator("[data-testid='page-title']")

    # ── Navegación ───────────────────────────────────────────────────

    def goto(self):
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

    # ── Acciones ─────────────────────────────────────────────────────

    def crear_tarea(self, titulo: str):
        """Rellena el formulario y envía."""
        self.input_titulo.fill(titulo)
        self.btn_agregar.click()
        self.page.wait_for_load_state("networkidle")

    def completar_tarea(self, titulo: str):
        """Hace clic en 'Completar' de la tarea con ese título."""
        item = self._item_por_titulo(titulo)
        item.locator("[data-testid='btn-completar']").click()
        self.page.wait_for_load_state("networkidle")

    def eliminar_tarea(self, titulo: str):
        """Hace clic en 'Eliminar' de la tarea con ese título."""
        item = self._item_por_titulo(titulo)
        item.locator("[data-testid='btn-eliminar']").click()
        self.page.wait_for_load_state("networkidle")

    # ── Consultas ────────────────────────────────────────────────────

    def tarea_existe(self, titulo: str) -> bool:
        return self._item_por_titulo(titulo).count() > 0

    def tarea_esta_completada(self, titulo: str) -> bool:
        item = self._item_por_titulo(titulo)
        return item.locator("[data-testid='badge-completada']").count() > 0

    def lista_esta_vacia(self) -> bool:
        return self.msg_lista_vacia.is_visible()

    def titulos_en_orden(self) -> list[str]:
        """Devuelve los títulos de todas las tareas en el orden de la lista."""
        return self.page.locator("[data-testid='tarea-titulo']").all_inner_texts()

    # ── Helpers privados ─────────────────────────────────────────────

    def _item_por_titulo(self, titulo: str):
        """Localiza el <li> cuyo tarea-titulo coincide exactamente."""
        return self.page.locator(
            f"[data-testid='tarea-item']:has([data-testid='tarea-titulo']:text-is('{titulo}'))"
        )
