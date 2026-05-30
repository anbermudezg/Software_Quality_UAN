# Informe – Taller de Pruebas de Integración

**Grupo:** velásquez – caminos  
**Rama:** `grupo_velasquez_caminos`  
**Integrantes:** Yorman David Velasquez Muños  | Laura Dayan Caminos Mora

---

## Parte 2 – Análisis crítico

### ¿Las pruebas verifican la colaboración entre módulos?

No. Las pruebas originales solo comprobaban `assert result is True` sin comprobar que los modulos de almacenamiento y notificacion fueran usados realmente.

### Interacciones no validadas

- Comunicación entre TaskService y TaskStorage
- Comunicación entre TaskService y Notifier
- Persistencia real de los datos
- Manejo de erorres durante el almacenamiento
- Manejo de errores durante el envio de notificaciones 

### Fallos que pasaban desapercibidos

- `add_task` que devuelve `True` sin usar storage ni notifier 
- Fallo aleatorio del notifier 
- Se guarda aunque falle la notificación
- Validaciones incorrectas de titulos o duplicados


---

## Parte 3 – Lado Oscuro

### ¿Las pruebas detectaron el error?
 Si, al modificar add_task() para que devolviera siempre TRUe, las 14 pruebas fallaron 

 ### ¿Por qué siguen pasando?
Las pruebas fallaron no ya que no solo verifican el valor del retorno. Estan comprobando que las tareas se guarden correctamente, que envien notificaciones, validen titulos vacios, duplicados y que manejen los errores adecuadamente. al reemplazar el Return True dejaron de cumplirse y los test detectaron el problema.

 ### ¿Qué debilidad fundamental tienen estas pruebas de integración?
Las pruebas originales solo estabn verificando el resultado final, no las interacciones entre módulos. Una implementación incorrecta podia aparentar funcionar aunque no realizara realmene las operaciones de almacenamiento o notificación. Las pruebas mejoradas eliminan esta debilidad al validar la colaboración entre los compone tes del sistema.

---

## Parte 4 – Enfoques aplicados

| Enfoque | Implementación |
|---------|----------------|
| **Top-Down** | `TestTopDown` con `StorageStub` y `NotifierStub` |
| **Bottom-Up** | `StorageDriver` en `test_storage_driver.py` (4 pruebas) |
| **Sandwich** | `TestSandwich`: `TaskStorage` real + `NotifierStub` |
| **Big-Bang** | Tests iniciales (débiles, todo conectado sin aserciones de integración) |

---

## Parte 5 – Decisiones de diseño

- Título Vacio: Se rechaza y retorna FALSE
- Tareas Duplicadas: No se guardan ni se notifican
- Fallo Storage: Se cancela la operación y retorna FALSE
- Fallo Notifier: Se revierten los cambios para mantener la consistencia
- Errores: Se manejan para evitar estados inconsistentes

---

## Parte 6 – Cobertura de código vs integración

### ¿Qué diferencia hay entre cobertura de código (líneas ejecutadas) y cobertura de integración?
- Código: líneas ejecutadas; puede ser 100 % con mocks que no reflejan comportamiento real.
- Integración: Contratos entre módulos (datos persistidos, orden, errores, estado compartido).

### Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?
Un 100 % unitario no garantiza el sistema integrado porque cada módulo puede estar bien aislado pero mal ensamblado (parámetros, orden, excepciones no propagadas).

### Señales de tests insuficientes:
Pasan con `add_task` saboteado; no hay aserciones sobre disco o llamadas; dependencias aleatorias sin control.

---

## Parte 7 – Reflexión final

### ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
Las pruebas unitarias validan la logica de cada modulo de forma aislada, pero no garantizan que los componentes colaboren correctamente. Las pruebas de intergracion permiten detectar errores en la comunicacion entre modulos, el manejo de excepciones y la consistencias de los datos

### ¿En qué situaciones reales usarías un enfoque bottom‑up y en cuáles top‑down? Justifica con base en la arquitectura del sistema.
- Bottom-up lo usaria para validar priemro componentes de bajo nivel como almacenamiento o acceso de datos. 
- Top-Down lo utilizaria para probar la logica principal del sistema utilizando stubs para simular dependencias.

### ¿Cómo aplicarías stubs y drivers en un proyecto con microservicios o con bases de datos externas? 
- Stubs para simular servicios externos como aPIs o sistemas de notificacion.
- Drivers para probar componentes de bajo nivel de forma independiente antes de integrarlos con el resto del sistema.