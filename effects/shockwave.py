import pygame
import math


class Shockwave:
    """A visual shockwave effect that expands outward from a point."""

    def __init__(self, x, y, max_radius=150, duration=0.8):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.current_radius = 0
        self.age = 0
        self.expansion_speed = max_radius / duration

    def update(self, dt):
        """Update the shockwave expansion."""
        self.age += dt
        self.current_radius += self.expansion_speed * dt
        return self.age < self.duration

    def draw(self, screen):
        """Draw the shockwave ring."""
        if self.current_radius > 0 and self.age < self.duration:
            # Calculate opacity based on age (fade out over time)
            opacity = max(0, int(255 * (1 - self.age / self.duration)))

            # Calculate ring thickness based on radius
            thickness = max(1, int(3 * (1 - self.age / self.duration)))

            # Create shockwave color (bright cyan/white)
            color = (255, 255, 255)

            # Draw the expanding ring
            if self.current_radius > 0 and opacity > 50:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)),
                                 int(self.current_radius), thickness)
