"""
Módulo de notificaciones (simula envío de correo) - CORREGIDO.
Se limpian las malas prácticas de importación interna.
"""

import random

class Notifier:
    def send(self, message):
        """
        Envía una notificación.
        En producción usaría SMTP; aquí simulamos una petición.
        Mantiene el 10% de fallo aleatorio controlado para el entorno de producción.
        """
        if random.random() < 0.1:  # 10% de fallo aleatorio simulado
            raise ConnectionError("No se pudo enviar la notificación")
        
        print(f"Notificación enviada: {message}")
        return True