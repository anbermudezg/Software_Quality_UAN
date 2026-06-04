"""
Módulo de almacenamiento en archivo JSON - CORREGIDO.
Aplica programación defensiva para evitar caídas por archivos corruptos o inexistentes.
"""

import json
import os

class TaskStorage:
    def __init__(self, filepath):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Garantiza de forma segura que el archivo exista con un JSON válido."""
        try:
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f)
        except IOError:
            # Si hay un problema de permisos en el sistema operativo
            pass

    def load(self):
        """Carga la lista de tareas. Retorna una lista vacía si falla o está corrupto."""
        if not os.path.exists(self.filepath):
            return []
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # G4: Si el archivo está vacío o corrupto, evita que la app colapse
            return []

    def save(self, tasks):
        """Guarda la lista de tareas de forma segura."""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            # Maneja fallos de disco lleno o falta de permisos de escritura
            return False