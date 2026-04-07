import numpy as np
import random

class Agent:
    """
    Represents an individual in the disease spread simulation.
    Each agent has a position, velocity, and an SIR state:
      'S' = Susceptible, 'I' = Infected, 'R' = Recovered
    """

    def __init__(self, x, y, vx, vy, state='S', agent_id=0):
        self.pos = np.array([x, y], dtype=float)
        self.velocity = np.array([vx, vy], dtype=float)
        self.state = state  # 'S', 'I', or 'R'
        self.agent_id = agent_id
        self.infection_timer = 0.0  # time spent infected
        self.quarantined = False
        self.radius = 5.0  # visual/collision radius in pixels

    def get_color(self):
        #Return color based on SIR state.
        if self.quarantined:
            return (128, 0, 128)  # purple for quarantined
        colors = {
            'S': (0, 150, 255),    # blue
            'I': (255, 50, 50),    # red
            'R': (100, 200, 100),  # green
        }
        return colors.get(self.state, (255, 255, 255))

    def infect(self):
        #Transition agent from Susceptible to Infected.
        if self.state == 'S':
            self.state = 'I'
            self.infection_timer = 0.0

    def recover(self):
        #Transition agent from Infected to Recovered.
        if self.state == 'I':
            self.state = 'R'
            self.quarantined = False

    @staticmethod
    def create_population(n, width, height, initial_infected=1, speed=2.0):
        """
        Generate a population of n agents with random positions and velocities.
        A specified number start as Infected; the rest are Susceptible.
        """
        agents = []
        for i in range(n):
            x = random.uniform(20, width - 20)
            y = random.uniform(20, height - 20)
            angle = random.uniform(0, 2 * np.pi)
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle)
            state = 'I' if i < initial_infected else 'S'
            agents.append(Agent(x, y, vx, vy, state=state, agent_id=i))
        return agents
