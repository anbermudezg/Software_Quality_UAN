"""
page_objects.py — Page Object Model para el Gestor de Tareas.

Encapsula todos los locators y acciones de la UI en una sola clase,
desacoplando los tests de los detalles de implementación del HTML.
"""

from playwright.sync_api import Page, expect


class TaskPage:
    """
    Page Object para la página principal del Gestor de Tareas.

    Centraliza los locators (usando data-testid) y las acciones
    de usuario, de modo que si la UI cambia solo se modifica aquí.
    """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

        # ── Locators ──────────────────────────────────────────────────────────
        self.page_title      = page.locator("[data-testid='page-title']")
        self.form            = page.locator("[data-testid='form-nueva-tarea']")
        self.input_titulo    = page.locator("[data-testid='input-titulo']")
        self.btn_agregar     = page.locator("[data-testid='btn-agregar']")
        self.lista_tareas    = page.locator("[data-testid='lista-tareas']")
        self.msg_lista_vacia = page.locator("[data-testid='msg-lista-vacia']")

    # ── Acciones básicas ──────────────────────────────────────────────────────

    def goto(self):
        """Navega a la página principal."""
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

    def crear_tarea(self, titulo: str):
        """Rellena el formulario y envía una nueva tarea."""
        self.input_titulo.fill(titulo)
        self.btn_agregar.click()
        self.page.wait_for_load_state("networkidle")

    def completar_tarea(self, titulo: str):
        """Hace clic en el botón Completar de la tarea con el título dado."""
        item = self._get_item_by_title(titulo)
        item.locator("[data-testid='btn-completar']").click()
        self.page.wait_for_load_state("networkidle")

    def eliminar_tarea(self, titulo: str):
        """Hace clic en el botón Eliminar de la tarea con el título dado."""
        item = self._get_item_by_title(titulo)
        item.locator("[data-testid='btn-eliminar']").click()
        self.page.wait_for_load_state("networkidle")

    # ── Consultas de estado ───────────────────────────────────────────────────

    def titulo_visible(self, titulo: str) -> bool:
        """Retorna True si algún elemento tarea-titulo contiene el texto dado."""
        titulos = self.page.locator("[data-testid='tarea-titulo']")
        for i in range(titulos.count()):
            if titulos.nth(i).inner_text().strip() == titulo:
                return True
        return False

    def tarea_esta_completada(self, titulo: str) -> bool:
        """Retorna True si la tarea tiene el badge de completada."""
        item = self._get_item_by_title(titulo)
        return item.locator("[data-testid='badge-completada']").count() > 0

    def tarea_existe(self, titulo: str) -> bool:
        """Retorna True si la tarea con ese título está en la lista."""
        return self._get_item_by_title(titulo).count() > 0

    def lista_esta_vacia(self) -> bool:
        """Retorna True si se muestra el mensaje de lista vacía."""
        return self.msg_lista_vacia.is_visible()

    def contar_tareas(self) -> int:
        """Retorna el número de tareas visibles en la lista."""
        return self.page.locator("[data-testid='tarea-item']").count()

    def titulos_en_orden(self) -> list[str]:
        """Retorna la lista de títulos en el orden en que aparecen."""
        locators = self.page.locator("[data-testid='tarea-titulo']")
        return [locators.nth(i).inner_text().strip() for i in range(locators.count())]

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _get_item_by_title(self, titulo: str):
        """Localiza el li de la tarea filtrando por el texto del título."""
        return self.page.locator(
            f"[data-testid='tarea-item']:has([data-testid='tarea-titulo']:text-is('{titulo}'))"
        )
