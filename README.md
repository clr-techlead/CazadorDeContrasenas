🌐 English | [Versión en español](README.es.md)

# 🔑 Password Hunter (Cazador de Contraseñas)

![Tests](https://github.com/clr-techlead/CazadorDeContrasenas/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

**Author:** Camilo Andrés León Rubriche
**Institution:** Universidad Nacional Abierta y a Distancia — UNAD
**Course:** Programming — Fourth Semester
**Version:** 1.0.0

An educational Python desktop game that combines strong password generation, random-chest mechanics, and a persistent scoring system, built with clean architecture and Object-Oriented Programming.

## Overview

Password Hunter is a casual desktop video game where the player generates cryptographically strong passwords to unlock virtual chests. Every valid password opens a random chest — common, rare, legendary, or cursed — that grants or subtracts points. Difficulty adjusts chest odds and the score multiplier.

The academic goal is to demonstrate, in a capstone project: OOP, inheritance, polymorphism, advanced exception handling, and good Python development practices.

## Screenshots

| Start screen | Password generated |
|---|---|
| ![Start screen](docs/screenshots/01_start_screen.png) | ![Password generated with strength meter](docs/screenshots/02_password_generated.png) |

| Chest opened + achievement unlocked | Global ranking & stats |
|---|---|
| ![Chest opened and achievement popup](docs/screenshots/03_chest_achievement.png) | ![Global ranking and stats panel](docs/screenshots/04_ranking_stats.png) |

## Features

| Category | Detail |
|---|---|
| Passwords | Random generation with no repeated characters, 6-rule validation, 0–100 strength analysis |
| Chests | 4 types using inheritance and polymorphism, odds adjustable by difficulty |
| UI | CustomTkinter dark theme, animations, progress bar, history panel |
| Persistence | Local JSON leaderboard, session history, global statistics |
| Achievements | 5 unlockable achievements with popup notifications |
| Difficulty | Easy / Normal / Hard / Extreme (changes odds and multipliers) |
| Sound | Effects via winsound (Windows, optional) |

## Architecture

```
CazadorDeContrasenas/
│
├── main.py              # Entry point
├── config.py             # Application constants
├── requirements.txt
├── LICENSE
├── conftest.py            # Adds project root to sys.path for tests
├── tests/                  # Unit tests (pytest)
│   ├── test_contrasena.py
│   ├── test_cofres.py
│   └── test_jugador.py
├── .github/workflows/
│   └── tests.yml            # CI: runs tests on every push
│
├── modelos/              # Domain layer (pure OOP)
│   ├── contrasena.py      # Generation + validation
│   ├── cofres.py           # Chest hierarchy (inheritance + polymorphism)
│   ├── jugador.py           # Session state
│   └── estadisticas.py       # Global statistics
│
├── vistas/                # Presentation layer (CustomTkinter)
│   ├── ventana_principal.py  # Root window and start screen
│   ├── panel_juego.py         # Active game UI
│   ├── panel_ranking.py        # Ranking modal window
│   └── componentes.py           # Reusable widgets
│
├── controladores/          # Coordination layer (MVC)
│   ├── juego_controlador.py  # Main orchestrator
│   └── validaciones_controlador.py
│
├── servicios/               # Infrastructure layer
│   ├── generador_service.py
│   ├── ranking_service.py
│   ├── estadisticas_service.py
│   └── sonido_service.py
│
├── excepciones/              # Domain exception hierarchy
│   └── excepciones.py
│
├── utils/                     # Cross-cutting utilities
│   ├── constantes.py
│   ├── colores.py
│   ├── helpers.py
│   └── animaciones.py
│
└── data/                       # JSON persistence
    ├── ranking.json
    └── historial.json
```

> Note: internal module, class, and function names remain in Spanish, matching the academic submission for UNAD. This README is provided in English for portfolio purposes.

## Installation

```bash
# 1. Clone or unzip the project
cd CazadorDeContrasenas

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

**Requirements:**
- Python 3.10 or higher (tested on 3.12)
- customtkinter >= 5.2.2

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

44 unit tests cover password generation/validation (`Contrasena`), the chest hierarchy and factory (`cofres.py`), and player state — score, streaks, achievements (`Jugador`). They run automatically on every push via GitHub Actions (see badge above).

## Game Flow

```
[Start screen]
  │ Enter name and difficulty
  ▼
[Game panel]
  │ Set length (8–64)
  │ Click "Generate & open chest"
  ▼
[Generation] ──→ Contrasena.generar()
  │
  ▼
[Validation] ──→ 6 rules + strength analysis
  │
  ├── Valid   ──→ FabricaCofre.crear() ──→ cofre.abrir()
  │                ├── CommonChest (+10)
  │                ├── RareChest (+25)
  │                ├── LegendaryChest (+50, ×2 on a lucky roll)
  │                └── CursedChest (-20)
  │
  └── Invalid ──→ Automatic CursedChest (penalty)

  ▼
[Recording] ──→ Jugador.registrar_ronda()
  │              └── Check achievements
  ▼
[UI] ──→ Update score, history, chest visual
  │
  ▼
[Continue?] ──→ Yes: new round
              └── No: terminar_partida() → save to leaderboard
```

## OOP Principles Implemented

**Encapsulation**
`Contrasena._valor` is private; accessible only through the `.valor` property. `Jugador._puntaje` is only modified through `registrar_ronda()`, guaranteeing state consistency.

**Inheritance**
`CofreBase → CofreComun, CofreRaro, CofreLegendario, CofreMaldito`. Each subclass inherits the interface and only redefines what makes it different.

**Polymorphism**
The `cofre.abrir()` method has the same signature across all four chest types. `JuegoControlador` calls `cofre.abrir()` regardless of the concrete type; the result varies by subclass.

**Abstraction**
`CofreBase` is abstract (ABC): it cannot be instantiated. It defines the contract (abstract methods) that subclasses are required to implement.

**Composition**
`JuegoControlador` holds instances of `GeneradorService`, `RankingService`, `EstadisticasService`, and `SonidoService` instead of inheriting from them.

## Exception Handling

| Exception | When it's raised |
|---|---|
| `LongitudInvalidaError` | Length < 8 or > 64 |
| `EntradaNoNumericaError` | The length field contains non-numeric text |
| `ContrasenaInvalidaError` | Security rules fail (uppercase, number, special char...) |
| `CaracterRepetidoError` | The password has duplicate characters |
| `ErrorPersistencia` | Problems reading/writing JSON files |

All inherit from `ErrorJuego → Exception`, allowing them to be caught with fine granularity or generically depending on context.

## Technologies

- Python 3.12
- CustomTkinter 5.x — modern UI with dark theme
- tkinter — window system base
- random — choice, choices, sample, shuffle
- json + pathlib — data persistence
- abc — abstract base classes
- dataclasses — immutable value types
- threading — sound on a separate thread
- winsound — sound effects (Windows)

## Known Issues

- The live score/round counters shown at the top of the game screen (PUNTOS / RONDAS / RACHA) do not visually refresh after opening a chest, even though the score is correctly calculated and saved (confirmed both directly through the game controller and in the final leaderboard/stats panel). Worth a quick look at `TarjetaStat.actualizar()` in `vistas/componentes.py` and the blink animation in `utils/animaciones.py` before a live demo.

## Possible Future Improvements

- Achievement system with cross-session persistence
- Turn-based multiplayer mode
- Export statistics to CSV
- Light / high-contrast theme
- Internationalization (i18n)
- Unit tests with pytest
- Web version with Flask + WebSockets
