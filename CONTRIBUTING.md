# Contributing guidelines

¡Gracias por tu interés en contribuir!. Este proyecto es open source y todas las contribuciones son bienvenidas.

---

## Requisitos generales

Antes de contribuir, asegúrate de tener el entorno correctamente configurado.
Este proyecto utiliza **Python**, **Poetry** y **Playwright**.

1. **Haz un fork** del repositorio y crea una rama para tu cambio:
   ```bash
   git checkout -b fix/nombre-del-cambio
   ```

2. Asegúrate de que tu código siga las buenas prácticas de **legibilidad y simplicidad**.
   Evita dependencias innecesarias y prioriza el código limpio.

3. Si agregas una nueva funcionalidad, explica brevemente su propósito en la descripción del PR.

---

## Commits semánticos

Usamos el formato de **commits semánticos**, lo que ayuda a mantener un historial claro y automatizable.

Estructura básica:

```console
<tipo>(opcional: alcance): <descripción corta>

opcional: <cuerpo del mensaje>
```

### Tipos comunes:

* **feat** → Nueva funcionalidad
* **fix** → Corrección de errores
* **refactor** → Mejora interna del código (sin cambiar comportamiento)
* **docs** → Cambios en documentación
* **style** → Formato o estilo del código (sin cambiar lógica)
* **test** → Nuevas pruebas o mejoras en las existentes
* **chore** → Mantenimiento general (scripts, dependencias, CI, etc.)

**Ejemplos:**

```bash
feat(cli): add support for multiple URLs
fix(parser): handle empty responses gracefully
docs(readme): update usage examples
```

> [!IMPORTANT]
> Para más información sobre el formato de commits semánticos, consulta [conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0).

---

## Pull Requests

* Envía un **PR por cada cambio lógico o funcional** (no combines varios temas en una sola PR).
* Describe claramente **qué problema soluciona o qué mejora introduce**.
* Si tu cambio incluye una nueva dependencia o modifica el comportamiento, menciónalo en la descripción.
* Asegúrate de que la rama esté actualizada con `master` antes de enviar el PR.

---

## Código y estilo

* Mantén el código **consistente y simple**.
* Usa nombres descriptivos para funciones, variables y archivos.
* Formatea el código con **ruff**:

  ```bash
  ruff format .
  ```
* Valida el código con **mypy**:

  ```bash
  mypy .
  ```
* Si tienes dudas, consulta el estilo existente en el código fuente.

---

## Buenas prácticas

* Antes de enviar una PR, prueba tu cambio localmente.
* Si agregas una nueva funcionalidad, considera actualizar el `README` o dejar un ejemplo en el PR.
* Si corriges un bug, explica el comportamiento anterior y el nuevo.

---

## Hacktoberfest 🎃

Durante Hacktoberfest, las PR válidas pueden recibir la etiqueta `hacktoberfest-accepted`.
Por favor, evita PR triviales o cambios sin propósito.

---

¡Gracias por contribuir y ayudar a mejorar este proyecto! 🙌
