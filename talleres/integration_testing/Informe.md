# Informe 
## Parte 2
1. ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?
    - Rta: Si
```javascript
(base) eleider@Macs-MacBook-Pro integration_testing % pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0 -- /opt/miniconda3/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/eleider/Software_Quality_UAN/talleres/integration_testing
plugins: mock-3.15.1
collected 3 items                                                              

tests/test_service_integration.py::TestServiceIntegration::test_add_task_happy_path PASSED [ 33%]
tests/test_service_integration.py::TestServiceIntegration::test_complete_task PASSED [ 66%]
tests/test_storage_driver.py::test_storage_save_and_load PASSED          [100%]

============================== 3 passed in 0.05s ===============================
(base) eleider@Macs-MacBook-Pro integration_testing %
```

2. ¿Qué interacciones entre módulos no están siendo validadas? 
    - Rta: No, (No se usa  list_tasks)
3. ¿Qué fallos típicos de integración (errores de comunicación, excepciones no controladas, estados inconsistentes) podrían pasar desapercibidos?
    - Rta: Race condition(Error de carrera) Es cuando 2 sistemas pelean por un dato y este se vuelve inconsistente.
     Error de dependencia, codificar para crear y obtener in formación pero en módulos separados podría introducir un error en el que no apunte a las rutas correctas. 

## Parte 3
1. ¿Las pruebas detectaron el error? 
    - Rta: No
2. ¿Por qué siguen pasando?
    - Rta: El código esta defectuoso, es un falso positivo devolver direcctamente True sin procesar nada.
3. ¿Qué debilidad fundamental tienen estas pruebas de integración?
    - Rta: No validan completamente el funcionamiento interno de cada función.

## Parte 4
1. ¿Cuál es la diferencia entre cobertura de código y cobertura de integración?
    - Rta: Cobertura de código es qué líneas se ejecutaron, cobertura de integración es si se probó cómo interactúan los módulos.
2. ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione?
    - Rta: Porque las pruebas unitarias usan componentes aislados y no revisan los efectos reales ni las dependencias juntas.
3. ¿Qué señales indican que unas pruebas de integración son insuficientes?
    - Rta: Que solo hay happy path, no se prueban fallos y no se comprueba el estado real en disco o en servicios.

## Parte 6
1. ¿Qué pruebas hiciste para detectar la versión rota de la Parte 3?
    - Rta: Escribí pruebas tipo top-down y sandwich que verifican guardar en disco y notificar, más tests de error que simulan fallo del storage y del notifier.
2. ¿Por qué es importante que esas pruebas fallen con la versión rota y pasen con la corregida?
    - Rta: Porque así no es solo un falso positivo: se comprueba la integración real y se demuestra que el bug se arregla de verdad.
3. ¿Qué casos extremos cubre tu suite?
    - Rta: título vacío, duplicados, archivo vacío o inexistente, fallo simulado de storage, fallo simulado de notifier con rollback.

## Parte 7
1. ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
    - Rta: Que las unitarias solo prueban cada pieza aislada, pero no aseguran que el sistema entero funcione cuando los módulos se juntan.
2. ¿En qué situaciones reales usarías un enfoque bottom-up y en cuáles top-down?
    - Rta: Bottom-up cuando quiero validar que los módulos de bajo nivel (storage, DB) funcionan bien por sí solos. Top-down cuando necesito probar la parte principal de la app usando stubs para dependencias externas.
3. ¿Cómo aplicarías stubs y drivers en un proyecto con microservicios o con bases de datos externas?
    - Rta: Usaría stubs para simular servicios externos y no depender de red en los tests, y drivers para probar cada servicio o storage real sin pasar por toda la aplicación.

## Criterios del entregable
1. Detección de errores reales:
    - Rta: las pruebas top-down y sandwich están hechas para fallar si la versión está rota (Parte 3) y pasar con la versión corregida.
2. Uso correcto de stubs y drivers:
    - Rta: top-down usa stubs de Storage/Notifier, bottom-up usa el driver directo de TaskStorage, sandwich usa storage real + notifier stub.
3. Cobertura de error y casos extremos:
    - Rta: cubro título vacío, duplicado, archivo vacío/inexistente, fallo simulado en storage y fallo simulado en notifier con rollback.
4. Calidad del análisis escrito:
    - Rta: respuestas cortas, con el mismo estilo informal y explicando por qué.
5. Organización:
    - Rta: rama debe ser `edwin_amaya`, commits claros, no subir archivos temporales ni tests ocultos.
## Evidencia de pruebas y versión
- Tests ejecutados: `pytest -q tests/test_service_integration.py tests/test_storage_driver.py`
- Resultado: `15 passed in 0.06s`
- Rama final: `full_edwin_eleider_amaya_roa`
- Rama experimental: `edwin_experiment_roto`
- Último commit en la rama final: `7d5b4d5` con mensaje `docs: añadir evidencia de tests rotos y notas de rama`
- Archivos de evidencia: `evidence/fixed_tests.txt`, `evidence/broken_tests.txt`, `evidence/branch_notes.txt`
- Archivos temporales eliminados: `test_driver.json`, `test_tasks.json`

## Proceso cronológico y evidencia
1. Crear rama rota: `edwin_experiment_roto` con `src/service.py` saboteado para que `add_task()` devuelva True sin guardar ni notificar.
2. Ejecutar tests en la rama rota y guardar salida en `evidence/broken_tests.txt`.
3. Crear rama final limpia: `full_edwin_eleider_amaya_roa` desde la versión corregida.
4. Ejecutar tests en la rama final y guardar salida en `evidence/fixed_tests.txt`.
5. Añadir `evidence/branch_notes.txt` con los SHAs y nombres de ramas para dejar claro el flujo.

## Notas de entrega final
- Rama: `edwin_amaya`.
- Commits: mensajes simples pero claros, como “arreglé tests top-down y agregué casos extremos”.
- No subir `test_driver.json` ni `test_tasks.json` porque son archivos temporales.
- PR: en la descripción poner nombre completo y código de identificación.
