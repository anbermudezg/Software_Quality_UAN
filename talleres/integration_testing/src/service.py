"""
Lógica de negocio del gestor de tareas.
Implementado por: Jovany Gutierrez Vergara (Código: 12242217515).
Corrige los errores de integración originales para asegurar la consistencia mediante
un mecanismo de Rollback en caso de fallos en el Notificador y validación de entradas.
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
        Retorna True si se agregó con éxito.
        Retorna False si el título es vacío o si la tarea está duplicada.
        Lanza la excepción si ocurre un fallo en el Notificador o Almacenamiento,
        pero revierte los cambios en el Almacenamiento (Rollback) si el Notificador falla.
        """
        # 1. Validación de título vacío o con solo espacios
        if not title or not title.strip():
            return False

        # Cargamos las tareas actuales
        tasks = self.storage.load()

        # 2. Validación de tareas duplicadas
        if title in [t['title'] for t in tasks]:
            return False

        # Guardamos una copia del estado previo del almacenamiento para rollback
        previous_state = [dict(t) for t in tasks]

        # Agregamos la nueva tarea localmente y la guardamos en storage
        tasks.append({"title": title, "done": False})
        
        try:
            self.storage.save(tasks)
        except Exception as e:
            # Si el almacenamiento físico falla, propagamos la excepción
            raise e

        # Intentamos notificar
        try:
            self.notifier.send(f"Tarea '{title}' creada")
        except Exception as e:
            # Consistencia (Rollback): Si falla la notificación, revertimos el almacenamiento
            try:
                self.storage.save(previous_state)
            except Exception:
                # Si falla el rollback, se deja constancia sin ocultar la excepción original
                pass
            raise e

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
        """Lista todas las tareas persistidas en el almacenamiento."""
        return self.storage.load()
