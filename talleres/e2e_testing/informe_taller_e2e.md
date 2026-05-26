# Informe Taller de Pruebas E2E

**Autora:** Virginia Raga
**Fecha:** 26/05/2026

---

## Parte 2 — Analisis de las pruebas iniciales

### Las pruebas iniciales verifican algo util?

Honestamente, poco. Las pruebas originales se limitaban a ejecutar acciones y verificar
que no explotara nada, pero eso no es suficiente. Es como ir al medico, que te tome
la presion y diga "no te moriste, estas bien". Tecnicamente correcto, pero no muy util.

El problema concreto: creaban una tarea y nunca comprobaban que apareciera en pantalla.
Si la app guardaba la tarea internamente pero fallaba al mostrarla, el test igual pasaba.
Y es que un test que siempre pasa sin importar lo que pase... no esta haciendo su trabajo.

### Interacciones no cubiertas

Habia bastantes huecos. Las pruebas iniciales no verificaban que el titulo apareciera
en la lista despues de crearlo, ni que el badge de "completada" apareciera al marcar
una tarea, ni que el tachado del titulo funcionara visualmente. Tampoco cubrian flujos
combinados como crear, completar y luego eliminar en secuencia, ni casos limites
como intentar crear una tarea con titulo vacio o con un nombre repetido.

En resumen: probaban que el sistema respiraba, no que caminara.

---

## Parte 3 — Sabotaje

### Las pruebas iniciales detectan la modificacion maliciosa?

No, y eso es justamente lo preocupante. Si alguien modifica la app para que guarde
las tareas en la base de datos pero no las muestre en pantalla, las pruebas originales
seguirian pasando sin problema. Porque nunca verificaron que algo apareciera ante los
ojos del usuario.

### Debilidad fundamental

La verdad es que este experimento expone algo bastante basico pero que se olvida con
frecuencia: una prueba sin aserciones sobre el estado visible no es una prueba real,
es una ilusion de seguridad. Peor aun, puede generar una falsa confianza: el equipo
cree que todo funciona porque los tests estan en verde, pero el usuario ve una pantalla
rota. Las nuevas pruebas, en cambio, verifican exactamente lo que veria una persona
usando la app: que el titulo aparece, que el badge sale, que la tarea desaparece.

---

## Parte 7 — Reflexion E2E

### Que es un flaky test?

Un flaky test es ese test traicionero que a veces pasa y a veces falla, sin que nadie
haya tocado el codigo. Es frustrante porque no puedes confiar en el: cuando falla,
no sabes si es un bug real o simplemente mala suerte.

El ejemplo mas clasico es usar time.sleep(2) para esperar a que cargue un elemento.
En tu maquina rapida funciona siempre. En el servidor de CI lento, falla una de cada
tres veces. La solucion, como hicimos aqui, es usar expect().to_be_visible(), que
espera activamente hasta que el elemento aparezca o se agote el tiempo. Nada de
adivinar cuantos segundos necesita la app.

### Como garantizar aislamiento entre pruebas E2E?

En este proyecto el conftest.py resuelve esto de forma elegante: antes de cada prueba
llama al endpoint /tasks/clear, dejando la lista completamente vacia. Asi cada test
empieza desde cero, sin heredar tareas de pruebas anteriores. Ademas, cada prueba
crea sus propios datos desde el principio. El resultado es que si un test falla, no
arrastra a los demas consigo.

### Cuando preferir una prueba de integracion sobre una E2E?

Cuando quiero verificar logica interna sin el costo de levantar un navegador entero.
Esta suite tarda unos 65 segundos en correr 18 pruebas, lo cual esta bien, pero
imagina tener 500 pruebas E2E. Se vuelve insostenible.

Para verificar, por ejemplo, que el modelo no permite titulos duplicados, una prueba
de integracion que llame directamente a la funcion es diez veces mas rapida y igual
de precisa. Las E2E las reservaria para los flujos criticos que el usuario realmente
recorre: crear, completar, eliminar. Lo que importa desde afuera.

### Como aplicar Playwright en un proyecto con microservicios?

La clave es no intentar probar cada microservicio con Playwright, eso seria un error.
Lo que tiene sentido es levantar un entorno completo con Docker Compose y usar
Playwright para probar los flujos de negocio desde la perspectiva del usuario final,
sin importar cuantos servicios esten detras.

Por ejemplo, en un e-commerce: el test E2E verifica que el usuario puede agregar un
producto al carrito, pagar y recibir confirmacion. No le importa si eso involucra
tres microservicios distintos. Cada uno de esos servicios tendra sus propias pruebas
unitarias y de integracion. Playwright cubre la capa que ninguna otra prueba puede
cubrir: la experiencia real del usuario.
