import pygame
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for saving figures
import matplotlib.pyplot as plt
import numpy as np

# Colors
BG_COLOR = (15, 15, 30)
BORDER_COLOR = (60, 60, 80)
TEXT_COLOR = (200, 200, 220)
PANEL_BG = (25, 25, 45)

class Renderer:
    #Handles all pygame drawing for the disease spread simulation.
    def __init__(self, screen, sim_width, sim_height, panel_width=250):
        self.screen = screen
        self.sim_width = sim_width
        self.sim_height = sim_height
        self.panel_width = panel_width
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 18, bold=True)

    def draw_agents(self, agents):
        #Draw all agents as colored circles.
        for agent in agents:
            color = agent.get_color()
            pos = (int(agent.pos[0]), int(agent.pos[1]))
            pygame.draw.circle(self.screen, color, pos, int(agent.radius))
            # Draw transmission radius faintly for infected agents
            if agent.state == 'I' and not agent.quarantined:
                s = pygame.Surface((self.sim_width, self.sim_height), pygame.SRCALPHA)
                pygame.draw.circle(s, (*color, 30), pos, 15)
                self.screen.blit(s, (0, 0))

    def draw_panel(self, sim, paused):
        #Draw the info panel on the right side.
        panel_x = self.sim_width
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, 0, self.panel_width, self.sim_height))
        pygame.draw.line(self.screen, BORDER_COLOR, (panel_x, 0), (panel_x, self.sim_height), 2)

        s, i, r = sim.get_sir_counts()
        n = len(sim.agents)
        y = 20

        # Title
        title = self.title_font.render("Disease Spread Sim", True, TEXT_COLOR)
        self.screen.blit(title, (panel_x + 15, y))
        y += 35

        # SIR counts
        info_lines = [
            f"Time: {sim.time:.0f}",
            f"",
            f"Susceptible: {s}",
            f"Infected:    {i}",
            f"Recovered:   {r}",
            f"Total:       {n}",
            f"",
            f"Method: {sim.params['integration_method'].upper()}",
            f"Trans. Radius: {sim.params['transmission_radius']:.0f}",
            f"Trans. Prob:   {sim.params['transmission_prob']:.2f}",
            f"Recovery Time: {sim.params['recovery_time']:.0f}",
            f"",
            f"Social Dist: {'ON' if sim.params['social_distancing'] else 'OFF'}",
            f"Quarantine:  {'ON' if sim.params['quarantine'] else 'OFF'}",
        ]

        if paused:
            info_lines.insert(1, "** PAUSED **")

        for line in info_lines:
            color = TEXT_COLOR
            if "Susceptible" in line:
                color = (0, 150, 255)
            elif "Infected" in line:
                color = (255, 50, 50)
            elif "Recovered" in line:
                color = (100, 200, 100)
            elif "PAUSED" in line:
                color = (255, 255, 0)

            text = self.font.render(line, True, color)
            self.screen.blit(text, (panel_x + 15, y))
            y += 20

        # Mini SIR bar
        y += 10
        bar_x = panel_x + 15
        bar_w = self.panel_width - 30
        bar_h = 20
        if n > 0:
            s_w = int(bar_w * s / n)
            i_w = int(bar_w * i / n)
            r_w = bar_w - s_w - i_w
            pygame.draw.rect(self.screen, (0, 150, 255), (bar_x, y, s_w, bar_h))
            pygame.draw.rect(self.screen, (255, 50, 50), (bar_x + s_w, y, i_w, bar_h))
            pygame.draw.rect(self.screen, (100, 200, 100), (bar_x + s_w + i_w, y, r_w, bar_h))
        pygame.draw.rect(self.screen, BORDER_COLOR, (bar_x, y, bar_w, bar_h), 1)

        # Controls
        y += 40
        controls = [
            "Controls:",
            "P - Pause/Resume",
            "R - Reset",
            "1 - Toggle Euler/RK4",
            "D - Toggle Distancing",
            "Q - Toggle Quarantine",
            "ESC - Quit",
        ]
        for line in controls:
            text = self.font.render(line, True, (150, 150, 170))
            self.screen.blit(text, (panel_x + 15, y))
            y += 18

    def draw_frame(self, sim, paused=False):
        #Draw a complete frame.
        self.screen.fill(BG_COLOR)
        # Simulation border
        pygame.draw.rect(self.screen, BORDER_COLOR, (0, 0, self.sim_width, self.sim_height), 1)
        self.draw_agents(sim.agents)
        self.draw_panel(sim, paused)
        pygame.display.flip()


def plot_sir_curves(sir_history, title="SIR Curves", filename=None):
    #Plot SIR curves using matplotlib and optionally save to file.
    fig, ax = plt.subplots(figsize=(10, 6))
    t = sir_history['t']
    ax.plot(t, sir_history['S'], color='#0096FF', label='Susceptible', linewidth=2)
    ax.plot(t, sir_history['I'], color='#FF3232', label='Infected', linewidth=2)
    ax.plot(t, sir_history['R'], color='#64C864', label='Recovered', linewidth=2)
    ax.set_xlabel('Time Steps', fontsize=12)
    ax.set_ylabel('Number of Agents', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#0F0F1E')
    fig.patch.set_facecolor('#1A1A2E')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_color('#3C3C50')
    ax.legend(fontsize=11, facecolor='#1A1A2E', edgecolor='#3C3C50', labelcolor='white')

    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, facecolor=fig.get_facecolor())
        print(f"SIR curve saved to {filename}")
    plt.close(fig)
    return fig
