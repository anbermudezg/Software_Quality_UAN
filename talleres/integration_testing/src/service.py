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
        Error de integración: no valida título vacío,
        y no revierte la operación si la notificación falla.
        """
        tasks = self.storage.load()
        if not title.strip():
            return False
        if title in [t['title'] for t in tasks]:
            return False
        tasks.append({"title": title, "done": False})
        try:
            self.storage.save(tasks)
        except Exception as e:
            print(f"Error al guardar tarea: {e}")
            return False
        try:
            self.notifier.send(f"Tarea '{title}' creada")
        except Exception as e:
            print(f"Error al enviar notificación: {e}")
            self.storage.save(tasks[:-1])
            return False
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