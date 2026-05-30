class TaskPage:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url

    def ir_a_inicio(self):
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

    def crear_tarea(self, titulo):
        self.page.fill("[data-testid='input-titulo']", titulo)
        self.page.click("[data-testid='btn-agregar']")
        self.page.wait_for_load_state("networkidle")

    def completar_tarea(self, titulo):
        item = self.page.locator(
            f"[data-testid='tarea-item']:has([data-testid='tarea-titulo']:has-text('{titulo}'))"
        )
        item.locator("[data-testid='btn-completar']").click()
        self.page.wait_for_load_state("networkidle")

    def eliminar_tarea(self, titulo):
        item = self.page.locator(
            f"[data-testid='tarea-item']:has([data-testid='tarea-titulo']:has-text('{titulo}'))"
        )
        item.locator("[data-testid='btn-eliminar']").click()
        self.page.wait_for_load_state("networkidle")

    def obtener_titulos(self):
        return self.page.locator("[data-testid='tarea-titulo']").all_inner_texts()

    def tarea_existe(self, titulo):
        return titulo in self.obtener_titulos()

    def tarea_completada(self, titulo):
        item = self.page.locator(
            f"[data-testid='tarea-item']:has([data-testid='tarea-titulo']:has-text('{titulo}'))"
        )
        return item.locator("[data-testid='badge-completada']").count() > 0

    def lista_vacia(self):
        return self.page.locator("[data-testid='msg-lista-vacia']").count() > 0