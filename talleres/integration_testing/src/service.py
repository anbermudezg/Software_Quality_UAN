class TaskService:
    def __init__(self, storage, notifier):
        self.storage = storage
        self.notifier = notifier

    def add_task(self, title):
        # 1. Limpiar espacios extras y rechazar si queda vacío
        clean_title = title.strip()
        if not clean_title:
            return False

        tasks = self.storage.load()

        # 2. Controlar duplicados sin importar mayúsculas/minúsculas
        for task in tasks:
            if task["title"].lower() == clean_title.lower():
                return False

        tasks.append({"title": clean_title, "done": False})
        self.storage.save(tasks)
        
        try:
            self.notifier.send(f"Tarea '{clean_title}' creada")
        except Exception:
            pass
            
        return True

    def complete_task(self, title):
        tasks = self.storage.load()
        for task in tasks:
            if task["title"].strip().lower() == title.strip().lower():
                task["done"] = True
                self.storage.save(tasks)
                return True
        return False
