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
        Retorna True si se agregó, False en caso de duplicado.
        Rechaza títulos vacíos y revierte el alta si falla la notificación.
        """
        # No dejamos pasar tareas vacías.
        if not title or not title.strip():
            raise ValueError("El título no puede estar vacío")

        title = title.strip()
        tasks = self.storage.load()
        if title in [t['title'] for t in tasks]:
            return False

        # Guardamos lo que había por si algo falla después.
        previous_tasks = [dict(task) for task in tasks]
        tasks.append({"title": title, "done": False})
        self.storage.save(tasks)

        try:
            self.notifier.send(f"Tarea '{title}' creada")
        except Exception:
            # Si el aviso falla, dejamos todo como estaba.
            self.storage.save(previous_tasks)
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