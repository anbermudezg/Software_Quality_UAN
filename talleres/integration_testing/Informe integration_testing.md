# Taller: Pruebas de Integración – Más allá de los tests unitarios

## 🔍 Parte 2 – Análisis crítico de las pruebas

Responde en un documento:

- ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?
  Las pruebas actuales validan únicamente algunos casos básicos de funcionamiento entre los módulos. Aunque los tests pasan correctamente, esto no nos garantiza que toda la integración entre componentes sea robusta.
  Por ejemplo, las pruebas verifican operaciones simples como agregar tareas, completarlas y guardar información, pero no están evaluando escenarios más complejos donde puedan ocurrir errores durante la comunicación entre módulos.
  En conclusión, las pruebas actuales comprueban el funcionamiento básico, pero no cubren completamente la colaboración entre todos los componentes del sistema.

- ¿Qué interacciones entre módulos no están siendo validadas?
  Hay varias cosas que las pruebas actuales no están comprobando. Por ejemplo, no revisar qué pasa si el módulo de almacenamiento falla o si recibe datos incorrectos. 
  Tampoco validan situaciones donde un módulo devuelve información inesperada o cuando hace muchas operaciones seguidas.
  Además, no se comprueba bien cómo reaccionan los módulos cuando ocurre un error durante la comunicación entre ellos, por lo que todavía podrían existir problemas ocultos de integración.      

- ¿Qué fallos típicos de integración (errores de comunicación, excepciones no controladas, estados inconsistentes) podrían pasar desapercibidos?
  Algunos errores importantes podrían pasar desapercibidos porque las pruebas actuales son muy básicas. Por ejemplo, podrían existir problemas cuando un módulo envía información incorrecta a otro, cuando ocurre una excepción y el programa no sabe manejarla, o cuando los datos quedan guardados de manera incompleta. 
  También podría pasar que una tarea aparezca como completada en una parte del sistema pero no en otra, generando inconsistencias. Como no se están comprobando escenarios más difíciles, todavía pueden existir errores de integración que no han sido detectados.


## ⚠️ Parte 3 – El lado oscuro de las pruebas de integración

Responde:

- ¿Los tests detectaron el error?
  Las pruebas no lograron detectar el error, ya que, a pesar de que el código está completamente roto, porque no guarda las tareas en el almacenaje ni envía las notificaciones, en las pruebas se muestra que todo pasa con éxito; esto solo nos muestra que las pruebas pasaron por alto el fallo. 

- ¿Por qué siguen pasando?
  Las pruebas actuales siguen pasando porque están mal diseñadas, puesto que solo verifican que el método devuelve true al terminar, pero no está comprobando los efectos secundarios. 
  Esto quiere decir que la prueba asume que la función responde de True que todo salió bien, pero no se toma el trabajo de ir al módulo de almacenamiento a verificar si el archivo de texto o la base de datos guardó la tarea, ni revisar si el notificador hizo su tarea. 

- ¿Qué debilidad fundamental tienen estas pruebas de integración?
  La debilidad principal es que no está validando la integración real entre los componentes, solo prueba el resultado superficialmente del método principal (service.py). Pero no verifica el comportamiento ni el estado de los módulos con los que interactúa (almacenamiento y el notificador).
  Para que sean verdaderas las pruebas de integración, deberían controlar que los datos viajen de un módulo a otro y se guarden de verdad, en lugar de sólo confiar que sean verdaderas. 


## 🔧 Parte 4 – Aplicación de enfoques de integración


### 4.1 Enfoque Top‑Down
Se realizaron las modificaciones pertinentes segun las indicaciones dadas, revisar el archivo.

## ¿Qué es y por qué usarlo aquí?
En el enfoque Top-Down pruebas el módulo de nivel más alto (Service) primero, y reemplazas sus dependencias de nivel inferior (Storage, Notifier) con stubs —objetos falsos que simulan el comportamiento esperado sin ejecutar la lógica real.
Esto te permite validar que la lógica de negocio de Service es correcta: que llama a sus dependencias con los parámetros correctos, que maneja duplicados, que retorna los valores esperados, etc

## ¿Qué cambios se hicieron?
Los tests originales dependían de componentes reales, lo que generaba pruebas frágiles por la escritura de archivos físicos y el fallo aleatorio del notificador.
En la Parte 4.1, se sustituyeron TaskStorage y Notifier por Stubs manuales en memoria. Con este cambio, los nuevos tests no solo evalúan el resultado final, sino que validan con total certeza el contrato de integración: es decir, verifican que TaskService invoque a las dependencias en el orden correcto y con los parámetros exactos esperados, eliminando efectos secundarios y la aleatoriedad.


### 4.2 Enfoque Bottom‑Up
Se realizaron las modificaciones pertinentes segun las indicaciones dadas, revisar el archivo.

## ¿Qué es y por qué usarlo aquí?
En el enfoque Bottom-Up pruebas el módulo de nivel más bajo (TaskStorage) de forma aislada, usando un driver (suite de pruebas) para controlar sus entradas y salidas directamente, sin depender de la lógica de negocio del nivel superior (TaskService).
Esto permite validar que la base de datos JSON lee, escribe e inicializa los archivos de manera correcta y segura bajo cualquier escenario físico.

## ¿Qué cambios se hicieron?
El archivo tests/test_storage_driver.py tenía una versión inicial débil que solo probaba un caso básico y dejaba basura en el disco.
En la Parte 4.2, se reorganizó el código y se le añadió un fixture automatizado que limpia el entorno. Se expandió el driver a 5 pruebas rigurosas: creación con lista vacía si el archivo no existe, flujo unitario, persistencia de múltiples tareas en orden, y la política para títulos vacíos (donde el storage permite guardarlo por ser un archivo físico válido, delegando la regla de negocio al servicio), logrando un componente de persistencia robusto e independiente.

### 4.3 Enfoque Sandwich
Se realizaron las modificaciones pertinentes, revise el archivo 

## ¿Qué es y por qué usarlo aquí?
 En el enfoque Sandwich se combinan componentes reales en las capas de persistencia inferiores (`TaskStorage`) con un **stub** para aislar las dependencias externas o inestables del sistema (`Notifier`). 

## ¿Qué cambios se hicieron?
 Se creó el archivo `tests/test_sandwich_integration.py` con dos escenarios de integración híbrida. Al instanciar un `TaskStorage` real junto con un `NotifierSandwichStub` en memoria, la primera prueba verifica simultáneamente que el archivo JSON se escribe físicamente en el disco y que el servicio envía los parámetros correctos de notificación. La segunda prueba válida de manera real que las restricciones de duplicados protegen el almacenamiento físico y bloquean llamadas de notificación innecesarias, logrando una suite veloz, segura y determinista. 




## 🔧 Parte 5 – Mejora de las pruebas de integración

## ¿Qué se hizo?: 
Se programaron pruebas de integración avanzadas utilizando stubs falsos y un driver de almacenamiento para forzar intencionalmente escenarios críticos (caída del servidor de red, disco duro lleno, archivos JSON en 0 bytes y tareas duplicadas).

## ¿Para qué se hizo?: 
Para garantizar la robustez y la tolerancia a fallos del sistema. Sirve para certificar que el negocio no se detenga si internet se cae (manteniendo la consistencia al guardar localmente) y asegurar que la aplicación nunca colapse ni explote ante errores físicos de hardware o archivos de datos corruptos.

## 📊 Parte 6 – Reflexión sobre cobertura de integración

## ¿Qué diferencia hay entre cobertura de código (líneas ejecutadas) y cobertura de integración?
La cobertura de código se refiere a cuántas líneas o partes del programa fueron ejecutadas durante las pruebas. Esto ayuda a saber si el código fue recorrido por los tests, pero no significa necesariamente que todo funcione bien. En cambio, la cobertura de integración se enfoca en comprobar si los diferentes módulos del sistema realmente trabajan correctamente entre sí, compartiendo datos y comunicándose de forma adecuada. Es decir, una prueba puede ejecutar muchas líneas de código, pero aun así no validar correctamente la interacción entre componentes.

## ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?
Porque las pruebas unitarias normalmente prueban cada módulo por separado y de forma aislada. Aunque cada parte funcione correctamente individualmente, pueden aparecer errores cuando todos los módulos se conectan e intercambian información. Por ejemplo, puede haber problemas con parámetros incorrectos, datos inconsistentes, excepciones no controladas o fallos en la comunicación entre módulos. Por eso, tener 100% de cobertura unitaria no asegura que el sistema completo funcione bien cuando todos los componentes trabajan juntos.

## ¿Qué métricas o señales te indicarían que unas pruebas de integración son insuficientes?
Algunas señales de que las pruebas de integración son insuficientes son cuando los tests solo revisan resultados simples y no validan las interacciones reales entre los módulos. También es una señal negativa si las pruebas no detectan errores importantes aunque el sistema esté roto, como ocurrió en la parte 3. Otras señales pueden ser la falta de pruebas para casos extremos, ausencia de validación de errores o excepciones, poca verificación de estados internos y dependencia de pruebas demasiado superficiales que solo revisan valores de retorno sin comprobar lo que realmente ocurre dentro del sistema.


## 🧠 Parte 7 – Reflexión final

Responde:

## ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
Aprendimos que las pruebas unitarias sirven para comprobar que una función o módulo funciona correctamente por separado, pero no garantizan 	que todo el sistema integrado funcione bien. Un módulo puede pasar todas sus pruebas individuales y aun así fallar cuando se comunica con otros componentes. Las pruebas de integración son importantes porque permiten validar cómo interactúan realmente los módulos, cómo comparten información y cómo reaccionan ante errores o situaciones inesperadas.  

## ¿En qué situaciones usarías un enfoque bottom‑up y en cuáles top‑down?
Usaría el enfoque bottom-up cuando los módulos inferiores, como el almacenamiento o la base de datos, son los más importantes y necesito asegurar primero que funcionan correctamente antes de integrarlos con el resto del sistema. En este proyecto, por ejemplo, tendría sentido probar primero storage.py porque es el encargado de guardar y cargar la información.
En cambio, usaría top-down cuando quiero validar primero la lógica del sistema y el flujo general de la aplicación. En este caso, service.py es el módulo principal porque coordina la comunicación entre el almacenamiento y el notificador. Por eso, usando stubs se puede probar primero la lógica del servicio sin depender de que los demás módulos funcionen completamente. 

## ¿Cómo aplicarías stubs y drivers en un proyecto real para desacoplar dependencias externas?
En un proyecto real con microservicios o bases de datos externas usaría stubs para simular servicios que todavía no existen o son difíciles de controlar durante las pruebas, por ejemplo una API de pagos o un servicio de correos. De esta manera se pueden hacer pruebas sin depender de internet o sistemas externos reales. También usaría drivers para probar módulos pequeños que todavía no tienen una interfaz principal completa, simulando las llamadas de entrada para probar módulos aún no conectados a una interfaz completa. En ambos casos el objetivo es aislar las pruebas de dependencias externas costosas o inestables, logrando pruebas rápidas, deterministas y reproducibles en cualquier entorno."



## 📦 8. Anexo: Contenido Opcional (Puntos Extra)

Para complementar la suite de integración, se incorporaron elementos opcionales de valor arquitectónico y tácticas avanzadas de diseño de pruebas basadas en la experiencia.

### 8.1 Diagrama de Arquitectura e Integración de Módulos (ASCII)
El siguiente esquema ilustra cómo interactúan los componentes reales del sistema y de qué manera se inyectaron los *Stubs*, *Mocks* y *Drivers* en las fases de pruebas (**Top-Down**, **Bottom-Up** y **Sandwich**):

```text
      [ CAPA DE CONTROL / LÓGICA ]              [ CAPA DE PERSISTENCIA ]
            +-------------+                         +-------------+
            | TaskService |<------------------------| TaskStorage |
            +------+------+                         +-------------+
                   |                                       |
                   | (Petición de Red)                     | (Escritura Física)
                   v                                       v
            +-------------+                         +-------------+
            |  Notifier   |                         |  tasks.json |
            +-------------+                         +-------------+
                   |                                       |
  =================|=======================================|=================
    ESTRATEGIAS DE AISLAMIENTO E INYECCIÓN EN TESTING:     |
                                                           |
  [Top-Down]   --> Inyecta: StorageStub y NotifierStub     |
  [Bottom-Up]  --> Ataca de forma aislada mediante un      +--> Driver directo
  [Sandwich]   --> Combina: TaskStorage (REAL) + NotifierSandwichStub
  [Opcionales] --> Aísla la red mediante un NotifierMock genérico
```
## 8.2 Batería de Pruebas Adicionales: "Error Guessing"

## ¿Qué se hizo?: 
Se creó un archivo de pruebas (test_error_guessing_opcional.py) usando un Mock para inyectar entradas anómalas: cadenas vacías/espacios, inyección de código HTML (<script>) y duplicados combinando mayúsculas y minúsculas.

## ¿Para qué se hizo?: 
Para anticipar comportamientos maliciosos o errores comunes del usuario común (Error Guessing). Sirve para certificar que el sistema bloquee el registro de tareas invisibles, detecte duplicados aunque cambie la tipografía y almacene scripts de forma segura como texto plano sin romper la aplicación.
