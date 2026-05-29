"""
Módulo de almacenamiento en archivo JSON.
Contiene mejoras de robustez para evitar errores al cargar archivos vacíos o inexistentes.
"""

import json
import os

class TaskStorage:
    def __init__(self, filepath):
        self.filepath = filepath
        if not os.path.exists(filepath) or (os.path.exists(filepath) and os.path.getsize(filepath) == 0):
            with open(filepath, 'w') as f:
                json.dump([], f)

    def load(self):
        """Carga la lista de tareas. Retorna lista vacía si el archivo no existe o está vacío."""
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            return []
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save(self, tasks):
        """Guarda la lista de tareas en el archivo."""
        with open(self.filepath, 'w') as f:
            json.dump(tasks, f, indent=2)
