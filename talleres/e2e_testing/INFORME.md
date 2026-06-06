# Informe del Taller de Pruebas E2E

## Parte 2 — Análisis

¿Las pruebas iniciales verifican algo útil? ¿Por qué?
Las pruebas iniciales son intencionalmente débiles. Verifican solo que la página responde (código HTTP 200) y que ciertos elementos existen en el DOM, pero no validan el comportamiento correcto de la aplicación. Por ejemplo, verifican que el formulario existe pero no que al enviar una tarea ésta se agregue a la lista. Por lo tanto, no verifican nada útil desde la perspectiva del usuario.

¿Qué interacciones de usuario no estaban cubiertas?
Las pruebas iniciales no cubrían:
- Verificar que al crear una tarea, ésta aparezca en la lista.
- Verificar que al completar una tarea, se muestre el badge de completada y el título se tache.
- Verificar que al eliminar una tarea, ésta desaparezca de la lista.
- Verificar que el input se limpie después de agregar una tarea.
- Verificar casos extremos como título vacío, tareas duplicadas, lista vacía, etc.

## Parte 3 — Sabotaje

¿Las pruebas iniciales detectaron la modificación maliciosa?
No. Incluso después de modificar la ruta `create_task` para que no guarde la tarea (simplemente redirige sin llamar a `repo.add()`), las pruebas iniciales siguen pasando.

¿Qué debilidad fundamental expone este experimento?
Las pruebas iniciales no verifican el estado de la interfaz de usuario después de una acción; solo verifican que no haya errores de red o que ciertos elementos existan. Esto las hace incapaces de detectar fallos lógicos donde la acción se ejecuta pero no produce el cambio esperado en el estado del sistema.

## Parte 7 — Reflexión E2E

Explica con tus palabras qué es un flaky test y da un ejemplo concreto.
Un flaky test es aquel que pasa o falla de manera no determinística sin cambios en el código. Un ejemplo común en pruebas E2E es un test que depende de tiempos de carga: si se usa `time.sleep()` fijo y la aplicación es más lenta en某些 ejecuciones, el test puede fallar porque el elemento aún no apareció. Otro ejemplo es una carrera entre la acción del usuario y la actualización del estado, donde a veces el test verifica antes de que la actualización se complete.

¿Cómo garantizarías el aislamiento entre tests E2E?
Antes de cada test, limpiar el estado del sistema (por ejemplo, borrando todas las tareas mediante un endpoint dedicado como `/tasks/clear`). En este proyecto, el fixture `page` en `conftest.py` hace una petición POST a `/tasks/clear` antes de cada test, asegurando que cada test comience con una lista de tareas vacía.

¿Cuándo preferirías una prueba de integración sobre una E2E?
Preferiría una prueba de integración cuando quiera verificar la interacción entre componentes internos (por ejemplo, entre el controlador y el modelo) sin necesidad de abrir un navegador. Las pruebas E2E son más lentas y frágiles, así que para lógica que no depende de la UI, las pruebas de integración son más rápidas y confiables.

¿Cómo aplicarías Playwright o Selenium en un proyecto con microservicios?
En un proyecto con microservicios, las pruebas E2E deben tratar al sistema como una caja negra, interactuando únicamente mediante las interfaces expuestas (APIs REST, UI web, etc.). Cada microservicio tendría su propio conjunto de pruebas de contrato o de integración. Las pruebas E2E se enfocarían en flujos de usuario que atraviesan múltiples microservicios (por ejemplo, crear una usuario en el servicio de autenticación, luego crear una orden en el servicio de pedidos). Se utilizarían herramientas como Docker Compose o Kubernetes para levantar todo el entorno de pruebas antes de ejecutar los escenarios E2E.