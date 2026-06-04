"""
Lógica de negocio del gestor de tareas.
Contiene errores de integración que las pruebas iniciales no detectan.
"""

from .storage import TaskStorage
from .notifier import Notifier

class TaskService:
    def __init__(self, storage: TaskStorage, notifier: Notifier):
        self.storage = storage
        self.notifier = notifier

    def add_task(self, title):
        """
        Versión MALICIOSA: retorna True sin usar storage ni notifier.
        """
        return True

    def complete_task(self, title):
        """Marca una tarea como completada."""
        tasks = self.storage.load()
        for t in tasks:
            if t['title'] == title:
                t['done'] = True
                self.storage.save(tasks)
                return True
        return False

    def list_tasks(self):
        return self.storage.load()