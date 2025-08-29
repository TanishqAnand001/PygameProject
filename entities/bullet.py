import pygame
import math


class Bullet:
    """A projectile fired by the player ship."""

    def __init__(self, x, y, direction_x=0, direction_y=-1, speed=600, size=3):
        """
        Initialize a bullet.
        Args:
            x, y: Starting position
            direction_x, direction_y: Direction vector (normalized)
            speed: Bullet speed in pixels per second
            size: Bullet radius
        """
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.size = size
        self.active = True

        # Cache integer coordinates for performance
        self.int_x = int(x)
        self.int_y = int(y)

        # Visual properties
        self.color = (255, 255, 100)  # Bright yellow
        self.trail_length = 8
        self.trail_positions = []

    def update(self, dt, screen_width, screen_height):
        """
        Update bullet position and check bounds.
        Args:
            dt: Delta time in seconds
            screen_width, screen_height: Screen boundaries
        Returns:
            bool: True if bullet is still active
        """
        # Update position
        self.x += self.direction_x * self.speed * dt
        self.y += self.direction_y * self.speed * dt

        # Cache integer coordinates
        self.int_x = int(self.x)
        self.int_y = int(self.y)

        # Add to trail
        self.trail_positions.append((self.int_x, self.int_y))
        if len(self.trail_positions) > self.trail_length:
            self.trail_positions.pop(0)

        # Check bounds - deactivate if out of screen
        if (self.x < -10 or self.x > screen_width + 10 or
            self.y < -10 or self.y > screen_height + 10):
            self.active = False

        return self.active

    def draw(self, surface):
        """Draw the bullet with a trail effect."""
        if not self.active:
            return

        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail_positions):
            alpha_factor = (i + 1) / len(self.trail_positions)
            trail_size = max(1, int(self.size * alpha_factor))
            trail_color = (
                int(self.color[0] * alpha_factor),
                int(self.color[1] * alpha_factor),
                int(self.color[2] * alpha_factor)
            )
            pygame.draw.circle(surface, trail_color, (trail_x, trail_y), trail_size)

        # Draw main bullet
        pygame.draw.circle(surface, self.color, (self.int_x, self.int_y), self.size)

        # Add bright core
        core_color = (255, 255, 255)
        pygame.draw.circle(surface, core_color, (self.int_x, self.int_y), max(1, self.size - 1))

    def get_rect(self):
        """Get collision rectangle for the bullet."""
        return pygame.Rect(self.int_x - self.size, self.int_y - self.size,
                          self.size * 2, self.size * 2)
