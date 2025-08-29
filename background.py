import pygame
from entities.star import Star


class Background:
    """Manages an optimized scrolling starfield with motion trails."""

    def __init__(self, screen_width, screen_height, star_count=300):  # Reduced default star count
        """
        Initialize the background.
        Args:
            screen_width (int): The width of the game screen.
            screen_height (int): The height of the game screen.
            star_count (int): The number of stars to generate.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dark_blue = (0, 0, 20)

        # --- Optimized Starfield Surface ---
        # Use hardware acceleration if available
        self.star_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA).convert_alpha()
        self.trail_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA).convert_alpha()
        self.trail_surface.fill((0, 0, 10, 15))

        # --- Star Generation ---
        self.stars = [Star(screen_width, screen_height) for _ in range(star_count)]

        # Performance tracking
        self.frame_count = 0
        self.update_frequency = 60  # Update trail effect every 60 frames for better performance

    def update(self, dt):
        """
        Update all stars in the starfield with optimizations.
        Args:
            dt (float): The time in seconds since the last frame.
        """
        # Update stars efficiently
        for star in self.stars:
            star.update(dt)

    def draw(self, screen):
        """
        Draw the optimized background with selective trail updates.
        Args:
            screen (pygame.Surface): The main display surface to draw on.
        """
        # 1. Draw the solid dark blue background
        screen.fill(self.dark_blue)

        # 2. Apply trail effect less frequently for better performance
        self.frame_count += 1
        if self.frame_count % 2 == 0:  # Update trails every other frame
            self.star_surface.blit(self.trail_surface, (0, 0))

        # 3. Draw visible stars only
        visible_stars = 0
        for star in self.stars:
            # Only draw stars that are likely visible
            if -10 <= star.int_y <= self.screen_height + 10:
                star.draw(self.star_surface)
                visible_stars += 1

        # 4. Draw the complete starfield onto the main screen
        screen.blit(self.star_surface, (0, 0))

    def get_visible_star_count(self):
        """Get the number of currently visible stars for debugging."""
        return sum(1 for star in self.stars if -10 <= star.int_y <= self.screen_height + 10)
