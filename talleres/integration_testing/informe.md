# Informe: Taller de Pruebas de Integración

## Qué se hizo en el taller

En este taller se trabajó para entender mejor las pruebas de integración y no quedarnos solo con que los tests “pasen”, sino con revisar de verdad si los módulos se conectan bien entre sí.

Primero se revisó el proyecto base y las pruebas que ya venían hechas. Ahí se notó que eran muy simples, porque solo comprobaban si algunas funciones devolvían `True`, pero no miraban si el servicio realmente estaba usando el almacenamiento y el notificador. O sea, podían pasar aunque algo por dentro estuviera mal.

Después se hizo el sabotaje pedido en `add_task()`. La idea era probar qué pasaba si esa función devolvía `True` sin guardar nada ni avisar a nadie. Con las pruebas viejas, eso no se detectaba. Eso sirvió para ver la debilidad del enfoque inicial.

Luego se arregló esa parte en `src/service.py`. Se agregó validación para que no entren títulos vacíos, se revisó el caso de tareas repetidas y también se hizo rollback si la notificación falla, para no dejar el sistema en un estado raro.

También se mejoraron las pruebas. En `tests/test_service_integration.py` se hicieron pruebas top-down usando stubs para simular `Storage` y `Notifier`, y así revisar la lógica del servicio sin depender de cosas externas. Ahí se probaron casos como:

- tarea nueva,
- título vacío,
- tarea duplicada,
- fallo del notificador,
- fallo del almacenamiento.

Además, se hizo una parte sandwich, donde se usó el almacenamiento real pero el notificador falso. Eso ayudó a ver mejor si la persistencia sí quedaba bien guardada sin tener que mandar notificaciones reales.

En `tests/test_storage_driver.py` se trabajó el enfoque bottom-up. Ahí se probó `TaskStorage` directamente, como un driver, para revisar si podía crear el archivo, guardar una tarea, guardar varias y leer todo después.

Por último, se escribió el informe con las respuestas de las preguntas del entregable y una explicación más general de lo aprendido en el taller.

## Respuestas directas del entregable

### Parte 2 - Análisis crítico

**¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?**

No del todo. Las primeras pruebas solo miraban el resultado final y no revisaban si los módulos de verdad hablaban entre sí.

**¿Qué interacciones entre módulos no están siendo validadas?**

No se comprobaba bien si `TaskService` llamaba a `storage.load()`, `storage.save()` y `notifier.send()` como debía.

**¿Qué fallos típicos de integración podrían pasar desapercibidos?**

Podían pasar cosas como guardar mal una tarea, no notificar, dejar datos a medias o esconder errores sin que nadie se enterara.

### Parte 3 - Sabotaje controlado

**¿Las pruebas detectaron el error?**

Con las pruebas viejas no. Con las nuevas sí.

**¿Por qué seguían pasando al inicio?**

Porque estaban revisando solo el retorno de la función y no lo que pasaba por dentro.

**¿Qué debilidad fundamental tenían?**

Eran demasiado superficiales y no comprobaban la colaboración real entre módulos.

### Parte 6 - Cobertura de código vs cobertura de integración

**¿Qué diferencia hay entre cobertura de código y cobertura de integración?**

La cobertura de código mira qué líneas se ejecutan. La cobertura de integración mira si las partes del sistema trabajan bien juntas.

**¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?**

Porque una función puede ejecutarse completa y aun así fallar la comunicación entre módulos o quedar mal el estado final.

**¿Qué señales indicarían que una integración es insuficiente?**

Si nunca fallan los tests cuando se rompe una dependencia, si no revisan el estado guardado o si solo miran retornos, algo está flojo.

### Parte 7 - Reflexión final

**¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?**

Que las unitarias sirven para revisar partes pequeñas, pero no alcanzan para ver si todo el sistema se entiende bien.

**¿En qué situaciones usarías bottom-up y en cuáles top-down?**

Bottom-up lo usaría cuando quiero revisar primero lo de abajo, como el almacenamiento. Top-down lo usaría cuando quiero empezar por la lógica principal.

**¿Cómo aplicarías stubs y drivers en un proyecto con microservicios o bases externas?**

Los stubs servirían para simular servicios externos y los drivers para probar módulos antes de tener todo conectado.

## Casos trabajados

Durante el taller se revisaron estos escenarios:

- títulos vacíos,
- tareas duplicadas,
- fallo en el almacenamiento,
- fallo en la notificación,
- consistencia del sistema cuando algo falla a la mitad,
- archivo JSON vacío o que no existe.

## Lo más importante que se aprendió

Lo más importante fue entender que un test que “pasa” no siempre significa que el sistema esté bien. A veces solo significa que el test está muy débil. Por eso se cambiaron las pruebas para que revisen de verdad las interacciones y no solo el resultado final.

## Evidencia de validación

Se ejecutó:

```bash
pytest tests -v
```

Y las 12 pruebas quedaron pasando.
