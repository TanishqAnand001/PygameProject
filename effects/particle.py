import pygame
from config.settings import *


class Particle:
    """An optimized particle with customizable properties."""

    def __init__(self, x, y, velocity_x=0, velocity_y=0, size=2, life=1.0,
                 color=(255, 255, 255), particle_type="rectangle"):
        """
        Initialize a particle with optimized properties.
        """
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.initial_size = size
        self.life = life
        self.max_life = life

        # Ensure color is a valid RGB tuple
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        else:
            self.color = (255, 255, 255)  # Default white

        self.particle_type = particle_type
        self.gravity = 0
        self.fade_rate = 1.0
        self.shrink_rate = 0.0

        # Cache integer values for performance
        self.int_x = int(x)
        self.int_y = int(y)
        self.int_size = max(1, int(size))

    def update(self, dt):
        """Update particle position, life, and size with optimizations."""
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Cache integer coordinates less frequently
        self.int_x = int(self.x)
        self.int_y = int(self.y)

        # Apply gravity
        if self.gravity != 0:
            self.velocity_y += self.gravity * dt

        # Update life
        self.life -= dt * self.fade_rate

        # Update size
        if self.shrink_rate > 0:
            self.size = max(0, self.size - self.shrink_rate * dt)
            self.int_size = max(1, int(self.size))

        return self.life > 0 and self.size > 0

    def draw(self, surface):
        """Draw the particle with optimized rendering."""
        if self.life <= 0 or self.size <= 0:
            return

        # Calculate alpha based on life remaining
        alpha_ratio = max(0, min(1, self.life / self.max_life))

        # Create color with alpha
        current_color = (
            int(self.color[0] * alpha_ratio),
            int(self.color[1] * alpha_ratio),
            int(self.color[2] * alpha_ratio)
        )

        # Ensure color values are valid (0-255)
        current_color = (
            max(0, min(255, current_color[0])),
            max(0, min(255, current_color[1])),
            max(0, min(255, current_color[2]))
        )

        # Draw based on particle type
        if self.particle_type == "circle":
            if self.int_size > 0:
                pygame.draw.circle(surface, current_color, (self.int_x, self.int_y), self.int_size)
        else:  # rectangle
            if self.int_size > 0:
                rect = pygame.Rect(self.int_x - self.int_size // 2, self.int_y - self.int_size // 2,
                                 self.int_size, self.int_size)
                pygame.draw.rect(surface, current_color, rect)
