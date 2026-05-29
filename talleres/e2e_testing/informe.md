# Informe del Taller de Pruebas E2E

## Parte 2 - Análisis crítico de las pruebas

### Pregunta 1: ¿Las pruebas actuales verifican que las tareas se crean correctamente?

No, realmente no lo verifican. Las pruebas iniciales solo comprueban que la página cargue y que algunos elementos existan, pero no revisan si la tarea queda guardada y visible en la lista.

### Pregunta 2: ¿Qué acciones del usuario no están siendo validadas?

No se estaba validando si crear una tarea tenía un efecto real en la aplicación. Tampoco se comprobaba si completar una tarea cambiaba su estado o si eliminarla hacía que desapareciera de la lista. Además, no se revisaban casos como título vacío, tareas repetidas o lista vacía.

### Pregunta 3: ¿Qué fallos críticos de la UI podrían pasar desapercibidos?

Podrían pasar desapercibidos errores como que el formulario se viera bien pero no guardara nada, que el botón de completar no hiciera nada, que el botón de eliminar no borrara realmente la tarea o que la lista mostrara información vieja. En general, la UI podía verse “normal” aunque por dentro no estuviera funcionando bien.

## Parte 3 - El lado oscuro de las pruebas E2E

### Pregunta 1: ¿Los tests detectaron el error?

No, no lo detectaron. Después del sabotaje, las pruebas iniciales siguieron pasando aunque la tarea ya no se guardara.

### Pregunta 2: ¿Por qué siguen pasando?

Porque esas pruebas no estaban mirando el resultado real de la acción. Solo revisaban que la navegación no fallara y que algunos elementos estuvieran presentes, pero no comprobaban el cambio de estado en el sistema.

### Pregunta 3: ¿Qué debilidad fundamental tienen estas pruebas E2E?

La debilidad principal es que usan aserciones muy flojas. En vez de verificar el comportamiento que le importa al usuario, solo confirman que la aplicación “no se rompa” visualmente. Eso da una falsa sensación de seguridad.

## Parte 7 - Reflexión sobre pruebas E2E en CI/CD

### Pregunta 1: ¿Qué son los flaky tests y por qué son especialmente comunes en E2E?

Son pruebas que a veces pasan y a veces fallan sin que el código haya cambiado. Son comunes en E2E porque dependen de muchas cosas al mismo tiempo: el navegador, el backend, la red, los tiempos de carga y la sincronización de la interfaz.

### Pregunta 2: ¿Cómo garantizarías el aislamiento entre tests en una suite E2E?

Usaría datos separados para cada prueba, limpiaría el estado antes o después de cada una y evitaría que un test dependa de otro. La idea es que cada prueba empiece desde cero y no importe el orden en que se ejecuten.

### Pregunta 3: ¿En qué casos usarías E2E en lugar de pruebas de integración?

Usaría E2E cuando quiera revisar un flujo completo de principio a fin, sobre todo en funciones importantes de la aplicación. Por ejemplo, cuando un usuario crea algo, lo guarda, lo modifica o lo elimina y quiero ver todo el recorrido real.

### Pregunta 4: ¿Cómo aplicarías Playwright o Selenium en un proyecto con microservicios?

Los usaría para validar solo los flujos más importantes que atraviesan varios servicios y llegan hasta la interfaz. No los usaría para todo, porque suelen ser más lentos y más frágiles. Para la mayor parte de la cobertura, confiaría más en pruebas de integración, contrato y unitarias.