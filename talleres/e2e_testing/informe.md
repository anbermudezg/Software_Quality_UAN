# Informe — Taller: Pruebas E2E

---

## Parte 2 — Análisis crítico de las pruebas iniciales

### ¿Las pruebas iniciales verifican algo útil?

No de forma significativa. Las pruebas originales tienen dos problemas estructurales:

**Aserciones trivialmente verdaderas.** `assert title.count() >= 0` siempre es `True` porque `count()` nunca puede ser negativo, incluso si el elemento no existe. `assert page.url is not None` pasa mientras el navegador esté abierto, independientemente de lo que muestre la página.

**Sin verificación de estado.** `test_agregar_tarea_no_lanza_error` llena el formulario y hace clic, pero nunca comprueba que la tarea haya aparecido en la lista. El test pasa aunque el sistema descarte la tarea silenciosamente.

### ¿Qué interacciones de usuario no estaban cubiertas?

| Acción | Estado en pruebas originales |
|---|---|
| Verificar que la tarea creada aparece en la lista | No cubierto |
| Verificar el badge "✓ Completada" | No cubierto |
| Verificar que la tarea desaparece al eliminarla | No cubierto |
| Flujo completo crear → completar → eliminar | No cubierto |
| Título vacío | No cubierto |
| Título duplicado | No cubierto |
| Mensaje de lista vacía | No cubierto |
| Orden de inserción | No cubierto |

### ¿Qué fallos críticos de la UI podrían pasar desapercibidos?

- Un bug que impida guardar tareas en el servidor pasa completamente desapercibido.
- Un fallo en el CSS que oculte toda la lista no sería detectado.
- Un error en la ruta `complete` que no cambie el estado tampoco sería detectado.
- Una regresión que rompa el botón Eliminar no fallaría ningún test original.

---

## Parte 3 — El lado oscuro: sabotaje controlado

Se modificó `create_task` en `app.py` para hacer `return redirect(url_for("index"))` sin llamar a `get_repo().add(title)`.

### ¿Las pruebas iniciales detectaron el error?

No. Las 5 pruebas originales siguieron pasando porque ninguna verificaba que la tarea existiera en la lista después de crearla.

### ¿Qué debilidad fundamental expone este experimento?

Las pruebas originales verifican **interacción superficial** (el formulario existe, no hay error de red) pero no **efectos observables** (la tarea aparece en la UI, el estado del servidor cambió). Una prueba E2E que no afirma sobre el estado final de la interfaz es equivalente a no probarla.

Con las pruebas nuevas (`TestCrearTareaFuerte` y demás), el sabotaje produce **15 fallos inmediatos**, incluyendo `test_tarea_aparece_en_lista_tras_crearla` que es el caso más directo.

---

## Parte 7 — Reflexión sobre pruebas E2E en CI/CD

### ¿Qué es un flaky test y por qué son comunes en E2E?

Un **flaky test** es un test que a veces pasa y a veces falla sin que el código haya cambiado. Son especialmente comunes en E2E porque:

- Dependen de tiempos de carga de la red y del navegador, que varían entre ejecuciones.
- Las animaciones CSS pueden hacer que un elemento no sea interactuable en el momento exacto en que el test intenta hacer clic.
- El estado compartido entre tests puede generar condiciones de carrera.

**Ejemplo concreto:** si se usa `time.sleep(1)` para esperar a que cargue la página, en un servidor lento tardará más de 1 segundo y el test fallará; en uno rápido pasará. En este taller se usa `wait_for_load_state("networkidle")` para esperar de forma determinista a que la red esté inactiva, eliminando esta fuente de flakiness.

### ¿Cómo garantizarías el aislamiento entre tests E2E?

El `conftest.py` del taller implementa la estrategia correcta: antes de cada test, el fixture `page` llama a `POST /tasks/clear`, que vacía el archivo JSON de tareas. Esto garantiza que cada test parte de un estado limpio sin depender del orden de ejecución.

Para proyectos más grandes se puede complementar con:
- Bases de datos de prueba separadas por test (transacciones con rollback).
- Contenedores Docker que se recrean por suite.
- Identificadores únicos por test para evitar colisiones de datos.

### ¿Cuándo preferirías una prueba de integración sobre una E2E?

Las pruebas E2E son lentas (este taller tarda ~40 segundos para 25 tests). Se prefieren pruebas de integración cuando:

- Se quiere verificar la lógica de negocio o la persistencia sin necesidad del navegador.
- Se prueban rutas de error que son difíciles de reproducir desde la UI (fallos de disco, timeouts de red).
- Se necesita feedback rápido en CI/CD (las pruebas de integración corren en milisegundos).

Las pruebas E2E se reservan para los flujos críticos de usuario que validan el sistema completo: crear una tarea, completarla y eliminarla es un flujo que ninguna prueba unitaria ni de integración puede validar de extremo a extremo.

### ¿Cómo aplicarías Playwright en un proyecto con microservicios?

En un sistema de microservicios, Playwright actuaría sobre la interfaz de usuario del frontend, que a su vez consume varios servicios backend. La estrategia recomendada es:

- **Stubs de servicios externos** (MSW, WireMock) para simular respuestas de microservicios en los tests E2E, evitando dependencias de red reales.
- **Entorno de staging** con todos los servicios reales corriendo, donde se ejecuta un subconjunto pequeño de E2E (smoke tests) en cada deploy.
- **Contract testing** (Pact) para verificar los contratos entre microservicios a nivel de integración, reservando E2E solo para los flujos de negocio más críticos.

---

## Diagrama de arquitectura y cobertura de tests

```
┌─────────────────── Navegador (Playwright) ───────────────────┐
│                                                              │
│  TaskPage (Page Object)                                      │
│    crear_tarea()  completar_tarea()  eliminar_tarea()        │
│    titulo_visible()  tarea_esta_completada()  ...            │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │  HTTP (data-testid locators)
┌──────────────────────────▼───────────────────────────────────┐
│                   Flask App (src/app.py)                     │
│   GET /          POST /tasks      POST /tasks/<id>/complete  │
│                  POST /tasks/<id>/delete  POST /tasks/clear  │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│              TaskRepository (src/models.py)                  │
│   all()  add()  complete()  delete()  clear()                │
│                    data/tasks_test.json                      │
└──────────────────────────────────────────────────────────────┘

Cobertura por clase de test:
  TestCrearTareaFuerte    → POST /tasks + GET / (lista)
  TestCompletarTareaFuerte→ POST /tasks/<id>/complete + badge UI
  TestEliminarTareaFuerte → POST /tasks/<id>/delete + ausencia UI
  TestFlujoCompleto       → Flujo completo de extremo a extremo
  TestCasosExtremos       → Validaciones de negocio en la UI
```

---

## Resultado de ejecución de tests

```
Con código correcto:
  25 passed — 0 failed ✅

Con sabotaje en create_task (return True sin llamar a repo.add):
  15 failed — las pruebas fuertes detectan el error inmediatamente ✅
  10 passed — las pruebas débiles originales no detectan nada (comportamiento esperado)
```
