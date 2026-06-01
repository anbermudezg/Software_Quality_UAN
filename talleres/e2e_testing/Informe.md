Parte 2 y 3 -- Analisis y Sabotage
**¿Las pruebas iniciales verificaban algo útil?**
*No eran lo suficientemente útiles, solo verificaban que la página cargara (status 200), pero no validaban si el contenido (las tareas) estaban 
en la interfaz de usuario. 
**¿Las pruebas iniciales detectaron la modificación maliciosa (Sabotaje)?**
*No, cuando comentamos la linea get_repo().add(title), las pruebas iniciales seguían pasando porque el servidor respondía correctamente, auqneu la tarea nunca se guardaba. 
**¿Que debilidad fundamental expone este experimento?**
*Expone que las pruebas E2E debiles (que solo verifican estados de HTTP) no garantizan que el sistema funcione. Una prueba E2E real debe verificar el estado de la UI 
Parte 7 // Reflexion 
**¿Que es flaky test?**
*Es un test que a veces pasa y otras veces falla sin que haya cambiado el codigo. Por ejemplo, un test que falla porque el internet se puso lento y el boton no aparecio en 1 segundo, pero en el segundo intento si funciona
**¿Como garantizaria un aislamiento entre test E2E?**
*Usando un endpoint de limpieza antes de cada test para asegurar que la base de datos este vacia y un test no dependa de lo que hizo el anterior
**¿Cuando preferiria una prueba de integrafcion sobre una E2E?**
*Cuando se necesite probar la logica entre la base de datos y la API sin necesidad de abrir un navegador, ya que las de integracion son mucho mas rapidas
**¿Como aplicaria PlayWright en un proyecdto con microservicios?**
*Configuraria un entorno de Staging donde todos los microservicios esten corriendo y usaria Playwright para simular el viaje completo del usuario a traves de todos los servicios desde la interfaz principal. 