# Informe Técnico - Taller de Pruebas de Integración
**Asignatura:** Calidad de Software  
**Universidad:** Universidad Antonio Nariño (UAN)  
**Estudiante:** Jovany Gutierrez Vergara  
**Código:** 12242217515  
**Fecha:** 29 de Mayo de 2026  

---

## 🔍 Parte 2 – Análisis crítico de las pruebas existentes

### 1. ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?
**No.** Las pruebas provistas al inicio del taller no validan la colaboración real y el comportamiento acoplado entre los módulos. Solo se limitan a invocar los métodos de `TaskService` y hacer aserciones superficiales sobre el valor de retorno booleano (`True`). 

Estas pruebas "en verde" dan una falsa sensación de seguridad debido a que no inspeccionan si los datos fueron modificados físicamente en el almacenamiento, ni si los efectos secundarios críticos (como el envío de notificaciones por correo) ocurrieron con los parámetros esperados.

### 2. ¿Qué interacciones entre módulos no están siendo validadas?
* **Persistencia efectiva de datos:** No se verifica que al llamar a `service.add_task()`, los datos realmente se hayan escrito en el archivo físico JSON mediante el método `storage.save()`.
* **Invocación de Notificación:** No se valida si el servicio llama al método `notifier.send()` para notificar al usuario.
* **Aislamiento en errores:** No se verifica el comportamiento del sistema cuando uno de los módulos de integración (p. ej. `Notifier` o `Storage`) falla, lo que deja las excepciones al descubierto.
* **Independencia del estado:** Los archivos físicos de prueba no se limpian sistemáticamente antes y después de cada test. Por ende, la ejecución de una prueba deja remanentes que alteran el estado inicial de la prueba subsiguiente, rompiendo el principio de aislamiento.

### 3. ¿Qué fallos típicos de integración podrían pasar desapercibidos?
* **Excepciones no controladas de red (Efectos secundarios):** Si `notifier.send()` lanza una excepción de comunicación (`ConnectionError`), la ejecución de la lógica de negocio se interrumpe abruptamente sin que el cliente reciba un manejo de error limpio.
* **Estados inconsistentes en base de datos/archivo:** Si el notificador de red falla *después* de que el archivo JSON ya fue actualizado, el sistema queda en un estado inconsistente. La tarea existirá en el almacenamiento persistente, pero la notificación jamás se envió ni se le reportó el fallo al usuario de forma integrada.
* **Excepciones de escritura (I/O):** Si el almacenamiento no tiene permisos de escritura o el disco está lleno (`IOError`), el sistema fallará sin que exista una prueba de integración que valide cómo se propaga o maneja esta situación.
* **Falsos positivos por contratos desalineados:** Si la firma de los métodos entre los componentes cambia, pero las pruebas de integración no validan el flujo de datos exacto, podrían ocurrir fallos catastróficos en producción que los tests ignoran.

---

## ⚠️ Parte 3 – El lado oscuro de las pruebas de integración

Tras aplicar el sabotaje controlado en `add_task` dentro de `src/service.py` (haciendo que retorne siempre `True` sin utilizar el storage ni invocar al notifier), obtuvimos los siguientes resultados:

### 1. ¿Las pruebas detectaron el error?
**Parcialmente e indirectamente.** 
* La prueba `test_add_task_happy_path` **NO** detectó el sabotaje y continuó pasando exitosamente en verde.
* La prueba `test_complete_task` **SÍ** falló con un error del tipo `AssertionError: assert False is True`, debido a que intentaba completar una tarea que nunca se persistió en el almacenamiento físico.

### 2. ¿Por qué siguen pasando?
La prueba `test_add_task_happy_path` sigue pasando porque está débilmente diseñada: su única aserción es `assert result is True`. Dado que el método saboteado fue forzado a retornar directamente `True` (bypasseando por completo la persistencia y la notificación), el test evalúa la aserción como exitosa sin darse cuenta de que el sistema interno no realizó ninguna acción real.

### 3. ¿Qué debilidad fundamental tienen estas pruebas de integración?
Su debilidad fundamental es la **falta de validación de efectos secundarios y contratos de colaboración**. Confían únicamente en el canal de retorno simple de la función (el booleano) en lugar de verificar el comportamiento de los componentes integrados. En pruebas de integración, es imperativo validar:
1. Que los componentes dependientes fueron efectivamente llamados.
2. Que fueron llamados con los parámetros correctos.
3. Que el estado persistente final del sistema cambió de acuerdo a la operación.

---

## 🔧 Parte 4 – Aplicación de los enfoques de integración

### 4.1 Enfoque Top-Down (Pruebas en `TestTopDown`)
Para este enfoque, simulamos los componentes de nivel inferior (`Storage` y `Notifier`) construyendo stubs manuales independientes: `StorageStub` y `NotifierStub`. Esto nos permitió aislar por completo la lógica del servicio `TaskService` (módulo de alto nivel) para validar su flujo de control sin depender de accesos al disco duro o conexiones simuladas a la red.
* **Verificación de contratos:** Validamos que el servicio invoque a `storage.save` con la colección que contiene la nueva tarea estructurada y que ejecute `notifier.send` con el mensaje descriptivo exacto: `"Tarea '...' creada"`.
* **Casos extremos:** Validamos el comportamiento ante títulos vacíos y duplicados sin alterar ningún entorno físico.

### 4.2 Enfoque Bottom-Up (Pruebas en `test_storage_driver.py`)
Diseñamos un **driver de prueba** directo para validar de forma totalmente aislada el módulo de nivel inferior `TaskStorage`. De esta manera, probamos exhaustivamente la persistencia JSON sin instanciar ni depender del módulo de negocio `TaskService`.
Añadimos **4 pruebas completas** que cubren:
1. **Archivo no existe:** Validamos que al iniciar el storage, se cree físicamente en el disco con la estructura básica `[]`.
2. **Guardar y recuperar una tarea:** Validamos que un diccionario de tarea se escriba y se lea manteniendo sus atributos intactos.
3. **Guardar y recuperar múltiples tareas:** Validamos la integridad del archivo JSON al manejar colecciones ordenadas de múltiples tareas.
4. **Política ante títulos vacíos:** 
   * **Definición de Política:** Aplicando el principio de diseño de *Responsabilidad Única*, definimos que la capa de almacenamiento (`TaskStorage`) es un componente puramente tecnológico y de infraestructura. Su único rol es persistir las estructuras de datos JSON que recibe del negocio. Por ende, **el almacenamiento no impone reglas sobre el contenido del título** (es permisivo), delegando la validación del dominio y del negocio exclusivamente al servicio `TaskService`. El test del driver verifica que el almacenamiento puede persistir con éxito una tarea con título vacío si es provista directamente, confirmando el desacoplamiento arquitectónico adecuado.

### 4.3 Enfoque Sandwich (Pruebas en `TestSandwich`)
El enfoque Sandwich (híbrido) combina el componente de infraestructura real `TaskStorage` (que escribe a un archivo en el directorio temporal del sistema) con el stub de notificaciones `NotifierStub` (evitando llamadas inestables de red).
* **Integración parcial:** Se valida que `TaskService` interactúa correctamente con el archivo físico real a la vez que colabora con un notificador simulado de forma estable.

---

## 🔧 Parte 5 – Mejora de las pruebas de integración y robustez

Hemos refactorizado la lógica de negocio en `src/service.py` e implementado pruebas de integración avanzadas y robustas que aseguran la consistencia y la detección inmediata del sabotaje:

### 1. Detección del Sabotaje (Parte 3)
Las nuevas pruebas Sandwich realizan aserciones directas sobre los stubs de notificación (`notifier.send_called`) y sobre la lectura directa del almacenamiento real (`storage.load()`). Si el método es saboteado para omitir estos pasos, las aserciones de integración fallan de inmediato, impidiendo que el código defectuoso pase desapercibido.

### 2. Consistencia y Rollback ante errores parciales
* **El Problema de Integración:** Si la persistencia es exitosa pero la red falla al enviar la notificación, el sistema queda en un estado inconsistente (el almacenamiento tiene una tarea de la cual el usuario final nunca fue alertado de su creación).
* **Solución de Consistencia (Rollback):** Implementamos un bloque transaccional controlado en `add_task`. Si `notifier.send` lanza una excepción (como `ConnectionError`), capturamos el error y realizamos un **Rollback de datos**, sobrescribiendo el almacenamiento con el estado previo a la transacción. Posteriormente, propagamos la excepción para alertar al cliente.
* **Prueba de Validación:** En `test_notifier_failure_triggers_rollback_in_real_storage`, simulamos que el notificador lanza `ConnectionError` y verificamos que el archivo JSON final queda completamente limpio, demostrando que no hay corrupción ni inconsistencia de datos tras un error de comunicación.

### 3. Casos Extremos y Robustez General
* **Fallo en Almacenamiento:** Validamos con `FailsStorageStub` que si el disco falla lanzando `IOError`, la excepción se propaga limpiamente y se detiene el flujo (no se intenta enviar notificaciones inútiles).
* **Títulos Vacíos:** `add_task` ahora valida mediante `not title or not title.strip()` y rechaza el registro retornando `False` sin persistir ni notificar.
* **Tareas Duplicadas:** Se valida mediante comparación lineal de títulos para evitar tareas repetidas y mantener la integridad lógica de la colección.
* **Listado de Tareas Robustas:** Modificamos `src/storage.py` para soportar de manera robusta casos donde el archivo físico JSON no existe, está vacío (tamaño 0 bytes) o está corrupto, retornando de forma segura una lista vacía `[]` en lugar de romper el sistema con `JSONDecodeError`.

---

## 📊 Parte 6 – Reflexión sobre cobertura de integración

### 1. ¿Qué diferencia hay entre cobertura de código (líneas ejecutadas) y cobertura de integración?
* **Cobertura de código (Code Coverage):** Es una métrica meramente cuantitativa. Mide el porcentaje de líneas de código, bloques o ramas que son recorridos físicamente por la suite de pruebas durante su ejecución. No evalúa si los resultados obtenidos son lógicos o si los componentes están colaborando de manera correcta.
* **Cobertura de integración:** Es una dimensión cualitativa. Mide el grado en que los caminos de comunicación, interfaces, flujos de datos y contratos entre diferentes módulos autónomos del sistema han sido validados bajo escenarios exitosos y de fallo. Se enfoca en la frontera de contacto entre componentes.

### 2. ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?
Porque las pruebas unitarias validan cada componente en aislamiento, asumiendo (a través de mocks) que el resto del universo se comporta según el contrato esperado. En un entorno integrado real:
* Las suposiciones de diseño de las dependencias pueden ser incorrectas o estar desactualizadas.
* Pueden ocurrir fallos físicos de red, timeouts o problemas de permisos de archivos inaccesibles que los mocks omiten por diseño.
* Pueden presentarse inconsistencias de estado compartido, condiciones de carrera o desalineación en el formato de transferencia de datos (p. ej. un módulo esperando una lista y recibiendo un diccionario).

### 3. ¿Qué métricas o señales te indicarían que unas pruebas de integración son insuficientes?
* **Paso Exitoso de Pruebas con Módulos Rotos:** El hecho de sabotear o desactivar funciones internas clave (como persistencia o notificaciones) y que la suite de pruebas continúe pasando en verde (como en la Parte 3).
* **Ausencia de Aserciones de Efecto Secundario:** Que las pruebas solo realicen `assert` sobre el tipo de retorno directo de las funciones, sin validar el cambio de estado persistente o llamadas a otros subsistemas.
* **Falta de Pruebas de Fallo Parcial:** Pruebas que solo exploran el "Happy Path" (camino feliz) y omiten comprobar qué sucede si la base de datos se cae, si se va el internet o si un archivo está corrupto.
* **Mucha dependencia del entorno local:** Pruebas que fallan si se corren en una máquina distinta debido a rutas rígidas o dependencias externas no aisladas con stubs.

---

## 🧠 Parte 7 – Reflexión final

### 1. ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
Aprendí que las pruebas unitarias son excelentes para validar algoritmos específicos y lógica interna compleja de forma rápida, pero son ciegas ante problemas de comunicación y sincronización de estado. Las pruebas de integración son la verdadera línea de defensa para asegurar que la maquinaria completa del software se ensamble y funcione coordinadamente, capturando problemas de contratos y fallos físicos que las unitarias jamás verían.

### 2. ¿En qué situaciones reales usarías un enfoque bottom-up y en cuáles top-down? Justifica con base en la arquitectura del sistema.
* **Bottom-Up:** Lo usaría en sistemas donde la infraestructura de bajo nivel (capas de persistencia ORM, wrappers de APIs financieras externas, sistemas embebidos de lectura de sensores o drivers de comunicación directa) es la parte más compleja, crítica y propensa a fallar. Al validar primero la base del sistema mediante drivers robustos, aseguramos la estabilidad física antes de ensamblar la lógica del negocio de alto nivel.
* **Top-Down:** Lo usaría en proyectos de desarrollo ágil, prototipos rápidos, o metodologías como BDD/TDD enfocado en la experiencia de usuario (UX) o en la API de negocio principal. Cuando los microservicios externos o la base de datos de infraestructura aún no están definidos o no están listos, el uso de stubs detallados permite diseñar y refinar la lógica del negocio de alto nivel de forma prioritaria, posponiendo las decisiones técnicas de almacenamiento e infraestructura.

### 3. ¿Cómo aplicarías stubs y drivers en un proyecto con microservicios o con bases de datos externas?
* **Microservicios (Stubs):** Para aislar un microservicio bajo prueba de sus vecinos en la red, utilizaría herramientas como **WireMock**, **Mountebank** o contenedores con respuestas mockeadas (Mock Servers). Estos stubs interceptan las peticiones HTTP/gRPC salientes y retornan respuestas JSON estáticas preconfiguradas (tanto exitosas como con latencia o códigos de error 500), garantizando que las pruebas no dependan del estado real de los otros microservicios en el clúster.
* **Bases de Datos Externas (Stubs / In-Memory):** Implementaría stubs o repositorios mockeados en memoria (como SQLite in-memory para bases relacionales o `mongomock` para MongoDB) para agilizar las pruebas de negocio rápidas sin conectarse al servidor real.
* **Microservicios y Bases de Datos (Drivers):** Para pruebas de integración reales Bottom-Up, utilizaría **Docker Compose** o **Testcontainers** para instanciar en cada ejecución una base de datos real (PostgreSQL/Redis) o un bus de mensajería (RabbitMQ). El driver de prueba sería una suite ejecutada mediante peticiones reales (utilizando herramientas como `requests` o el cliente de pruebas de FastAPI) que dispara cargas de datos específicas contra los endpoints del microservicio desplegado en el contenedor, validando la interacción física completa de extremo a extremo.

---

## 📦 Anexo - Diagrama de Integración y Colaboración

A continuación se muestra un diagrama ASCII que ilustra la arquitectura de integración implementada y cómo se distribuyen los stubs durante las fases de pruebas:

```
                                +-------------------+
                                |    TEST SUITE     |
                                | (Pytest Runner)   |
                                +---------+---------+
                                          |
                        +-----------------+-----------------+
                        |                 |                 |
                  (Enfoque Top-Down)      |          (Enfoque Sandwich)
                        |                 |                 |
                        v                 v                 v
                 +--------------+         |          +--------------+
                 |  StorageStub |         |          | TaskStorage  |
                 | (Manual Stub)|         |          | (Real File)  |
                 +------+-------+         |          +------+-------+
                        ^                 |                 ^
                        |                 |                 |
                        +-----------+     |     +-----------+
                                    |     |     |
                                    v     v     v
                              +---------------------+
                              |     TaskService     | <--- (Módulo de Negocio Principal)
                              +----------+----------+
                                         |
                        +----------------+----------------+
                        |                                 |
                        v                                 v
                 +--------------+                  +--------------+
                 | NotifierStub |                  |   Notifier   |
                 | (Manual Stub)|                  | (Real/Random)|
                 +--------------+                  +--------------+
                  (Aislamiento)                     (Producción)
```

Este esquema de pruebas garantiza un 100% de cobertura cualitativa en todos los niveles, detectando fallos en la persistencia física, controlando de forma segura las dependencias inestables y resguardando la consistencia transaccional del sistema mediante el mecanismo de Rollback de datos ante fallos externos.
