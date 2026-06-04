from playwright.sync_api import Page

class TaskPage:
    def __init__(self, page: Page):
        self.page = page
        
        self.url_base = page.url

        """Definimos los locators usando atributos data-testid. Estos atributos se usan como
        una pactica recomendada, si un disenador cambia el color del boton o mueve el input 
        de lugar, el data-testid se mantiene igual y el test no se rompe de manera fragil."""

        self.input_titulo = page.locator("[data-testid='input-titulo']")
        self.btn_agregar = page.locator("[data-testid='btn-agregar']")
        
        """Al definir self.tarea_items señalamos todos los elementos con ese ID, playwright no 
        captura un solo elemento estatico, sino que cre una referncia a una coleccion de elementos.
        Esto nos permite contar cuantas tareas hay en la interfaz en tiempo real."""

        self.lista_tareas = page.locator("[data-testid='lista-tareas']")
        self.tarea_items = page.locator("[data-testid='tarea-item']")
        self.msg_vacia = page.locator("[data-testid='msg-lista-vacia']")
    def ir_a_inicio(self):

        """Navega a la ruta principal de la aplicación. Método de acción, este método ayuda a 
        garantizar el aislamiento entre tests. Al llamarlo al inicio de cada prueba, forzamos 
        que cada test empiece desde un punto limpio en la URL inicial de la aplicación, 
        evitando que la contaminación de estados o depender del éxito de fallos de URLs 
        de los tests anteriores."""
    
        self.page.goto(self.url_base)
    def crear_tarea(self, titulo: str):

        """Llena en formulario y agrega una nueva tarea: automatiza la acción de crear una 
        tarea; escribe el texto en el cuadro de texto y luego hace click en el botón de 
        añadir. El archivo no necesita saber cómo se crea una tarea, simplemente llama 
        a la función .crear_tarea(“Estudiar”), logrando que las pruebas tengan un lenguaje 
        más limpio y legible."""

        self.input_titulo.fill(titulo)
        self.btn_agregar.click()

    def obtener_tarea(self, index: int):

        """Devuelve el locator de una tarea específica por su índice. Lo logra mediante la 
        función .nth(index) de playwright. Otorga escalabilidad y dinamismo al framework 
        de pruebas, este método permite reutilizar la misma lógica para validar cualquier 
        posición en listas masivas. """

        return self.tarea_items.nth(index)
    def completar_tarea(self, index: int):

        """Esta función hace clic en el botón de completar de una tarea específica. 
        También evita falsos positivos en las pruebas. Al encadenar tarea.locator(), 
        nos aseguramos de interactuar solo con el botón de completar la fila seleccionada, 
        garantizando una automatización robusta."""

        tarea = self.obtener_tarea(index)
        tarea.locator("[data-testid='btn-completar']").click()      
    def eliminar_tarea(self, index: int):

        """Hacer clic en el botón de eliminar de una tarea especifica: Su función es 
        completar el ciclo de vida de la entidad de tareas permitiendo que el archivo 
        de pruebas ejecute flujos de integración completos."""

        tarea = self.obtener_tarea(index)
        tarea.locator("[data-testid='btn-eliminar']").click()