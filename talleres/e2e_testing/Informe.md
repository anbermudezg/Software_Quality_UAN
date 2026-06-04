---

## 🔍 Parte 2 — Análisis crítico de las pruebas

- ¿Las pruebas actuales verifican que las tareas se crean correctamente?
- Rta: Los test solo verifican que al crear una tarea no lancé una exepcion al hacer click en agregar, pero no verifica si la tarea quedo guardada 

- ¿Qué acciones del usuario no están siendo validadas?
- Rta: No se verifica que sucede si un usuario ingresa una tarea duplicada o con el titulo vacio, no se verifica si la tarea recien creada 
- aparece en la lista de tareas activas, no se verifica que tras acompletar una tarea el estilo cambie, no se verifica si al recargar la pagina 
  los datos se mantienen

- ¿Qué fallos críticos de la UI podrían pasar desapercibidos?
- Rta: si el titulo no se renderiza de manera correcta la prueba seguira pasando debido a que no verifica el contenido del titulo
- si al completar una tarea no queda marcada como completada seguira pasando los test debido a que no se verifica el estado de la tarea
  
---

---

## ⚠️ Parte 3 — El lado oscuro de las pruebas E2E

3. Analiza el resultado.

Responde:
- ¿Los tests detectaron el error?
- Rta: lo test actuales no dectan el error

- ¿Por qué siguen pasando?
- Rta: el test solo verifica que la solicitud se envie y que el servidor responda en este caso el servidor solo responde con el codigo 302, 
  el test nunca consulta si el archivo JSON si contiene los datos de "mi tarea"

- ¿Qué debilidad fundamental tienen estas pruebas E2E?
- Rta: estas pruebas solo prueban el camino feliz es decir que es lop que pasa si el usuario hace todo correctamente, Los test so verifican 
  que el la comunicacion con el servidor no falle pero ignora lo requisitos funcionales

---

## 📊 Parte 7 — Reflexión sobre pruebas E2E en CI/CD

Usando el notebook `notebooks/04_lado_oscuro_e2e.ipynb`, responde:

- ¿Qué son los flaky tests y por qué son especialmente comunes en E2E?
- Rta: los flaky test son pruebas con resultados inconsistentes es decir que pasan un test y a asu vez fallan el mismo test sin que se haya hecho ningun 
  cambio en el codigo son cumunes debiado a que en ocaciones el test intenta acceder o interactuar con un elemento antes que el navegador lo haya 
  terminado de procesar

- ¿Cómo garantizarías el aislamiento entre tests en una suite E2E?
- Rta: usar fixtures que ejecuten una limpieza entes de que cada test comience asegurando que no existan interferencias con otros test ejecutados anteriormente
  levantar una instancia efimera de la base de datos o del servidor para cada ejecución de la suite garantizando que el entorno esté limpio desde el inicio.

- ¿En qué casos usarías E2E en lugar de pruebas de integración?
- Rta: En ningun caso se deberia remplazar las pruebas de integracion con E2E. la pruebas de integracion comprueban la comunicacion entre partes o modulos y las E2E 
  valida la funcionalidad completa desde la perspectiva del usuario

---