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
        Agrega una nueva tarea.
        Retorna True si se agregó, False en caso de duplicado o título inválido.
        Mantiene consistencia si la notificación falla.
        """
        if not title or not str(title).strip():
            return False

        tasks = self.storage.load()
        if title in [t['title'] for t in tasks]:
            return False

        original_tasks = list(tasks)
        tasks.append({"title": title, "done": False})
        self.storage.save(tasks)
        try:
            self.notifier.send(f"Tarea '{title}' creada")
        except Exception:
            self.storage.save(original_tasks)
            raise
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