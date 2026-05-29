# Informe – Taller: Pruebas E2E

---

## Resumen

En este taller se realizó un proceso completo de evaluación y mejora de pruebas E2E sobre una aplicación Flask de gestión de tareas, usando Playwright como herramienta principal. Se comenzó identificando las debilidades de las pruebas iniciales, que pasaban sin verificar ningún efecto real sobre la UI. Mediante un sabotaje controlado se demostró que suprimir la persistencia de tareas no era detectado por esas pruebas. A continuación se implementaron pruebas robustas organizadas con el patrón Page Object Model, cubriendo creación, completado, eliminación, flujo completo y casos extremos. Finalmente se reflexionó sobre los retos propios de las pruebas E2E en entornos de integración continua.

---

## Parte 2 – Análisis crítico de las pruebas iniciales

### ¿Las pruebas iniciales verifican algo útil?

No. Las pruebas originales están diseñadas para pasar siempre, independientemente del comportamiento real de la aplicación. Por ejemplo, `test_titulo_visible` verifica `count() >= 0`, condición que es siempre verdadera incluso si el elemento no existe en el DOM. Y `test_agregar_tarea_no_lanza_error` solo comprueba que no se lanza una excepción de red, sin verificar que la tarea haya sido guardada o mostrada en la lista.

### ¿Qué interacciones del usuario no estaban cubiertas?

No se validaba ninguna de las siguientes acciones:

- Que al crear una tarea su título apareciera en la lista.
- Que al completar una tarea apareciera el badge "✓ Completada" y el título quedara tachado.
- Que al eliminar una tarea desapareciera de la lista.
- Que un título vacío o duplicado fuera rechazado.
- Que la lista mostrara el mensaje "No hay tareas" cuando estuviera vacía.
- Que el orden de creación se mantuviera en la lista.

### ¿Qué fallos críticos de la UI podrían pasar desapercibidos?

Podrían pasar desapercibidos: que el formulario envíe los datos al endpoint incorrecto, que la lista no se actualice tras una operación, que el badge de completada no se renderice, que el botón de eliminar no invoque la ruta correcta, o que el mensaje de lista vacía nunca se muestre. Cualquiera de estos errores sería invisible para las pruebas originales.

---

## Parte 3 – El lado oscuro: sabotaje controlado

### ¿Las pruebas iniciales detectaron la modificación maliciosa?

No. Al modificar `create_task` en `app.py` para que devuelva el redirect sin llamar a `repo.add()`, los cinco tests originales siguieron pasando sin ningún error.

### ¿Por qué siguen pasando?

Porque ninguna prueba verifica que la tarea haya aparecido en la lista. `test_agregar_tarea_no_lanza_error` solo confirma que la petición HTTP no falló, lo que sigue siendo cierto aunque no se persista nada. El redirect funciona igual con o sin la llamada a `repo.add()`.

### Debilidad fundamental

Las pruebas confunden "ausencia de error" con "comportamiento correcto". Una prueba E2E que no verifica el estado de la UI después de una acción del usuario no está probando nada útil; simplemente confirma que el servidor no se cayó.

---

## Parte 4 – Playwright: locators y aserciones

Se implementó la clase `TestCrearTareaFuerte` con cinco pruebas que verifican efectos reales:

- Que el título aparece en la lista (`tarea_existe`).
- Que el número de ítems aumenta correctamente.
- Que una tarea nueva no tiene badge de completada.
- Que el input queda vacío tras enviar el formulario.
- Que el sabotaje de la Parte 3 es detectado (`test_deteccion_sabotaje_add_task` falla si `repo.add()` no es llamado).

Todos los locators usan `data-testid`, lo que los hace independientes de clases CSS o estructura HTML que puedan cambiar.

---

## Parte 5 – Page Object Model

Se implementó `TaskPage` en `tests/page_objects.py`. La clase centraliza:

- Todos los locators como atributos del objeto.
- Acciones (`crear_tarea`, `completar_tarea`, `eliminar_tarea`) que encapsulan la interacción con el formulario y los botones.
- Consultas (`tarea_existe`, `tarea_esta_completada`, `lista_esta_vacia`, `titulos_en_orden`) que devuelven estados de la UI sin exponer selectores a los tests.

**Ventaja principal**: si el HTML cambia (por ejemplo, se renombra un `data-testid`), solo se actualiza `TaskPage` y no cada test individualmente.

El flujo completo en `TestFlujoCompleto::test_ciclo_vida_completo` demuestra cómo el POM permite escribir tests que leen como una descripción del comportamiento del usuario, sin detalles técnicos de selectores.

---

## Parte 6 – Escenarios de error y casos extremos

Se implementaron seis pruebas en `TestCasosExtremos`:

- Título vacío rechazado (lista permanece vacía).
- Título con solo espacios rechazado.
- Tarea duplicada no se agrega (la lista mantiene exactamente un ítem).
- Mensaje de lista vacía visible al inicio (estado limpio por fixture).
- Orden de creación preservado en la lista.
- Completar una tarea no afecta el estado de las demás.

Estos casos cubren las condiciones de frontera más comunes en aplicaciones de gestión de listas.

---

## Parte 7 – Reflexión sobre pruebas E2E en CI/CD

### ¿Qué son los flaky tests y por qué son especialmente comunes en E2E?

Un flaky test es una prueba que a veces pasa y a veces falla sin que el código haya cambiado. Son especialmente comunes en E2E porque estas pruebas dependen de múltiples factores externos que no siempre son deterministas: velocidad de respuesta del servidor, tiempo de renderizado del navegador, animaciones CSS, carga del sistema operativo, o disponibilidad de red. Por ejemplo, un test que hace clic en un botón justo después de una navegación puede fallar si el botón todavía no está en el DOM en ese momento. La solución es usar `wait_for_selector` o los `expect()` de Playwright con reintentos automáticos, en lugar de `time.sleep()`.

### ¿Cómo garantizarías el aislamiento entre tests E2E?

El aislamiento se garantiza asegurando que cada test comienza con un estado conocido y limpio, sin depender del estado dejado por tests anteriores. En este taller, el fixture `page` del `conftest.py` llama al endpoint `/tasks/clear` antes de cada test, lo que garantiza que la lista de tareas esté vacía al inicio. Adicionalmente, cada test crea sus propios datos en lugar de asumir que ya existen. Otro mecanismo útil es usar bases de datos o archivos temporales dedicados para tests, como se hace aquí con `data/tasks_test.json`.

### ¿En qué casos preferirías una prueba E2E sobre una de integración?

Las pruebas E2E son preferibles cuando lo que se quiere validar es el flujo completo desde la perspectiva del usuario: que al hacer clic en "Agregar" la tarea aparece en la lista, que al completarla el badge se muestra, que la navegación entre páginas funciona. Las pruebas de integración son más adecuadas para validar la lógica interna entre módulos (que `Service` llama a `Storage` con los parámetros correctos) sin necesidad de un navegador. En general, se usan pocas E2E (los flujos más críticos del usuario) y muchas pruebas de integración y unitarias, siguiendo la pirámide de testing.

### ¿Cómo aplicarías Playwright o Selenium en un proyecto con microservicios?

En un proyecto con microservicios, las pruebas E2E con Playwright o Selenium se ejecutarían contra el frontend desplegado en un entorno de staging que tenga todos los servicios corriendo. Para pruebas más rápidas y estables, los microservicios externos (autenticación, pagos, notificaciones) se pueden reemplazar por mocks o stubs de red (usando herramientas como WireMock o el `route()` de Playwright para interceptar peticiones HTTP). Esto permite probar el frontend de forma aislada sin depender de la disponibilidad de todos los backends. Las pruebas E2E verdaderas (contra el sistema completo) se reservan para el pipeline de integración continua previo a producción.

---

## Diagrama de arquitectura del sistema bajo prueba

```
┌─────────────────────────────────────────────────────────────┐
│                     Playwright (tests)                      │
│  TaskPage (POM) → page.click / fill / expect / locator      │
└────────────────────────────┬────────────────────────────────┘
                             │  HTTP (navegador headless)
┌────────────────────────────▼────────────────────────────────┐
│                    Flask App (src/app.py)                    │
│  GET /   POST /tasks   POST /tasks/<id>/complete|delete      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  TaskRepository (models.py)                  │
│              Persistencia en data/tasks_test.json            │
└─────────────────────────────────────────────────────────────┘

Estrategia de aislamiento:
──────────────────────────────────────────────────────────────
fixture page  │ POST /tasks/clear antes de cada test
archivo JSON  │ data/tasks_test.json exclusivo para tests
POM           │ TaskPage encapsula todos los locators
──────────────────────────────────────────────────────────────
```

