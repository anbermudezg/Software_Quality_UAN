# Taller: Pruebas de Integración – Más allá de los tests unitarios

## 🎯 Objetivo

Comprender la importancia de las pruebas de integración, aplicar enfoques (bottom‑up, top‑down, sandwich, big‑bang) y utilizar stubs y drivers para validar la interacción entre módulos.

## 📦 Estructura del proyecto

- `src/`: código del sistema (módulos con errores de integración).
- `tests/`: pruebas iniciales (débiles, pasan pero no detectan fallos reales).
- `tests_hidden/`: pruebas ocultas (solo para evaluación del profesor).
- `notebooks/`: guías interactivas sobre conceptos clave.
- `data/`: archivo de ejemplo para el almacenamiento.

## 🧪 Parte 1 – Instalación y ejecución inicial

1. Clona o descarga el proyecto.
2. Instala las dependencias:

pip install -r requirements.txt

3. Ejecuta las pruebas existentes:

pytest tests/ -v

4. Observa el resultado: todos los tests pasan.

## 🔍 Parte 2 – Análisis crítico de las pruebas

Responde en un documento:

- ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?
R:// No, al revisar las pruebas actuales, en el archivo test_service_integration.py la prueba def test_add_task_happy_path() Solo es correcta si retorna un true pero esto esta mal hecho ya que no detectaria fallos como el hecho de que no se guarde la tarea o muchos mas problemas
- ¿Qué interacciones entre módulos no están siendo validadas?
R:// No se esta validando que despues de add_task la tarea realmente exista en el archivo, asi como no se esta validando que a el metodo Notifier se le esten pasando los datos correctos, tampoco se esta revisando que en la funcion complete_task si se modifique el estado de la tarea y no solo devuelva true y finalmente tampoco se esta validando los parametros que se estan pasando al storage
- ¿Qué fallos típicos de integración (errores de comunicación, excepciones no controladas, estados inconsistentes) podrían pasar desapercibidos?
R:// podria pasar el estado inconsistente, debido a que add_task podria notificar sin guardar la informacion o viceversa, asi mismo los datos de storage podrian corromperse al tener datos incorrectos o vacios y finalmente uno de los mayores problemas es que la funcion add_task retorne True sin hacer ninguna funcion

## ⚠️ Parte 3 – El lado oscuro de las pruebas de integración

1. Abre src/service.py y localiza el método add_task.
2. Modifícalo para que siempre devuelva True sin llamar al almacenamiento ni al notificador.
3. Vuelve a ejecutar los tests de integración:

pytest tests/test_service_integration.py -v

4. Analiza el resultado.

Responde:

- ¿Los tests detectaron el error?
R:// No, los test no detectaron el error del codigo
- ¿Por qué siguen pasando?
R:// esto sigue pasando ya que la prueba solo verifica que se devuelva un valor true y al cambiar el codigo para que solo reciba true, este no se rompe ya que "cumple" y todas las pruebas aparecen como correctas a pesar que el codigo no se esta ejecutando correctamente
- ¿Qué debilidad fundamental tienen estas pruebas de integración?
R:// Que realmente dejan de ser pruebas ya que no verifican que el codigo funcione correctamente al no revisar que si se guarde correctamente la informacion y que la llamada al notifier se realice de manera correcta por ende no se verifica que el codigo cumpla la funcion para la que fue creada, porque tecnicamente no lo esta probando

## 🔧 Parte 4 – Aplicación de enfoques de integración

En esta parte utilizarás los notebooks y escribirás pruebas que implementen diferentes estrategias de integración.

### 4.1 Enfoque Top‑Down

- Usa un stub para storage y notifier y prueba la lógica de service.py de forma aislada.
- Escribe los tests en tests/test_service_integration.py (sección TestTopDown).

### 4.2 Enfoque Bottom‑Up

- Escribe un driver que pruebe directamente el módulo storage.py (sin pasar por service).
- Crea el archivo tests/test_storage_driver.py y escribe al menos 3 pruebas que verifiquen operaciones de lectura/escritura en el archivo JSON.

### 4.3 Enfoque Sandwich

- Combina stubs (para notifier) con el módulo real de storage y prueba el flujo completo de agregar una tarea desde service, verificando que el storage se actualiza correctamente.

## 🔧 Parte 5 – Mejora de las pruebas de integración

Refactoriza y amplía las pruebas para que:

- Detecten la modificación maliciosa de la Parte 3.
- Cubran escenarios de error:
  - Fallo en el almacenamiento (simula una excepción en storage.save).
  - Fallo en el notificador (simula que notifier.send lanza excepción).
  - Verifica que el sistema mantiene la consistencia (si falla la notificación, la tarea no debe quedar guardada a medias, o debe manejarse adecuadamente).
- Incluyan casos extremos:
  - Agregar una tarea con título vacío (debe ser rechazada).
  - Agregar tareas duplicadas.
  - Listar tareas cuando el archivo está vacío o no existe.

## 📊 Parte 6 – Reflexión sobre cobertura de integración

Utiliza el notebook notebooks/04_lado_oscuro.ipynb y responde:

- ¿Qué diferencia hay entre cobertura de código y cobertura de integración?
R:// La principal difetencia en que la cobertura de codigo mide que porcentaje de lineas se ejecutaron mendiante los test, encambio la cobertura de integracion evalua que los puntos de interaccion entre los modulos esten funcionando y siendo probados
- ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?
R:// porque este no verifica realmente que la conexion y funcionamiento enre modulos sea correcto, permitiendo que muchas pruebas engañosas pasen al no verificar correctanmente

## 🧠 Parte 7 – Reflexión final

Responde:

- ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
R:// aprendi que los test unitarios llegan a ser muy limitados ya que solo verifican un modulo aislado, en cambio los de integracion verifican y prueban la colaboracion de modulos, lo que hace que sea mas facil detectar muchos mas bugs
- ¿En qué situaciones usarías un enfoque bottom‑up y en cuáles top‑down?
R://usaria las pruebas bottom para poder probar modulos complejos y validar que funcionen correctamente, los Top-Down los usaria para probar el codigo sin tener que depender de modulos inferiores 
- ¿Cómo aplicarías stubs y drivers en un proyecto real para desacoplar dependencias externas?
R:// Los stubs los usaria para reemplazar el uso de servicios externos durante las pruebas, evitando costos adicionales y uso de apis

los drivers los usaria para validar modulos base sin la dependencia de datos o de modulos inferiores que aun no esten completos

