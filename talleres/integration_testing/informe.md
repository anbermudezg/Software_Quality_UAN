# Informe – Taller: Pruebas de Integración

---

## Resumen

En este taller se realizó un proceso completo de evaluación y mejora de pruebas de integración, comenzando con la ejecución de los tests existentes y el análisis de sus limitaciones. Se identificó que las pruebas iniciales no garantizaban la correcta colaboración entre módulos, ya que estaban diseñadas para verificar únicamente el valor de retorno de las funciones, sin comprobar efectos secundarios como la escritura en archivos o el envío de notificaciones. Al modificar intencionalmente el método `add_task` para que siempre retornara `True` sin invocar al almacenamiento ni al notificador, se comprobó que todos los tests seguían pasando, lo que evidenció la debilidad de afirmaciones centradas solo en resultados inmediatos y la falta de validación de las interacciones reales entre componentes.

A partir de allí, se aplicaron los enfoques clásicos de integración: en el enfoque top-down se crearon stubs para `Storage` y `Notifier` que permitieron verificar las llamadas y los parámetros intercambiados; en el enfoque bottom-up se implementó un driver para probar el módulo `TaskStorage` de forma aislada con casos como archivo inexistente, guardado y recuperación de tareas, y manejo de títulos vacíos; y en el enfoque sandwich se combinaron módulos reales con stubs para validar integraciones parciales sin depender de servicios externos. Adicionalmente, se ampliaron las pruebas para cubrir escenarios de error como fallos durante el almacenamiento, fallos en la notificación, títulos vacíos, tareas duplicadas y consistencia del sistema ante errores parciales, logrando que las nuevas pruebas sí detectaran el sabotaje realizado.

Finalmente, se reflexionó sobre la diferencia entre cobertura de código y cobertura de integración, entendiendo que alcanzar el 100 % de líneas ejecutadas no es suficiente para asegurar la corrección del software integrado, y que es indispensable validar las colaboraciones reales, los contratos entre módulos y el comportamiento ante fallos para tener confianza en el sistema.

---

## Parte 2 – Análisis crítico de las pruebas iniciales

### ¿Las pruebas actuales verifican realmente la colaboración entre módulos?

No. Las pruebas originales solo verifican que los métodos `add_task` y `complete_task` devuelvan `True`, pero no comprueban que realmente se haya escrito la tarea en el archivo o que se haya enviado una notificación. Por ejemplo, `test_add_task_happy_path` crea un `TaskStorage` real y un `Notifier` real, pero nunca lee el archivo para confirmar que la tarea se guardó, ni revisa que el notificador haya sido invocado. La colaboración entre módulos queda sin validar.

### Interacciones entre módulos no validadas

No se está validando la comunicación entre `TaskService` y `TaskStorage` (escritura y lectura de tareas) ni entre `TaskService` y `Notifier` (envío de notificaciones con el mensaje correcto). Tampoco se verifican los contratos de datos: por ejemplo, que el servicio envíe al almacenamiento una tarea con la estructura esperada. Además, no se prueban escenarios donde estos módulos fallen o reciban entradas inesperadas.

### Fallos típicos de integración que podrían pasar desapercibidos

Podrían pasar desapercibidos fallos de comunicación (excepciones silenciadas en `storage.save` o `notifier.send`), estados inconsistentes (una tarea guardada pero no notificada, o viceversa), errores de formato entre módulos, y dependencias no controladas (por ejemplo, que el notificador necesite red y los tests sigan pasando sin red real). También quedarían ocultos errores lógicos como la duplicación de tareas o la aceptación de títulos vacíos.

---

## Parte 3 – El lado oscuro: sabotaje controlado

### ¿Las pruebas detectaron el error?

No. Los tests de integración existentes (`test_add_task_happy_path` y `test_complete_task`) siguieron pasando después de modificar `add_task` para que siempre devuelva `True` sin hacer nada más. El error no fue detectado.

### ¿Por qué siguen pasando?

Pasan porque su única verificación es `assert result is True`. Las pruebas no examinan los efectos secundarios de la operación, como la escritura real en el archivo o las llamadas al notificador. Al no exigir que el sistema haya interactuado realmente con sus dependencias, cualquier implementación que retorne `True` satisface la condición, incluso si está completamente rota.

### Debilidad fundamental

Su debilidad es que confunden "prueba en verde" con "sistema integrado correctamente". Validan únicamente el valor de retorno inmediato, ignorando por completo la colaboración entre módulos, los efectos secundarios y el manejo de errores. Esto las convierte en pruebas ciegas ante fallos de integración reales, ya que no ejercitan el flujo completo ni los contratos entre componentes.

---

## Parte 4 – Enfoques de integración aplicados

### 4.1 Top-Down (`TestTopDown`)

Se crearon dos stubs: `StubStorage` (almacena en memoria y registra llamadas) y `StubNotifier` (acumula mensajes). Con ellos se aisló completamente `TaskService` y se verificó:

- Que `storage.save` es invocado con los datos correctos.  
- Que `notifier.send` es invocado con el mensaje esperado.  
- Que la política de duplicados funciona sin depender de disco.  
- Que título vacío es rechazado (`return False`, sin escritura).  
- Comportamiento ante fallos: `StubStorageRaisesOnSave` y `StubNotifierRaises` permiten verificar que las excepciones se propagan (el `service.py` original no las captura).

**Ventaja del enfoque**: permite probar la lógica de negocio de `Service` incluso antes de que `Storage` o `Notifier` existan en su forma final.

### 4.2 Bottom-Up (`TestTaskStorageDriver`)

Se escribió un driver (`test_storage_driver.py`) que prueba `TaskStorage` directamente, sin `Service`. Las 8 pruebas cubren:

1. Creación automática del archivo si no existe.  
2. Guardar y recuperar una tarea.  
3. Guardar y recuperar múltiples tareas.  
4. Título vacío: `Storage` lo acepta (decisión de política: la validación le corresponde a `Service`).  
5. Sobrescritura del contenido previo.  
6. Guardar lista vacía.  
7. Persistencia real entre dos instancias distintas del objeto.  
8. Que `load()` no modifica el archivo en disco.

**Ventaja del enfoque**: da confianza en el componente de menor nivel antes de integrar capas superiores.

### 4.3 Sandwich (`TestSandwich`)

Se combinó `TaskStorage` **real** (archivo temporal) con `StubNotifier`. Esto valida que:

- La tarea escrita por `Service` sobrevive a una recarga desde disco.  
- El stub del notificador recibe exactamente el mensaje generado por `Service`.  
- Duplicados no se duplican en el archivo JSON.

**Ventaja del enfoque**: detecta problemas de serialización/deserialización que los stubs de memoria no pueden revelar, sin depender de red ni SMTP.

---

## Parte 5 – Corrección del código fuente

Se identificó y corrigió el error documentado en `service.py`:

```python
# Antes (sin validación):
tasks = self.storage.load()
if title in [t['title'] for t in tasks]:
    return False

# Después (con validación de título vacío):
if not title or not title.strip():
    return False
tasks = self.storage.load()
if title in [t['title'] for t in tasks]:
    return False
```

La prueba `test_add_task_titulo_vacio_rechazado` falla con la versión original y pasa con la corregida, cumpliendo el criterio de detección de errores reales (30 % de la nota).

Las pruebas `test_add_task_realmente_usa_storage` y `test_add_task_realmente_usa_notifier` detectan la versión saboteada de la Parte 3: si `add_task` devuelve `True` sin llamar a los módulos, ambas pruebas fallan.

---

## Parte 6 – Reflexión sobre cobertura de integración

### Diferencia entre cobertura de código y cobertura de integración

La cobertura de código mide el porcentaje de líneas, ramas o caminos del código fuente que se ejecutan durante las pruebas. La cobertura de integración, en cambio, se refiere a la medida en que las interacciones entre módulos son ejercitadas y validadas, incluyendo llamadas, intercambio de datos y manejo de fallos. Se puede tener un 100 % de cobertura de código (todas las líneas ejecutadas) y 0 % de cobertura de integración si nunca se verifican las colaboraciones.

**Ejemplo observado en el taller**: las pruebas originales cubrían al 100 % las líneas de `add_task`, pero no verificaban que `storage.save` o `notifier.send` fueran llamados. Un sabotaje que elimine esas llamadas mantiene la cobertura de código intacta pero rompe la integración completamente.

### ¿Por qué 100 % de cobertura unitaria no garantiza integración?

Porque las pruebas unitarias aíslan cada módulo con dobles que siempre se comportan de manera ideal. En producción, las dependencias reales pueden fallar, devolver datos con formatos inesperados, ser lentas o no estar disponibles. La cobertura unitaria no valida que los módulos se comuniquen correctamente en conjunto, que los contratos se respeten, ni que el sistema reaccione ante errores en cascada. Por eso, un sistema con alta cobertura unitaria puede fallar estrepitosamente al integrarse.

### Señales de pruebas de integración insuficientes

Señales claras de insuficiencia son: que todas las pruebas pasen después de un sabotaje como el de la Parte 3, que no existan pruebas con stubs que registren llamadas, que no se simulen fallos de dependencias, que nunca se verifiquen archivos o mensajes generados, y que los tests de integración no detecten escenarios como títulos vacíos, duplicados o excepciones en los colaboradores. Otra señal es que no se usen estrategias como top-down o bottom-up para cubrir distintas capas.

---

## Parte 7 – Reflexión final

### ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?

Las pruebas unitarias, aunque son rápidas y aíslan lógica de negocio, no pueden detectar problemas de comunicación, serialización, orden de llamadas o fallos en dependencias externas. Las pruebas de integración son indispensables para garantizar que los módulos realmente colaboran, que el flujo de datos es correcto y que el sistema se comporta de forma robusta ante fallos. Unitarias e integración se complementan; ninguna basta por sí sola.

### ¿Cuándo usar Bottom-Up y cuándo Top-Down?

Se usaría un enfoque **bottom-up** cuando los módulos de más bajo nivel, como el acceso a base de datos o el almacenamiento en archivos, son críticos y complejos. En el taller, aplicar este enfoque a `TaskStorage` permitió validar su comportamiento (archivo inexistente, guardado, recuperación, rechazo de títulos vacíos) antes de construir sobre él.

Se emplearía **top-down** cuando se necesite probar la lógica de orquestación de un servicio de alto nivel sin tener listas todas sus dependencias reales. En el taller, este enfoque se usó para probar `TaskService` con stubs de `Storage` y `Notifier`, verificando que las decisiones y el flujo general fueran correctos, sin preocuparse por detalles de persistencia o envío de mensajes.

### ¿Cómo aplicarías stubs y drivers en un proyecto con microservicios o con bases de datos externas?

En un proyecto con microservicios, se usarían stubs para simular las respuestas de otros servicios (por ejemplo, un stub de un servicio de autenticación) y así evitar dependencias de red durante las pruebas de integración. Los drivers se emplearían para probar directamente adaptadores de base de datos (repositorios) con una base de datos en memoria o un contenedor temporal, validando operaciones CRUD sin necesidad del servicio completo. Esto permite detectar errores de integración de forma temprana y aislada, sin desplegar todo el ecosistema.

### ¿Qué significa realmente que "los tests pasen"?

Significa que, para los escenarios codificados en los tests y con las comprobaciones que se incluyeron, la unidad de código devolvió lo que se esperaba. Esto no significa que el programa esté libre de errores ni que cumpla correctamente todos los requisitos; simplemente dice que los caminos probados no rompieron las afirmaciones definidas. Si esas afirmaciones son débiles o los casos son insuficientes, los tests podrían dar una falsa sensación de seguridad.

---

## Diagrama de arquitectura y enfoques aplicados

```
┌─────────────────────────────────────────────────────────┐
│                      TaskService                        │
│  add_task / complete_task / list_tasks                  │
└───────────────┬─────────────────────┬───────────────────┘
                │                     │
        ┌───────▼──────┐     ┌────────▼────────┐
        │  TaskStorage │     │    Notifier     │
        │  (JSON file) │     │ (SMTP / print)  │
        └──────────────┘     └─────────────────┘

Enfoques aplicados:
──────────────────────────────────────────────────────────
Top-Down    │ Service ← StubStorage + StubNotifier
Bottom-Up   │ [Driver] → TaskStorage (sin Service)
Sandwich    │ Service ← TaskStorage (real) + StubNotifier
──────────────────────────────────────────────────────────
```

