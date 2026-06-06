# Reflexión Técnica - Taller de Pruebas de Integración

**Nombres:** 
Julian Santiago Gonzalez Becerra
Cod: 13572323365
Nicol Danna Ximena Cifuentes Zabala
Cod: 13572324939
Santiago Castañeda Garcia
Cod: 13572326957
**Fecha:** 28/05/2026

---

## Parte 2 – Análisis crítico de las pruebas

### ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?

No lo hacen. Las pruebas iniciales solo revisaban si `add_task` retornaba `True`, pero no verificaban si la tarea se guardó en el storage ni si el notifier recibió la notificación. Esto es un problema porque el código puede no ejecutarse propiamente y las pruebas seguir pasando.

### ¿Qué interacciones entre módulos no están siendo validadas?

- No se verifica explícitamente que `storage.save()` se llame con los datos correctos
- No se comprueba que `notifier.send()` reciba el mensaje esperado  
- No se valida el estado del storage después de la operación
- El archivo JSON no se inspecciona para confirmar persistencia real

### ¿Qué fallos típicos de integración podrían pasar desapercibidos?

- Fallos aleatorios del notifier (10% de probabilidad)
- Estados inconsistentes cuando la tarea se guarda pero falla la notificación
- Títulos vacíos que el sistema acepta sin validación
- Duplicados que no se detectan correctamente

---

## Parte 3 – Resultados del sabotaje

Cuando modifiqué `add_task()` para solo retornar `True` sin usar storage ni notifier:

**¿Las pruebas detectaron el error?**  
Sí. Con los tests nuevos fallaron 10 tests, demostrando que detectan el problema.

**¿Por qué las pruebas iniciales no lo detectaban?**  
Porque las aserciones solo revisaban el valor de retorno. Sin verificar interacciones ni estado, el impostor pasaba desapercibido.

**Debilidad fundamental:**  
No validan el estado del sistema ni las interacciones entre componentes. Esto genera falsa confianza.

---

## Enfoques de integración aplicados

### Top-Down
Usamos stubs para Storage y Notifier. Las pruebas verifican que el Service invoque correctamente a sus dependencias con los parámetros esperados.

### Bottom-Up  
Creamos tests aislados para TaskStorage usando tempfile como driver. Se cubrieron: archivo inexistente, guardar/recuperar, múltiples tareas, título vacío.

### Sandwich
Combinamos Storage real con StubNotifier (y viceversa). Así validamos la persistencia real mientras controlo el comportamiento del notifier.

---

## Parte 6 – Reflexión sobre cobertura de integración

### ¿Qué diferencia hay entre cobertura de código y cobertura de integración?

- **Cobertura de código:** Dice qué líneas se ejecutaron. Ejemplo: si `add_task` retorna `True`, la línea se "cuenta" como ejecutada aunque no haya guardado nada.

- **Cobertura de integración:** Dice si los módulos interactúan correctamente. Verifica que los datos fluyan entre componentes y que las llamadas ocurren como se espera.

### ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione?

Porque las líneas pueden ejecutarse sin que las interacciones sean correctas. En el taller vimos que el impostor (que no llama a storage) podía pasar las pruebas si solo revisamos el valor de retorno.

### Señales de que las pruebas de integración son insuficientes

- Tests que solo verifican valores de retorno
- No hay inyección de fallos en dependencias
- No se verifica que los stubs reciban llamadas correctas
- Estado compartido entre tests (archivos sin limpiar)

---

## Parte 7 – Reflexión final

### Limitaciones de pruebas unitarias vs integración

Las pruebas unitarias verifican cada módulo por separado, pero el problema real está en cómo interactúan. Un test de storage puede pasar mientras que `add_task` no llama al storage correctamente. Necesitamos pruebas que validen las colaboraciones entre módulos.

### Cuándo usar bottom-up vs top-down

- **Bottom-up:** Cuando los módulos de bajo nivel (storage, base de datos) están listos y confiables. Probamos desde ahí hacia arriba. Ideal para sistemas donde la capa de datos es compleja y estable.

- **Top-down:** Cuando quiero probar la lógica de negocio antes que las dependencias externas estén listas. Usando stubs podemos validar el Service sin esperar a que storage o notifier estén terminados.

### Aplicación de stubs y drivers en proyectos reales

- **Stubs para APIs externas:** En lugar de llamar un servicio HTTP real, creamos un stub que devuelva respuestas predefinidas. Así pruebo tanto escenarios exitosos como errores sin depender de servicios externos.

- **Drivers para bases de datos:** Script que inicializa la BD de test con datos limpios, ejecuta las pruebas, y luego limpia. Cada test tiene un entorno aislado.

- **Ejemplo práctico:** Para Stripe, usaría un stub que devuelva "pago exitoso" para happy path, y otro que lance `CardError` para pruebas de error. El driver prepararía órdenes de prueba en la base de datos.