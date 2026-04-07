import pygame
import sys
import random
import numpy as np
from agent import Agent
from simulation import Simulation
from visualization import Renderer, plot_sir_curves

# CONFIGURATION — These parameters control the simulation and can be easily modified/tested for experimentation.

CONFIG = {
    # Population
    'num_agents': 200,
    'initial_infected': 3,
    'agent_speed': 2.0,

    # Disease parameters
    'transmission_radius': 15.0,
    'transmission_prob': 0.3,
    'recovery_time': 500.0,

    # Numerical integration
    'dt': 1.0,
    'integration_method': 'euler',  # 'euler' or 'rk4'

    # Interventions
    'social_distancing': False,
    'distancing_factor': 0.5,
    'quarantine': False,
    'quarantine_prob': 0.05,
    'quarantine_speed': 0.0,

    # Display
    'sim_width': 800,
    'sim_height': 600,
    'panel_width': 250,
    'fps': 30,
    'record_interval': 5,  # record SIR every N frames
}


def create_simulation(config):
    #Create a fresh simulation from config parameters. This is used for initial setup and resetting the simulation.
    agents = Agent.create_population(
        n=config['num_agents'],
        width=config['sim_width'],
        height=config['sim_height'],
        initial_infected=config['initial_infected'],
        speed=config['agent_speed'],
    )
    params = {
        'dt': config['dt'],
        'transmission_radius': config['transmission_radius'],
        'transmission_prob': config['transmission_prob'],
        'recovery_time': config['recovery_time'],
        'integration_method': config['integration_method'],
        'social_distancing': config['social_distancing'],
        'distancing_factor': config['distancing_factor'],
        'quarantine': config['quarantine'],
        'quarantine_prob': config['quarantine_prob'],
        'quarantine_speed': config['quarantine_speed'],
    }
    return Simulation(agents, config['sim_width'], config['sim_height'], params)


def main():
    random.seed(42)
    np.random.seed(42)

    pygame.init()
    total_width = CONFIG['sim_width'] + CONFIG['panel_width']
    screen = pygame.display.set_mode((total_width, CONFIG['sim_height']))
    pygame.display.set_caption("Disease Spread Simulation — CSCI 3010U")
    clock = pygame.time.Clock()

    sim = create_simulation(CONFIG)
    renderer = Renderer(screen, CONFIG['sim_width'], CONFIG['sim_height'], CONFIG['panel_width'])

    paused = False
    running = True
    frame = 0

    print("Disease Spread Simulation")
    print("Controls: P=Pause, R=Reset, 1=Toggle Euler/RK4, D=Distancing, Q=Quarantine, ESC=Quit")

    # Main simulation loop - handles user input, updates simulation, and renders each frame
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset simulation
                    random.seed(42)
                    np.random.seed(42)
                    sim = create_simulation(CONFIG)
                    frame = 0
                    print("Simulation reset.")
                elif event.key == pygame.K_1:
                    # Toggle integration method
                    if sim.params['integration_method'] == 'euler':
                        sim.params['integration_method'] = 'rk4'
                    else:
                        sim.params['integration_method'] = 'euler'
                    print(f"Integration: {sim.params['integration_method'].upper()}")
                elif event.key == pygame.K_d:
                    # Toggle social distancing
                    sim.params['social_distancing'] = not sim.params['social_distancing']
                    factor = sim.params['distancing_factor'] if sim.params['social_distancing'] else 1.0 / sim.params['distancing_factor']
                    for agent in sim.agents:
                        if not agent.quarantined:
                            agent.velocity *= factor
                    print(f"Social distancing: {'ON' if sim.params['social_distancing'] else 'OFF'}")
                elif event.key == pygame.K_q:
                    # Toggle quarantine
                    sim.params['quarantine'] = not sim.params['quarantine']
                    print(f"Quarantine: {'ON' if sim.params['quarantine'] else 'OFF'}")
                elif event.key == pygame.K_s:
                    # Save SIR curves
                    plot_sir_curves(sim.sir_history, title="SIR Curves", filename="sir_curves.png")

        if not paused:
            sim.step()
            frame += 1

            # Auto-save SIR plot when epidemic ends
            if sim.is_finished() and not paused:
                print(f"Epidemic ended at time {sim.time:.0f}")
                plot_sir_curves(sim.sir_history, title="SIR Curves — Epidemic Complete", filename="sir_curves.png")
                paused = True

        renderer.draw_frame(sim, paused)
        clock.tick(CONFIG['fps'])

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
