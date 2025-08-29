import random
from config.settings import *
from effects.particle import Particle


class ThrusterParticle(Particle):
    """Optimized thruster particle with pre-computed colors."""

    # Pre-compute color variations using config colors
    ORANGE_COLORS = [THRUSTER_COLOR_HOT, THRUSTER_COLOR_WARM, (255, 255, 0)]
    RED_COLORS = [(255, 100, 0), (200, 50, 0), (150, 0, 0)]

    def __init__(self, x, y, direction_x, direction_y):
        # Random position variation
        x += random.uniform(-3, 3)
        y += random.uniform(-3, 3)

        # Velocity based on direction with randomization
        velocity_x = direction_x * random.uniform(60, 100) + random.uniform(-10, 10)
        velocity_y = direction_y * random.uniform(60, 100) + random.uniform(-10, 10)

        # Random size and life
        size = random.uniform(1, 4)
        life = random.uniform(0.8, 1.2)

        # Start with orange color
        color = random.choice(self.ORANGE_COLORS)

        super().__init__(x, y, velocity_x, velocity_y, size, life, color, "rectangle")

        # Thruster-specific properties
        self.fade_rate = 3.0
        self.shrink_rate = 3.0
        self.life_stage = 0  # 0=orange, 1=red, 2=dark_red

    def update(self, dt):
        """Update thruster particle with optimized color changes."""
        result = super().update(dt)

        # Change color based on life remaining (less frequent updates)
        life_ratio = self.life / self.max_life
        if life_ratio > 0.7 and self.life_stage != 0:
            self.color = random.choice(self.ORANGE_COLORS)
            self.life_stage = 0
        elif 0.4 < life_ratio <= 0.7 and self.life_stage != 1:
            self.color = random.choice(self.RED_COLORS)
            self.life_stage = 1
        elif life_ratio <= 0.4 and self.life_stage != 2:
            self.color = (100, 0, 0)
            self.life_stage = 2

        return result
