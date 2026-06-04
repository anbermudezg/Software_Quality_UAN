## 🔍 Parte 2 – Análisis crítico de las pruebas

- ¿Las pruebas actuales verifican realmente que los módulos colaboran correctamente?
- Rta: Las pruebas solo valida un camino en el que todo este correcto y no verifican la colaboracion entre los modulos cuando sucede un error

- ¿Qué interacciones entre módulos **no** están siendo validadas?
- Rta: No se verifica si en test_complete_task se guardan los datos correctamente, no se prueba si TaskService maneje correctamente una exepcion de notifier.Send()
  no se comprueba la interacion si se envian datos invalidos

- ¿Qué fallos típicos de integración (errores de comunicación, excepciones no controladas, estados inconsistentes) podrían pasar desapercibidos?
- Rta: Efecto corateral: en TaskService.add_task, si el metodo self_notifier.send() lanza una exepcion, la tarea se guarda en el storage
  el servicio no captura la exepcion, lo que causa que el usuario resibe el error pero el JSON queda modificado

  Crashes en cascada: si Notifier lanza una exepcion el backend tendra un fallo critico debido a que add_task no tiene un bloque de try/except


---

## ⚠️ Parte 3 – El lado oscuro de las pruebas de integración

- ¿Las pruebas detectaron el error?
- Rta: las pruebas no dectectaron ningun error 

- ¿Por qué siguen pasando?
- Rta: test_add_task_happy_path sigue pasando debido solo pruebas si add_task retorna true, pero el test ingnora como obtuvo el retorno 

- complete_task sigue pasando debido a una falta de limpieza de los archivos del entorno los archivos JSON que ya tienen los resultados de las pruebas 
  anteriormente realizadas. complete_task leyo los resultados viejos y la marco como completada y devolvio true

- ¿Qué debilidad fundamental tienen estas pruebas de integración?
- Rta: las pruebas solo comprueban el valor de retorno no verifican que los componentes integrados tengan un cambio real

- no limpiar los archivos JSON que contienen resultados de pruebas viejas lo que ocaciona que los test confien en estos archivos haya falsos positivos 

---

## 📊 Parte 6 – Reflexión sobre cobertura de integración

- ¿Qué diferencia hay entre cobertura de código (líneas ejecutadas) y cobertura de integración?
- Rta: La cobertura de codigo solo mide que porcentaje de lineas de codigo fueron ejecutadas mientras que se corren los test 
- mientras la coberturta de integracion es una prueba cualitativa, mide la comunicacion entre diferentes modulos, se enfoca
  principalmente en los contratos de datos, los flujos de exepciones compartidas y el comportamiento del sistema ante un fallo
  de una de sus dependencias

- ¿Por qué un 100% de cobertura unitaria no garantiza que el sistema integrado funcione correctamente?
- Rta: como en el experimento del "impostor" el 100% de cobertura unitaria da una ilucion de seguridad debido a que los componentes 
  no estan aislados usualmente sus dependencias son moks perfectos, pero estos no reflejan un esenario en produccion real

- ¿Qué métricas o señales te indicarían que unas pruebas de integración son insuficientes?
- Rta: pruebas solo basadas en caminos felices y cuenta con pruebas que fuerzen un fallo para ver si el sistema es tolerante a fallos 
  si la mayoria de la pruebas terminan validando solo que devuelva un boleano sin revisar efectos colaterales 

---

## 🧠 Parte 7 – Reflexión final

- ¿Qué aprendiste sobre las limitaciones de las pruebas unitarias frente a las de integración?
- Rta: las pruebas unitarias son exelentes para validar la correccion matematica y en algunos casos la logica, pero se asume que el resto de
  del sistema funciona de manera perfecta. algunos componentes pueden pasar sus pruebas usando un mock que simula otro modulo, pero si el modulo 
  real cambia su comportamiento el sistema colapsara.

- ¿En qué situaciones reales usarías un enfoque bottom‑up y en cuáles top‑down? Justifica con base en la arquitectura del sistema.
- Rta: bottom-up se usa cuando la arquitectura del sistema criticamente de modulos de infrastructura pesada, algoritmos complejos,
  sistemas de archivos o drivers de hardware 

  top-down se usan en las etapas de tempranas del proyecto, en arquitecturas orientadas a servicios permitiendo validear las reglas de negocio
  y la experiencia del usuario

---