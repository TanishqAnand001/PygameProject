import pygame
import random


class Star:
    """A single star in the starfield, with optimized properties."""

    def __init__(self, screen_width, screen_height):
        """
        Initialize the star with a random position, size, and speed.
        Args:
            screen_width (int): The width of the game screen.
            screen_height (int): The height of the game screen.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Pre-compute colors as tuples to avoid repeated list access
        self.TINT_COLORS = (
            (80, 80, 120), (120, 120, 150), (100, 100, 130), (90, 90, 110)
        )
        self.reset()

    def reset(self):
        """Reset the star to a new random state, usually off-screen."""
        self.x = random.randrange(0, self.screen_width)
        self.y = random.randrange(-self.screen_height, 0)
        # Much smaller star sizes to look far away
        self.size = random.uniform(0.2, 0.8)
        # Cache integer size to avoid repeated int() calls
        self.int_size = max(1, int(self.size))
        # Slower speed for distant effect
        self.speed = self.size * random.randint(5, 15)
        self.color = random.choice(self.TINT_COLORS)
        # Cache integer coordinates
        self.int_x = int(self.x)
        self.int_y = int(self.y)

    def update(self, dt):
        """
        Move the star down. If it goes off-screen, reset it.
        Args:
            dt (float): The time in seconds since the last frame.
        """
        self.y += self.speed * dt
        # Only update integer coordinates when needed
        self.int_y = int(self.y)
        if self.y > self.screen_height + 10:  # Small buffer to avoid edge cases
            self.reset()
            return True  # Star was reset
        return False  # Star is still active

    def draw(self, surface):
        """
        Draw the star as a tiny point on the surface.
        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        # Draw as very small circles for distant star effect
        if self.int_size == 1:
            # Single pixel stars
            surface.set_at((self.int_x, self.int_y), self.color)
        else:
            # Tiny circles for slightly larger stars
            pygame.draw.circle(surface, self.color, (self.int_x, self.int_y), self.int_size)
