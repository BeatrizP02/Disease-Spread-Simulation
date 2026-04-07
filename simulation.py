import numpy as np
import random

class Simulation:
    """
    Core simulation engine for disease spread.
    Handles agent movement (numerical integration), wall bouncing,
    collision detection for disease transmission, and SIR state transitions.
    """

    def __init__(self, agents, width, height, params=None):
        self.agents = agents
        self.width = width
        self.height = height

        # Default parameters (can be overridden)
        defaults = {
            'dt': 1.0,
            'transmission_radius': 15.0,
            'transmission_prob': 0.3,
            'recovery_time': 500.0,
            'integration_method': 'euler',  # 'euler' or 'rk4'
            'social_distancing': False,
            'distancing_factor': 0.5,  # speed multiplier when distancing
            'quarantine': False,
            'quarantine_prob': 0.0,  # probability infected agent gets quarantined
            'quarantine_speed': 0.0,  # speed of quarantined agents (0 = stationary)
        }
        if params:
            defaults.update(params)
        self.params = defaults

        # SIR history for plotting
        self.sir_history = {'S': [], 'I': [], 'R': [], 't': []}
        self.time = 0.0

        # Apply social distancing speed reduction at start if enabled
        if self.params['social_distancing']:
            for agent in self.agents:
                agent.velocity *= self.params['distancing_factor']

    def acceleration(self, pos, velocity):
        """
        Compute acceleration for an agent.
        In the base model agents move at constant velocity (no forces),
        so acceleration is zero.
        """
        return np.array([0.0, 0.0])

    def euler_step(self, agent):
        """Euler integration for position update."""
        dt = self.params['dt']
        acc = self.acceleration(agent.pos, agent.velocity)
        agent.pos += agent.velocity * dt
        agent.velocity += acc * dt

    def rk4_step(self, agent):
        """Runge-Kutta 4th order integration for position update."""
        dt = self.params['dt']
        pos = agent.pos.copy()
        velocity = agent.velocity.copy()

        # k1
        a1 = self.acceleration(pos, velocity)
        k1_v = velocity
        k1_a = a1

        # k2
        pos2 = pos + 0.5 * dt * k1_v
        velocity2 = velocity + 0.5 * dt * k1_a
        a2 = self.acceleration(pos2, velocity2)
        k2_v = velocity2
        k2_a = a2

        # k3
        pos3 = pos + 0.5 * dt * k2_v
        velocity3 = velocity + 0.5 * dt * k2_a
        a3 = self.acceleration(pos3, velocity3)
        k3_v = velocity3
        k3_a = a3

        # k4
        pos4 = pos + dt * k3_v
        velocity4 = velocity + dt * k3_a
        a4 = self.acceleration(pos4, velocity4)
        k4_v = velocity4
        k4_a = a4

        agent.pos = pos + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        agent.velocity = velocity + (dt / 6.0) * (k1_a + 2*k2_a + 2*k3_a + k4_a)

    def handle_wall_collisions(self, agent):
        """Bounce agents off the walls of the simulation boundary."""
        r = agent.radius
        if agent.pos[0] <= r:
            agent.pos[0] = r
            agent.velocity[0] *= -1
        elif agent.pos[0] >= self.width - r:
            agent.pos[0] = self.width - r
            agent.velocity[0] *= -1

        if agent.pos[1] <= r:
            agent.pos[1] = r
            agent.velocity[1] *= -1
        elif agent.pos[1] >= self.height - r:
            agent.pos[1] = self.height - r
            agent.velocity[1] *= -1

    def check_transmission(self):
        """
        Check for disease transmission via collision detection.
        If an Infected agent is within transmission_radius of a Susceptible agent,
        the disease transmits with a given probability.
        """
        t_radius = self.params['transmission_radius']
        t_prob = self.params['transmission_prob']

        infected = [a for a in self.agents if a.state == 'I' and not a.quarantined]
        susceptible = [a for a in self.agents if a.state == 'S']

        for inf_agent in infected:
            for sus_agent in susceptible:
                dist = np.linalg.norm(inf_agent.pos - sus_agent.pos)
                if dist <= t_radius:
                    if random.random() < t_prob:
                        sus_agent.infect()

    def update_recovery(self):
        """Update infection timers and recover agents when recovery time is reached."""
        for agent in self.agents:
            if agent.state == 'I':
                agent.infection_timer += self.params['dt']

                # Quarantine check
                if self.params['quarantine'] and not agent.quarantined:
                    if random.random() < self.params['quarantine_prob']:
                        agent.quarantined = True
                        speed = self.params['quarantine_speed']
                        if speed == 0:
                            agent.velocity = np.array([0.0, 0.0])
                        else:
                            angle = np.arctan2(agent.velocity[1], agent.velocity[0])
                            agent.velocity = np.array([speed * np.cos(angle), speed * np.sin(angle)])

                if agent.infection_timer >= self.params['recovery_time']:
                    agent.recover()

    def record_sir(self):
        """Record current SIR counts for plotting."""
        s = sum(1 for a in self.agents if a.state == 'S')
        i = sum(1 for a in self.agents if a.state == 'I')
        r = sum(1 for a in self.agents if a.state == 'R')
        self.sir_history['S'].append(s)
        self.sir_history['I'].append(i)
        self.sir_history['R'].append(r)
        self.sir_history['t'].append(self.time)

    def step(self):
        """Advance simulation by one time step."""
        # Move agents
        for agent in self.agents:
            if self.params['integration_method'] == 'rk4':
                self.rk4_step(agent)
            else:
                self.euler_step(agent)
            self.handle_wall_collisions(agent)

        # Disease mechanics
        self.check_transmission()
        self.update_recovery()

        self.time += self.params['dt']
        self.record_sir()

    def get_sir_counts(self):
        """Return current S, I, R counts."""
        s = sum(1 for a in self.agents if a.state == 'S')
        i = sum(1 for a in self.agents if a.state == 'I')
        r = sum(1 for a in self.agents if a.state == 'R')
        return s, i, r

    def is_finished(self):
        """Check if epidemic is over (no more infected agents)."""
        return all(a.state != 'I' for a in self.agents)
