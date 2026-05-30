"""
Módulo de notificaciones (simula envío de correo).
En pruebas se simulan fallos mediante stubs.
"""


class Notifier:
    def send(self, message):
        """Envía una notificación (simulada)."""
        print(f"Notificación enviada: {message}")
