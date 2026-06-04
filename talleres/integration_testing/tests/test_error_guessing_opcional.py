import sys
import os
import pytest

# Asegurar la ruta hacia 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service import TaskService
from src.storage import TaskStorage

class NotifierMock:
    def send(self, message):
        pass

class TestErrorGuessingOpcional:
    
    def test_guessing_spaces_only_title(self):
        storage = TaskStorage("test_guessing.json")
        service = TaskService(storage, NotifierMock())
        result = service.add_task("   ")
        if os.path.exists("test_guessing.json"):
            os.remove("test_guessing.json")
        assert result is False

    def test_guessing_html_injection(self):
        storage = TaskStorage("test_guessing.json")
        service = TaskService(storage, NotifierMock())
        result = service.add_task("<script>alert('XSS')</script>")
        if os.path.exists("test_guessing.json"):
            os.remove("test_guessing.json")
        assert result is True

    def test_guessing_case_insensitivity(self):
        storage = TaskStorage("test_guessing.json")
        service = TaskService(storage, NotifierMock())
        service.add_task("Estudiar Calidad")
        result_duplicate = service.add_task("ESTUDIAR CALIDAD")
        if os.path.exists("test_guessing.json"):
            os.remove("test_guessing.json")
        assert result_duplicate is False