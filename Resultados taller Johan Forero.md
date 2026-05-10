# Software Quality UAN — Evidencias del Taller
## Johan Nicolas Forero Giral

## Parte 2 – Análisis crítico de las pruebas

**1. ¿Las pruebas actuales garantizan que el código es correcto?**

No. Aunque en consola aparece que las pruebas funcionaron correctamente, al revisar más a fondo los archivos se notan varios problemas:

- `test_estadistica` solo valida que la respuesta sea `float`, no que el valor sea correcto
- `test_analizador` prueba en realidad el archivo `ordenar.py`, y aún así lo prueba mal porque ingresa la lista ya ordenada
- `test_ordenador` prueba el analizador de texto y siempre responde `True`, por lo cual no está testeando nada real

**2. ¿Qué aspectos del comportamiento NO están siendo validados?**

Prácticamente ninguno:

- `test_analizador` prueba el módulo incorrecto (`ordenar.py`) y no realiza tests apropiados
- `test_estadistica` solo revisa que el valor final sea `float`, no que el programa funcione correctamente
- `test_ordenador` prueba `analizar.py` y siempre devuelve `True`, por lo que siempre pasa sin probar nada real

**3. ¿Qué tipo de errores podrían pasar desapercibidos?**

Prácticamente todos, ya que realmente no se están realizando las pruebas.

---

## Parte 3 – El lado oscuro de las pruebas

**1. ¿Las pruebas detectaron el error?**

No. Los resultados marcan que pasó todas las pruebas correctamente.

**2. ¿Por qué siguen pasando?**

Al revisar `test_estadistica.py` se puede observar que la función solo verifica que el resultado sea de tipo `float`. Sin importar si la respuesta es realmente el promedio, el test pasa.

**3. ¿Qué debilidad tienen estos tests?**

Ninguno de los tests valida que el resultado del programa sea correcto. La debilidad central es que nunca se verifica que el código funcione como se espera.

---

## Parte 6 – Reflexión sobre cobertura

**1. ¿Qué diferencia hay entre cobertura y calidad de pruebas?**

La diferencia radica en que:

- **Cobertura** mide cuántas ramas del proyecto se cubren
- **Calidad** mide qué tan bien se realizan las pruebas

Como se evidenció en el taller, una cosa es pasar las pruebas y otra es que los resultados sean correctos para el comportamiento requerido.

**2. ¿Por qué 100% de coverage no garantiza corrección?**

El coverage solo verifica que se use la totalidad de las ramas del código, no que los resultados sean correctos. Por ejemplo:

```python
# La función debe sumar, pero multiplica
2 + 2 = 4  # resultado esperado
2 * 2 = 4  # el test pasa, el coverage está al 100%, pero el código es incorrecto
```

Aunque se cubra el 100% de las ramas, si la lógica interna es incorrecta el error no será detectado.