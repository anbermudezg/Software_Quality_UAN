from playwright.sync_api import Page, expect

class TaskPage:
    def __init__(self, page: Page):
        self.page = page
        self.input_titulo = page.get_by_test_id("input-titulo")
        self.btn_agregar = page.get_by_test_id("btn-agregar")
        self.lista_tareas = page.get_by_test_id("lista-tareas")
        self.msg_lista_vacia = page.get_by_test_id("msg-lista-vacia")

    def crear_tarea(self, titulo: str):
        self.input_titulo.fill(titulo)
        self.btn_agregar.click()

    def completar_tarea(self, titulo: str):
        item = self._get_item(titulo)
        item.get_by_test_id("btn-completar").click()

    def eliminar_tarea(self, titulo: str):
        item = self._get_item(titulo)
        item.get_by_test_id("btn-eliminar").click()

    def _get_item(self, titulo: str):
        return self.page.locator(
            f'[data-testid="tarea-item"]:has([data-testid="tarea-titulo"]:text("{titulo}"))'
        )

    def tarea_visible(self, titulo: str) -> bool:
        return self._get_item(titulo).is_visible()

    def tarea_completada(self, titulo: str) -> bool:
        item = self._get_item(titulo)
        return item.get_by_test_id("badge-completada").is_visible()

    def titulo_tachado(self, titulo: str) -> bool:
        item = self._get_item(titulo)
        span = item.get_by_test_id("tarea-titulo")
        return "done" in (span.get_attribute("class") or "")

    def contar_tareas(self) -> int:
        return self.page.locator('[data-testid="tarea-item"]').count()

    def esperar_tarea_visible(self, titulo: str):
        expect(self._get_item(titulo)).to_be_visible()

    def esperar_tarea_oculta(self, titulo: str):
        expect(self._get_item(titulo)).to_have_count(0)

    def esperar_badge_completada(self, titulo: str):
        item = self._get_item(titulo)
        expect(item.get_by_test_id("badge-completada")).to_be_visible()

    def esperar_lista_vacia(self):
        expect(self.page.get_by_test_id("msg-lista-vacia")).to_be_visible()
