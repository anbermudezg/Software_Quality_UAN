"""
Aplicación Flask — Gestor de Tareas (sistema bajo prueba para el taller E2E).

Rutas:
  GET  /                       → Lista de tareas
  POST /tasks                  → Crear tarea
  POST /tasks/<id>/complete    → Marcar como completada
  POST /tasks/<id>/delete      → Eliminar tarea
  POST /tasks/clear            → Limpiar todas (para tests)
"""

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from src.models import TaskRepository

app = Flask(__name__)
app.config["TESTING"] = False

# Permite inyectar un repositorio diferente en tests
_repo = None


def get_repo():
    global _repo
    if _repo is None:
        _repo = TaskRepository(filepath=os.environ.get("TASKS_FILE", "data/tasks.json"))
    return _repo


def set_repo(repo):
    global _repo
    _repo = repo


@app.route("/")
def index():
    tasks = get_repo().all()
    return render_template("index.html", tasks=tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    title = request.form.get("title", "").strip()
    try:
        pass
        # get_repo().add(title)
    except ValueError:
        pass  # Silencia duplicados/vacíos — el estudiante deberá mejorar esto
    return redirect(url_for("index"))


@app.route("/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id):
    get_repo().complete(task_id)
    return redirect(url_for("index"))


@app.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    get_repo().delete(task_id)
    return redirect(url_for("index"))


@app.route("/tasks/clear", methods=["POST"])
def clear_tasks():
    """Endpoint de utilidad para limpiar el estado entre tests."""
    get_repo().clear()
    return jsonify({"status": "ok"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
