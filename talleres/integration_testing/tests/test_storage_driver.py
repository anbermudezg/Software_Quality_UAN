# aqui van las pruebas tipo driver, sin usar Service
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage import TaskStorage


def test_storge_crea_archivo_falta(tmp_path):
    filep = tmp_path / 'missing_storage.json'
    assert not filep.exists()

    storage = TaskStorage(str(filep))

    assert filep.exists()
    assert storage.load() == []


def test_storage_save_and_load_one_task(tmp_path):
    filep = tmp_path / 'single_task.json'
    storage = TaskStorage(str(filep))

    tarea = {'title': 'Tarea única', 'done': False}
    storage.save([tarea])

    data = storage.load()
    assert data == [tarea]


def test_storage_save_and_load_multiple_taskss(tmp_path):
    filep = tmp_path / 'multiple_tasks.json'
    storage = TaskStorage(str(filep))

    tasks = [
        {'title': 'Tarea 1', 'done': False},
        {'title': 'Tarea 2', 'done': True},
    ]
    storage.save(tasks)

    data = storage.load()
    assert data == tasks


def test_storage_acepta_titulo_vacio(tmp_path):
    # politica: el storage solo guarda lo que le pase aun si esta vacio el titulo
    filep = tmp_path / 'empty_title.json'
    storage = TaskStorage(str(filep))

    tarea = {'title': '', 'done': False}
    storage.save([tarea])

    data = storage.load()
    assert data == [tarea]


def test_storage_loads_empty_file_as_empty_list(tmp_path):
    filep = tmp_path / 'empty_storage.json'
    filep.write_text('[]')

    storage = TaskStorage(str(filep))
    assert storage.load() == []
