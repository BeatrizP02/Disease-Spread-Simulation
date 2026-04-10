# Disease Spread Simulation using Collision Detection
**CSCI 3010U — Simulation and Modelling**
**Beatriz Provido — 100870394**

## Overview
An agent-based simulation of disease spread using collision detection in a 2D environment. Instead of traditional SIR models that assume uniform mixing, this simulation models transmission based on spatial proximity between individual agents.

## Features
- **SIR Model**: Agents transition between Susceptible, Infected, and Recovered states
- **Collision-Based Transmission**: Disease spreads only when agents are within a configurable radius
- **Numerical Integration**: Supports both Euler and RK4 methods
- **Public Health Interventions**: Social distancing (reduced agent speed) and quarantine (isolation of infected agents)
- **Real-Time Visualization**: Pygame-based rendering with live SIR statistics panel
- **SIR Curve Plotting**: Matplotlib-generated graphs saved as PNG

## Requirements
```
pip install pygame matplotlib numpy
```

## How to Run
```
python main.py
```

## Controls
| Key | Action |
|-----|--------|
| P | Pause/Resume |
| R | Reset simulation |
| 1 | Toggle Euler/RK4 |
| D | Toggle Social Distancing |
| Q | Toggle Quarantine |
| S | Save SIR curves |
| ESC | Quit |

## File Structure
- `main.py` — Entry point, configuration, and main loop
- `agent.py` — Agent class with SIR states and population generator
- `simulation.py` — Core engine with integration, collision detection, and disease mechanics
- `visualization.py` — Pygame renderer and matplotlib SIR curve plotting

## Parameters
All simulation parameters can be modified in the `CONFIG` dictionary in `main.py`:
- `num_agents`: 200
- `transmission_radius`: 15.0
- `transmission_prob`: 0.3
- `recovery_time`: 500.0
- `integration_method`: 'euler' or 'rk4'
