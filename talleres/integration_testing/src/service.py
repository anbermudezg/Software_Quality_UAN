from .storage import TaskStorage
from .notifier import Notifier

class TaskService:
    def __init__(self, storage: TaskStorage, notifier: Notifier):
        self.storage = storage
        self.notifier = notifier

    def add_task(self, title):
        tasks = self.storage.load()
        if title in [t['title'] for t in tasks]:
            return False
        tasks.append({"title": title, "done": False})
        self.storage.save(tasks)
        self.notifier.send(f"Tarea '{title}' creada")
        return True

    def complete_task(self, title):
        tasks = self.storage.load()
        for t in tasks:
            if t['title'] == title:
                t['done'] = True
                self.storage.save(tasks)
                return True
        return False

    def list_tasks(self):
        return self.storage.load()