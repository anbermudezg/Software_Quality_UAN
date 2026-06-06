# Informe — Taller E2E

## Parte 1 — Instalación y ejecución inicial

Instalación y arranque (resumen):

```bash
base) eleider@Macs-MacBook-Pro e2e_testing % pytest tests/ -v
============ test session starts ============
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0 -- /opt/miniconda3/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/eleider/Software_Quality_UAN/talleres/e2e_testing
plugins: mock-3.15.1, base-url-2.1.0, playwright-0.8.0, anyio-4.13.0
collected 5 items

tests/test_tareas_e2e.py::TestPaginaPrincipal::test_pagina_carga PASSED [ 20%]
tests/test_tareas_e2e.py::TestPaginaPrincipal::test_titulo_visible PASSED [ 40%]
tests/test_tareas_e2e.py::TestCrearTarea::test_formulario_presente PASSED [ 60%]
tests/test_tareas_e2e.py::TestCrearTarea::test_agregar_tarea_no_lanza_error PASSED [ 80%]
tests/test_tareas_e2e.py::TestCompletarTarea::test_completar_tarea_no_lanza_error PASSED [100%]

============= 5 passed in 2.90s =============
(base) eleider@Macs-MacBook-Pro e2e_testing %
```

### Observación inicial

Al ejecutar lo anterior las pruebas iniciales pasan correctamente.

### Pregunta

¿Las pruebas realmente están verificando comportamiento útil del sistema?

### Respuesta (tono coloquial, universitario)

No. Que los tests pasen no significa que lpruebe correctamente el flujo pueden haber falso positivos. Las pruebas actuales son mas validaciones rapidas: revisan que la página abra o que algunos elementos como selectores no lancen error, pero no comprueban que la tarea se guarde, si estan en la lista o si quedó realmente paso a un estado como completada. Hay validaciones indebidas ( `count() >= 0`) que basicamente siempre pasan, así que pueden dar falsos positivos: el test suena bien, pero no garantiza el comportamiento real.

## Parte 2 — Análisis crítico de las pruebas

━━━━━━━━━━━━━━━━━━

1. ¿Qué está pasando con las pruebas actuales?
   - Ahora mismo, los tests se quedan en la superficie: llenan el formulario y hacen clic en el botón, o simplemente validan que la página cargue. Sin embargo, no verifican si la tarea se guardó de verdad o si se muestra correctamente. Además, tenemos algunas aserciones muy débiles (como `count() >= 0`) que siempre van a pasar, lo que nos da falsos positivos que dice pasar y funcioanrcpero el app puede estar rota.

2. Acciones del usuario que estamos ignorando (Puntos Ciegos)
   - Confirmación visual y de contenido: que la tarea aparezca en la lista y que el texto coincida exactamente con lo que escribió el usuario (sin recortes ni errores).
   - Persistencia: que la tarea siga ahí si el usuario recarga la página (guardado real en backend o JSON).
   - Casos límite: qué pasa si intentan crear una tarea vacía, con títulos duplicados o con caracteres especiales.
   - Flujos complementarios: validar que al eliminar una tarea desaparezca por completo (UI y almacenamiento), y que al completarla se note el cambio visual (tachado/badge) y se actualice su estado en el repositorio.
   - Feedback: que los mensajes de error o validación realmente se le muestren al usuario cuando algo sale mal.

3. Riesgos críticos en la UI que podrían pasarse por alto
   - Tareas que se muestran en pantalla pero jamas almacena en el json
   - Botones que recargan la página por error y borran el progreso del usuario.
   - Selectores o `data-testid` mal hecho o erroneos que hagan que los tests busquen en el sitio equivocado.
   - Acciones que afecten al elemento incorrecto (por ejemplo, querer borrar la tarea 1 y que se borre la 2).
   - Problemas de estilos (ejemplo que no se vea algo, que este muy corrido elementos y sivualmente este no legible para las peronas) que impidan al usuario interactuar, aunque el backend funcione.

💡 Conclusión - Las pruebas actuales sirven como defensa muy básica, pero no aseguran la calidad ni funcionamiento adecuado del producto.

## Parte 3 — El lado oscuro de las pruebas E2E

━━━━━━━━━━━━━━━━━━

Sabotaje controlado

Se modificó `src/app.py` en la ruta `create_task` para que haga solo el `redirect` a `/` y no llame a `repo.add()`. Desde el navegador la aplicación sigue respondiendo igual, pero la tarea deja de guardarse.

### Evidencia de ejecución

```bash
pytest tests/test_tareas_e2e.py -v
```

Resultado real de la suite actual:

```bash
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.0.3, pluggy-1.5.0 -- /opt/miniconda3/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/eleider/Software_Quality_UAN/talleres/e2e_testing
plugins: mock-3.15.1, base-url-2.1.0, playwright-0.8.0, anyio-4.13.0
collected 5 items

tests/test_tareas_e2e.py::TestPaginaPrincipal::test_pagina_carga PASSED  [ 20%]
tests/test_tareas_e2e.py::TestPaginaPrincipal::test_titulo_visible PASSED  [ 40%]
tests/test_tareas_e2e.py::TestCrearTarea::test_formulario_presente PASSED  [ 60%]
tests/test_tareas_e2e.py::TestCrearTarea::test_agregar_tarea_no_lanza_error PASSED [ 80%]
tests/test_tareas_e2e.py::TestCompletarTarea::test_completar_tarea_no_lanza_error PASSED [100%]

============================== 5 passed in 2.74s ===============================
```

### Respuestas

¿Los tests detectaron el error?

No, el error pasó completamente desapercibido y la suite de pruebas no saltó en ningún momento.

¿Por qué siguen pasando?

Porque las pruebas actuales solo se fijan en que la interacción termine sin colgarse y en que el navegador reciba la redirección a `/`. Como el endpoint modificado sigue devolviendo esa respuesta HTTP válida, el test asume que todo está perfecto y da luz verde. No comprueba si la tarea se guardó de verdad, si aparece en la lista o si los datos llegaron bien al backend. Con que la página no explote, el test se da por bien servido.

¿Qué debilidad fundamental tienen estas pruebas E2E?

Básicamente, son demasiado superficiales. Se quedan en evaluar la navegación y que los botones estén ahí, pero no revisan el comportamiento real del sistema. Miden si el formulario se puede rellenar y enviar, pero no si la aplicación hace algo útil con esa información.

Esto deja al descubierto varios puntos críticos. Por ejemplo, nadie comprueba cómo queda el DOM después de mandar el formulario, ni se verifica si los datos se guardaron en el JSON o en el repositorio. Tampoco hay nada que nos asegure que el texto que sale en pantalla coincida con lo que el usuario escribió, ni se valida el ciclo completo de si la tarea quedó creada o completada.

## Parte 7 — Reflexión sobre pruebas E2E en CI/CD

1. ¿Qué son los flaky tests y por qué son tan comunes en E2E?
   - Los flaky tests son básicamente esas pruebas “inestables” que a veces pasan y a veces fallan, de la nada, sin que nadie haya tocado una sola línea de código. En E2E esto pasa muchísimo porque dependemos de muchas cosas externas a la vez: la velocidad de la red, cómo reacciona el navegador, los tiempos de carga de la interfaz o el estado del sistema en ese segundo exacto.
   - Un caso supertípico es cuando el test intenta hacer clic en un botón que todavía no se ha terminado de renderizar o asume que una sección va a cargar en un tiempo fijo. Si justo en ese momento el servidor va un poco lento o el DOM tarda un milisegundo más en reaccionar, el test se rompe por completo, aunque la aplicación en realidad funcione bien.

2. ¿Cómo garantizarías el aislamiento entre tests en una suite E2E?
   - La regla de oro aquí es que cada prueba tiene que arrancar desde cero, con un escenario limpio y sin heredar la “basura” o los datos que dejó el test anterior. En esta suite lo resolvemos usando el fixture `page`, que vacía el repositorio de tareas antes de que empiece cada test con un `POST /tasks/clear`. Así ninguna prueba contamina a las demás.
   - Además de eso, es clave trabajar con archivos de datos separados (como `data/tasks_test.json`) y no compartir cachés, sesiones o almacenamiento temporal sin haberlos reiniciado antes.
   - Al final, lo ideal es que cada test sea autosuficiente: que cree sus propios datos, haga sus propias validaciones y no dependa de que otra prueba haya creado algo previamente.

3. ¿En qué casos usarías E2E en lugar de pruebas de integración?
   - Usaría E2E cuando necesito comprobar que todo el camino funciona bien, desde que el usuario hace clic hasta que el dato llega al backend. Es la mejor opción para blindar los flujos más importantes de la app, como crear una tarea, marcarla como hecha o borrarla, porque ahí ves si todas las piezas encajan entre sí.
   - Como los tests E2E son más lentos y fáciles de romper que las pruebas de integración, no hay que abusar de ellos. Hay que reservarlos para los flujos vitales del negocio y dejar los escenarios más pequeños, específicos o lógicos a las pruebas de integración, que corren más rápido.
   - En resumen: E2E para validar la experiencia de usuario completa; integración para comprobar la lógica interna y que los componentes del backend se entienden bien.
