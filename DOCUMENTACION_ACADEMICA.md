# Documentación Académica — Cazador de Contraseñas
## Proyecto Integrador — Programación Orientada a Objetos
### Universidad Nacional Abierta y a Distancia (UNAD)

**Estudiante:** Camilo Andrés León Rubriche  
**Curso:** Programación — Cuarto semestre  
**Fecha de entrega:** Mayo 2026

---

## 1. Introducción

El desarrollo de software moderno exige algo más que escribir código que funcione. Exige construir soluciones organizadas, escalables y comprensibles para cualquier programador que las lea en el futuro. En ese contexto, la Programación Orientada a Objetos (POO) no es simplemente un paradigma académico, sino una forma de pensar que refleja la realidad en términos de entidades con comportamiento propio.

Este proyecto, denominado *Cazador de Contraseñas*, nació de la necesidad de integrar los conceptos fundamentales del curso en algo que no fuera un ejercicio aislado. Un videojuego casual ofrece el contexto perfecto: tiene reglas de negocio claras, entidades distintas con comportamiento propio, interacción del usuario, persistencia de datos y la necesidad de manejar errores de forma controlada.

El resultado es una aplicación de escritorio funcional que, además de ser un juego entretenido, sirve como referencia práctica de cómo se aplican herencia, polimorfismo, encapsulamiento, abstracción, excepciones personalizadas y arquitectura limpia en un proyecto real.

---

## 2. Objetivo General

Diseñar e implementar un juego interactivo de escritorio en Python que demuestre el dominio de la Programación Orientada a Objetos mediante una arquitectura limpia, manejo avanzado de excepciones e interfaz gráfica moderna.

---

## 3. Objetivos Específicos

1. Aplicar herencia y polimorfismo en la jerarquía de cofres del juego para demostrar la reutilización de código y el comportamiento diferenciado por subtipo.

2. Implementar encapsulamiento efectivo en las clases `Contrasena` y `Jugador` para proteger el estado interno y garantizar la integridad de los datos.

3. Crear una jerarquía de excepciones personalizadas que permita manejar errores del dominio con granularidad y mensajes informativos para el usuario.

4. Construir una interfaz gráfica profesional con CustomTkinter que separe completamente la capa de presentación de la lógica de negocio.

5. Implementar persistencia de datos en formato JSON para el ranking y el historial, garantizando que la información sobreviva entre sesiones.

6. Organizar el proyecto en módulos especializados que respeten el Principio de Responsabilidad Única (SRP).

---

## 4. Justificación Técnica

### ¿Por qué Python?
Python 3.12 ofrece soporte maduro para POO con tipado estático opcional (`type hints`), clases abstractas (`abc`), tipos valor inmutables (`dataclasses`, `NamedTuple`) y una librería estándar completa para aleatoriedad y persistencia. Su sintaxis limpia facilita que el código comunique la intención del programador sin ruido sintáctico.

### ¿Por qué CustomTkinter?
La interfaz de usuario es el punto de contacto con el jugador. Tkinter estándar tiene un aspecto anticuado; CustomTkinter resuelve ese problema con widgets modernos, soporte nativo de tema oscuro y bordes redondeados, sin requerir dependencias externas complejas. Para un proyecto educativo, el equilibrio entre facilidad de aprendizaje y resultado visual es ideal.

### ¿Por qué arquitectura en capas?
Un proyecto monolítico (todo en un archivo) escala mal y es difícil de mantener. Separar en capas (modelos, vistas, controladores, servicios) permite modificar la interfaz gráfica sin tocar la lógica del juego, cambiar el sistema de persistencia sin afectar la UI, y testear el dominio de forma aislada.

---

## 5. Programación Orientada a Objetos

La POO modela el mundo como un conjunto de objetos que tienen estado (atributos) y comportamiento (métodos). En lugar de escribir procedimientos sueltos, agrupamos datos y funciones relacionadas en clases. Esto produce código más organizado, reutilizable y fácil de razonar.

En este proyecto cada entidad del juego tiene su propia clase:
- `Contrasena` sabe generarse y validarse.
- `CofreBase` y sus subclases saben abrirse y mostrar su resultado.
- `Jugador` lleva la cuenta de la sesión y desbloquea logros.
- `JuegoControlador` orquesta las interacciones entre todos.

---

## 6. Herencia

La herencia permite crear nuevas clases basadas en una existente, reutilizando su estructura y especializing su comportamiento.

```python
class CofreBase(ABC):          # Clase padre abstracta
    nombre: str
    puntos_base: int
    
    @abstractmethod
    def abrir(self) -> ResultadoApertura: ...

class CofreComun(CofreBase):   # Hereda estructura
    nombre = "Cofre Común"
    puntos_base = 10
    
    def abrir(self) -> ResultadoApertura:
        # Implementación específica del cofre común
        ...

class CofreLegendario(CofreBase):   # Misma herencia, diferente comportamiento
    nombre = "Cofre Legendario"
    puntos_base = 50
    
    def abrir(self) -> ResultadoApertura:
        # Puede otorgar el doble con 20% de probabilidad
        ...
```

La jerarquía evita duplicar código: los métodos comunes (como `puntos_finales()` que aplica el multiplicador) se definen una sola vez en `CofreBase` y los cuatro tipos de cofre los heredan automáticamente.

---

## 7. Polimorfismo

El polimorfismo permite que objetos de diferentes clases respondan al mismo mensaje (llamada a método) de formas distintas. El código que llama al método no necesita saber con qué subtipo está trabajando.

```python
# El controlador NO sabe si el cofre es común, raro, legendario o maldito.
# Sólo sabe que tiene un método abrir().
cofre: CofreBase = FabricaCofre.crear(probabilidades, multiplicador)
resultado = cofre.abrir()     # ← polimorfismo en acción

# Cada subclase responde diferente:
# - CofreComun.abrir()      → +10 puntos, mensajes modestos
# - CofreLegendario.abrir() → +50 puntos, posible ×2
# - CofreMaldito.abrir()    → -20 puntos, mensajes de penalización
```

El beneficio es extensibilidad: si mañana añadimos `CofreeEpico`, sólo creamos la clase y la registramos en `FabricaCofre`. El resto del sistema funciona sin cambios.

---

## 8. Manejo de Excepciones

Las excepciones del dominio heredan de `ErrorJuego`, que hereda de `Exception`. Esta jerarquía permite capturar con granularidad:

```python
# En el controlador: try/except/else/finally completo
try:
    contrasena.lanzar_si_invalida()          # puede lanzar
    cofre = FabricaCofre.crear(probs, mult)  # puede lanzar
    apertura = cofre.abrir()

except ContrasenaInvalidaError as e:
    # Contraseña inválida → cofre maldito como penalización
    apertura = CofreMaldito().abrir()

except CaracterRepetidoError as e:
    # Error específico: mostrar qué carácter se repitió
    apertura = CofreMaldito().abrir()

else:
    # Sólo si NO hubo excepción: reproducir sonido de éxito
    self._reproducir_sonido_cofre(apertura.rareza)

finally:
    # Siempre: logging, limpieza de recursos temporales
    pass
```

**Por qué `else`:** El bloque `else` es una forma idiomática de Python para separar el «camino feliz» del manejo de errores. El código en `else` no corre si hubo excepción, lo cual es más explícito que un flag booleano.

**Por qué `finally`:** `finally` garantiza que el código de limpieza corre siempre, incluso si hay un `return` dentro del `try`. En producción, aquí iría el cierre de conexiones o el volcado de logs.

---

## 9. Modularidad

El proyecto está dividido en módulos con responsabilidades únicas:

| Módulo | Responsabilidad |
|---|---|
| `modelos/` | Lógica de dominio pura. No conoce la UI ni la persistencia. |
| `vistas/` | Presentación y eventos de usuario. No conoce el dominio. |
| `controladores/` | Coordinación. Conecta vistas y modelos. |
| `servicios/` | Infraestructura: archivos, sonido. |
| `excepciones/` | Contrato de errores del dominio. |
| `utils/` | Herramientas sin dependencias del dominio. |

Esta organización cumple el **Principio de Responsabilidad Única**: cada módulo tiene una sola razón para cambiar. Si el formato del ranking cambia, sólo se modifica `ranking_service.py`. Si el diseño de la UI cambia, sólo se modifica la capa `vistas/`.

---

## 10. CustomTkinter

CustomTkinter es una extensión de tkinter que añade widgets con diseño moderno. Sus características clave usadas en este proyecto:

- **CTkFrame**: contenedor con bordes redondeados y color de fondo configurable.
- **CTkLabel**: texto con fuente, color y tamaño precisos.
- **CTkEntry**: campo de entrada estilizado.
- **CTkButton**: botón con hover color y corner_radius.
- **CTkProgressBar**: barra de progreso animable programáticamente.
- **CTkScrollableFrame**: frame con scroll automático para el historial.
- **CTkToplevel**: ventana secundaria modal para ranking y logros.
- **CTkRadioButton**: selector de dificultad.

El tema oscuro se activa globalmente con:
```python
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
```

Las animaciones (parpadeo, fade de texto, movimiento de barra) se implementan con el scheduler `widget.after(ms, callback)` de tkinter, que agenda callbacks en el hilo de UI sin bloquear la ventana.

---

## 11. Conclusiones

1. **La POO no es sólo sintaxis.** Aplicarla correctamente requiere pensar en términos de responsabilidades, contratos e interacciones. Este proyecto evidencia que una buena distribución de responsabilidades produce código más fácil de entender, modificar y escalar.

2. **La herencia tiene valor real cuando existe una relación «es-un» genuina.** Los cuatro tipos de cofre *son* cofres: tienen el mismo contrato pero comportamientos distintos. Eso hace que la herencia aquí sea apropiada y no forzada.

3. **Las excepciones personalizadas mejoran la experiencia de desarrollo.** Un mensaje como "Longitud 5 fuera de rango [8–64]" es infinitamente más útil que un `ValueError: invalid literal` genérico. Diseñar excepciones descriptivas es una inversión pequeña con retorno alto.

4. **Separar la UI de la lógica de negocio no es burocracia: es libertad.** Durante el desarrollo de este proyecto, la interfaz cambió varias veces sin tocar una sola línea de los modelos.

5. **Python tiene herramientas para arquitectura seria.** `abc`, `dataclasses`, `NamedTuple`, `type hints`, `pathlib`: estas no son características de nicho, son el vocabulario de un código profesional.

---

## 12. Referencias APA 7

Lutz, M. (2013). *Learning Python* (5th ed.). O'Reilly Media.

Ramalho, L. (2022). *Fluent Python: Clear, Concise, and Effective Programming* (2nd ed.). O'Reilly Media.

Martin, R. C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

CustomTkinter. (2023). *CustomTkinter — Modern and customizable python UI-library*. GitHub. https://github.com/TomSchimansky/CustomTkinter

Python Software Foundation. (2024). *The Python Standard Library*. https://docs.python.org/3/library/

Van Rossum, G., Warsaw, B., & Coghlan, N. (2001). *PEP 8 – Style Guide for Python Code*. https://peps.python.org/pep-0008/

Alchin, M. (2010). *Pro Python*. Apress.

---

---

*Documento elaborado por **Camilo Andrés León Rubriche** como proyecto integrador de la asignatura Programación — Cuarto semestre — UNAD — Mayo 2026.*
