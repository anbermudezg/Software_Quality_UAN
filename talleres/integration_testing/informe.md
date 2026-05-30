# Informe – Taller: Pruebas de Integración

---

## Parte 2 – Análisis crítico de las pruebas existentes

### ¿Las pruebas actuales verifican que los módulos colaboran correctamente?

No. Las pruebas originales (`TestServiceIntegration`) crean instancias reales de `TaskStorage` y `Notifier`, invocan métodos y verifican únicamente el valor de retorno (`True`/`False`). No comprueban en ningún momento que:

- `storage.save` haya sido llamado.
- `notifier.send` haya sido invocado.
- El contenido persistido sea el correcto.
- La tarea exista realmente en el archivo tras la operación.

### ¿Qué interacciones entre módulos no están siendo validadas?

| Interacción | Estado en pruebas originales |
|---|---|
| `Service` → `Storage.load` | No verificada |
| `Service` → `Storage.save` con datos correctos | No verificada |
| `Service` → `Notifier.send` con mensaje correcto | No verificada |
| Comportamiento ante `Storage` que falla | No cubierto |
| Comportamiento ante `Notifier` que falla | No cubierto |
| Título vacío | No cubierto |
| Duplicados | No cubierto |

### ¿Qué fallos típicos de integración podrían pasar desapercibidos?

- **Falsos positivos por valor de retorno:** un método que retorne `True` sin hacer nada pasa todos los tests originales.
- **Estado inconsistente:** si `storage.save` no es llamado, la tarea se pierde al reiniciar, pero el test dice "pasó".
- **Errores silenciados:** si `notifier.send` lanza una excepción no capturada, el sistema falla en producción aunque los tests estén en verde.
- **Dependencias no controladas:** `Notifier` tiene un fallo aleatorio del 10% — los tests originales pueden pasar o fallar de forma no determinista.

---

## Parte 3 – El lado oscuro: sabotaje controlado

Se modificó `add_task` en `service.py` para que devolviera simplemente `return True` sin llamar a `storage` ni a `notifier`.

### ¿Las pruebas originales detectaron el error?

No. Ambos tests originales (`test_add_task_happy_path`, `test_complete_task`) siguieron pasando porque solo verificaban el valor de retorno booleano.

### ¿Por qué siguen pasando?

Porque las afirmaciones (`assert result is True`) solo evalúan lo que el método devuelve, no lo que hace internamente. Un método que miente sobre su trabajo es indistinguible de uno correcto si solo se mide su salida superficial.

### ¿Qué debilidad fundamental tienen?

Las pruebas originales no verifican **efectos observables** ni **colaboración real entre módulos**. Son funcionalmente equivalentes a pruebas unitarias con mocks sin assertions sobre las llamadas. No prueban integración, prueban la interfaz de salida.

Con las pruebas nuevas (`TestTopDown`), el sabotaje produce **14 fallos inmediatos**, incluyendo:
- `test_add_task_llama_a_storage_save` → falla porque `save_count == 0`
- `test_add_task_llama_a_notifier_send` → falla porque `len(messages) == 0`
- `test_add_task_parametros_correctos_en_storage` → falla porque `last_saved` es `None`
- Todos los tests `Sandwich` → fallan porque la tarea no aparece en el archivo real

---

## Parte 4 – Enfoques aplicados

### 4.1 Top-Down (`TestTopDown` en `test_service_integration.py`)

Se crearon dos stubs:

- **`StubStorage`**: implementa `load` y `save` en memoria, con contadores `load_count`, `save_count` y atributo `last_saved` para inspeccionar las llamadas.
- **`StubNotifier`**: registra todos los mensajes recibidos en una lista `messages`.

Las pruebas verifican que `Service`:
1. Llama a `storage.save` exactamente una vez.
2. Llama a `notifier.send` exactamente una vez.
3. Pasa el contenido correcto al guardar.
4. Incluye el título en el mensaje de notificación.
5. No llama a `save` ni a `send` en caso de duplicado.

**Justificación del enfoque:** al aislar `Service` con stubs, se prueba la lógica de negocio sin depender de archivos en disco ni de la red. Si los stubs no reciben las llamadas esperadas, el test falla aunque el valor de retorno sea correcto.

### 4.2 Bottom-Up (`test_storage_driver.py`)

Se escribió un driver directo: cada test crea un `TaskStorage` apuntando a un archivo temporal (`tmp_path` de pytest) y lo ejercita sin pasar por `Service`.

Pruebas implementadas (8 en total, mínimo exigido: 4):

1. El archivo se crea vacío si no existe.
2. Se guarda y recupera una tarea.
3. Se guardan y recuperan múltiples tareas.
4. Título vacío: `Storage` lo acepta (política de negocio, no de persistencia).
5. `save` sobrescribe el contenido anterior.
6. Guardar lista vacía limpia el archivo.
7. El campo `done` se preserva correctamente.
8. `save` falla si la ruta no existe (prueba de fallo de infraestructura).

**Justificación:** `Storage` es una dependencia de bajo nivel. Probarlo de forma aislada garantiza que sus operaciones de I/O son correctas antes de confiar en ellas desde `Service`.

### 4.3 Sandwich (`TestSandwich` en `test_service_integration.py`)

Se combina `Storage` real (escribe en disco usando `tmp_path`) con un `StubNotifier` que no envía correos.

Pruebas implementadas (5):
1. La tarea persiste en disco después de `add_task`.
2. El notifier recibe el mensaje correcto.
3. `complete_task` actualiza el campo `done` en disco.
4. Dos tareas distintas ambas persisten.
5. Un duplicado no genera una segunda entrada en disco.

**Justificación:** valida la integración real entre `Service` y `Storage` sin riesgo de enviar notificaciones a producción. El stub de `Notifier` evita dependencias de red, pero el comportamiento de persistencia se comprueba con el módulo real.

---

## Parte 5 – Mejoras de cobertura

### Detección del sabotaje

Los tests `test_add_task_llama_a_storage_save` y `test_add_task_llama_a_notifier_send` detectan directamente la modificación maliciosa: comprueban contadores de llamadas, no valores de retorno.

### Escenarios de error cubiertos

| Escenario | Test | Comportamiento esperado |
|---|---|---|
| `storage.save` lanza `IOError` | `test_fallo_en_storage_propaga_excepcion` | La excepción se propaga al llamador |
| `notifier.send` lanza `ConnectionError` | `test_fallo_en_notifier_propaga_excepcion` | La excepción se propaga (no es silenciada) |
| Fallo del notifier tras guardar | `test_consistencia_tras_fallo_en_notifier` | La tarea queda en storage (sin rollback) |

### Casos extremos

| Caso | Test | Decisión |
|---|---|---|
| Título vacío | `test_add_task_titulo_vacio_no_debe_persistirse` | **Documenta bug:** el sistema actual lo acepta; debería rechazarlo |
| Duplicados | `test_add_task_retorna_false_en_duplicado` + `test_duplicado_no_persiste_segunda_vez` | Rechazado correctamente |
| Archivo vacío / no existe | `test_archivo_no_existente_se_crea_vacio` | Se crea con lista vacía |

---

## Parte 6 – Reflexión sobre cobertura

### Cobertura de código vs. cobertura de integración

**Cobertura de código** mide qué porcentaje de líneas, ramas o instrucciones son ejecutadas durante los tests. Una línea "cubierta" solo significa que fue ejecutada, no que su interacción con otros módulos fue validada.

**Cobertura de integración** mide cuántos de los contratos entre módulos han sido verificados: ¿`Service` le pasa los datos correctos a `Storage`? ¿`Storage` persiste lo que recibe? ¿`Notifier` recibe el mensaje esperado?

**Ejemplo observado en el taller:** con el sabotaje (`return True`), la cobertura de código del método `add_task` es del 100% (se ejecuta la única línea). Sin embargo, la cobertura de integración es del 0%: ningún módulo externo fue invocado. Los tests originales pasaban con cobertura de código perfecta y cobertura de integración nula.

### ¿Por qué el 100% de cobertura unitaria no garantiza que el sistema funcione?

Las pruebas unitarias aíslan cada módulo con mocks. Si `Service` tiene un mock de `Storage`, puede verificar que llama a `storage.save(...)`, pero no que `TaskStorage.save` realmente persiste esos datos en disco correctamente. El contrato entre módulos queda sin probar.

### Señales de pruebas de integración insuficientes

- Los tests pasan aunque se rompa la comunicación entre módulos (como se demostró con el sabotaje).
- Los tests son no deterministas (fallan ocasionalmente por dependencias reales como red o disco).
- No existe ningún test que falle cuando se elimina una llamada a una dependencia.
- Los tests no cubren rutas de error de los módulos dependientes.

---

## Parte 7 – Reflexión final

### Limitaciones de las pruebas unitarias frente a las de integración

Las pruebas unitarias son rápidas, deterministas y aíslan fallos con precisión. Sin embargo, no detectan:
- Contratos rotos entre módulos (formato de datos incorrecto).
- Fallos de inicialización o configuración de dependencias reales.
- Comportamientos que emergen de la interacción entre módulos correctos individualmente.

Las pruebas de integración completan ese espacio: comprueban que los módulos, cuando se conectan, se comportan como se espera del sistema completo.

### ¿Cuándo usar bottom-up y cuándo top-down?

**Bottom-Up** es preferible cuando:
- Los módulos de bajo nivel (persistencia, infraestructura) son complejos o críticos.
- Se quiere garantizar que la base funciona antes de probar capas superiores.
- El equipo trabaja en módulos independientes que se ensamblan al final.

**Top-Down** es preferible cuando:
- La lógica de negocio (capa alta) es la parte más importante a validar.
- Los módulos de bajo nivel aún no están implementados (se usan stubs).
- Se quiere proteger la lógica de orquestación contra cambios en las dependencias.

En este proyecto, el **enfoque Sandwich** resultó el más completo: prueba `Service` con `Storage` real (valida la integración de persistencia) y un stub de `Notifier` (evita dependencias de red), combinando las ventajas de ambos enfoques.

### Stubs y drivers en microservicios o bases de datos externas

- **Stubs** reemplazan servicios externos (APIs REST, colas de mensajes, servicios de correo) con implementaciones en memoria que registran las llamadas. Permiten probar la lógica de integración sin depender de la disponibilidad o el estado de sistemas externos.
- **Drivers** ejercitan directamente repositorios o adaptadores de base de datos contra una instancia real de prueba (base de datos en contenedor, SQLite en memoria), verificando que las operaciones CRUD funcionan correctamente antes de integrarlas con la lógica de negocio.

En arquitecturas de microservicios, los stubs de servicios adyacentes son esenciales para mantener los tests rápidos y deterministas en un entorno donde cada servicio puede estar bajo desarrollo independiente.

---

## Diagrama de arquitectura e integración

```
┌─────────────────────────────────────────────────────────────────┐
│                         TaskService                             │
│  add_task(title)                                                │
│    ├── storage.load()    → verifica duplicados                  │
│    ├── storage.save()    → persiste la tarea nueva              │
│    └── notifier.send()   → envía notificación                   │
│  complete_task(title)                                           │
│    ├── storage.load()    → carga tareas                         │
│    └── storage.save()    → guarda cambio de estado              │
│  list_tasks()                                                   │
│    └── storage.load()    → retorna lista actual                 │
└───────────────┬──────────────────────────┬──────────────────────┘
                │                          │
    ┌───────────▼──────────┐   ┌──────────▼──────────┐
    │     TaskStorage      │   │      Notifier        │
    │  load() → JSON read  │   │  send() → SMTP/print │
    │  save() → JSON write │   │  (puede fallar)      │
    └──────────────────────┘   └──────────────────────┘

Enfoques usados:
  Top-Down:  Service + StubStorage + StubNotifier
  Bottom-Up: TaskStorage directo (driver, sin Service)
  Sandwich:  Service + TaskStorage real + StubNotifier
```

---

## Resultado de ejecución de tests

```
27 passed, 1 failed (documentado)
FAILED: test_add_task_titulo_vacio_no_debe_persistirse
→ Bug real del sistema: Service acepta y persiste títulos vacíos.
  Debe corregirse añadiendo validación en add_task.
```

Con la versión saboteada de `add_task` (`return True`):
```
14 failed → pruebas de integración detectan correctamente el sabotaje
```
