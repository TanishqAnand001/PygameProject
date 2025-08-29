"""
Start screen with animated title and menu options.
"""
import pygame
import math
import time
import random
from config.settings import *


class StartScreen:
    """Fancy start screen with animated elements."""

    def __init__(self, screen_width, screen_height):
        """Initialize the start screen."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Animation timers
        self.title_pulse_timer = 0
        self.menu_fade_timer = 0
        self.particle_timer = 0
        self.background_scroll = 0

        # Fonts - using modern built-in fonts
        self.title_font = pygame.font.Font(None, 120)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 42)
        self.credit_font = pygame.font.Font(None, 24)

        # Colors
        self.title_color = (100, 200, 255)
        self.subtitle_color = (200, 200, 255)
        self.menu_color = (255, 255, 255)
        self.menu_highlight_color = (255, 255, 100)
        self.credit_color = (150, 150, 150)

        # Menu options
        self.menu_options = ["START GAME", "CONTROLS", "QUIT"]
        self.selected_option = 0

        # Background particles
        self.particles = []
        self._create_background_particles()

        # Game title
        self.game_title = "NEXUS ASSAULT"
        self.game_subtitle = "Geometric Space Combat"

    def _create_background_particles(self):
        """Create animated background particles."""
        for _ in range(50):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'speed': random.uniform(10, 30),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150),
                'color': random.choice([(100, 150, 255), (150, 100, 255), (255, 150, 100)])
            }
            self.particles.append(particle)

    def handle_input(self, event):
        """Handle start screen input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                return "menu_move"
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                return "menu_move"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:
                    return "start_game"
                elif self.selected_option == 1:
                    return "show_controls"
                elif self.selected_option == 2:
                    return "quit_game"
        return None

    def update(self, dt):
        """Update start screen animations."""
        self.title_pulse_timer += dt
        self.menu_fade_timer += dt
        self.particle_timer += dt
        self.background_scroll += dt * 20

        # Update background particles
        for particle in self.particles:
            particle['y'] += particle['speed'] * dt
            if particle['y'] > self.screen_height:
                particle['y'] = -10
                particle['x'] = random.randint(0, self.screen_width)

    def draw(self, surface):
        """Draw the start screen."""
        # Clear with dark background
        surface.fill((5, 5, 20))

        # Draw animated background
        self._draw_background(surface)

        # Draw title with pulse animation
        self._draw_title(surface)

        # Draw menu
        self._draw_menu(surface)

        # Draw credits
        self._draw_credits(surface)

    def _draw_background(self, surface):
        """Draw animated background elements."""
        # Draw moving particles
        for particle in self.particles:
            alpha_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            color_with_alpha = (*particle['color'], particle['alpha'])
            pygame.draw.circle(alpha_surface, particle['color'],
                             (particle['size'], particle['size']), particle['size'])
            surface.blit(alpha_surface, (particle['x'], particle['y']))

        # Draw grid lines for sci-fi effect
        grid_alpha = int(30 + 20 * math.sin(self.background_scroll * 0.1))
        grid_color = (50, 100, 150, grid_alpha)

        # Vertical lines
        for x in range(0, self.screen_width, 100):
            start_pos = (x, 0)
            end_pos = (x, self.screen_height)
            pygame.draw.line(surface, grid_color[:3], start_pos, end_pos, 1)

        # Horizontal lines
        for y in range(0, self.screen_height, 100):
            start_pos = (0, y)
            end_pos = (self.screen_width, y)
            pygame.draw.line(surface, grid_color[:3], start_pos, end_pos, 1)

    def _draw_title(self, surface):
        """Draw animated game title."""
        # Title pulse effect
        pulse = math.sin(self.title_pulse_timer * 2) * 0.1 + 1.0

        # Main title
        title_surface = self.title_font.render(self.game_title, True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 3))

        # Scale effect
        scaled_width = int(title_surface.get_width() * pulse)
        scaled_height = int(title_surface.get_height() * pulse)
        scaled_title = pygame.transform.scale(title_surface, (scaled_width, scaled_height))
        scaled_rect = scaled_title.get_rect(center=title_rect.center)

        # Glow effect
        glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
        glow_color = (*self.title_color, int(50 * pulse))
        pygame.draw.rect(glow_surface, glow_color[:3], glow_surface.get_rect(), border_radius=10)
        glow_rect = glow_surface.get_rect(center=scaled_rect.center)
        surface.blit(glow_surface, glow_rect)

        surface.blit(scaled_title, scaled_rect)

        # Subtitle
        subtitle_surface = self.subtitle_font.render(self.game_subtitle, True, self.subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, title_rect.bottom + 30))
        surface.blit(subtitle_surface, subtitle_rect)

    def _draw_menu(self, surface):
        """Draw animated menu options."""
        menu_start_y = self.screen_height // 2 + 50

        for i, option in enumerate(self.menu_options):
            # Calculate position
            y_pos = menu_start_y + i * 60

            # Selection effects
            if i == self.selected_option:
                # Highlight animation
                highlight_pulse = math.sin(self.menu_fade_timer * 4) * 0.3 + 0.7
                color = tuple(int(c * highlight_pulse) for c in self.menu_highlight_color)

                # Selection box
                box_width = 300
                box_height = 50
                box_rect = pygame.Rect(0, 0, box_width, box_height)
                box_rect.center = (self.screen_width // 2, y_pos)

                # Animated border
                border_alpha = int(100 + 50 * math.sin(self.menu_fade_timer * 3))
                border_surface = pygame.Surface((box_width + 10, box_height + 10), pygame.SRCALPHA)
                border_color = (*self.menu_highlight_color, border_alpha)
                pygame.draw.rect(border_surface, border_color[:3], border_surface.get_rect(),
                               width=3, border_radius=5)
                border_rect = border_surface.get_rect(center=box_rect.center)
                surface.blit(border_surface, border_rect)
            else:
                color = self.menu_color

            # Draw menu text
            text_surface = self.menu_font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_pos))
            surface.blit(text_surface, text_rect)

    def _draw_credits(self, surface):
        """Draw credits and instructions."""
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to quit"
        ]

        y_start = self.screen_height - 120
        for i, instruction in enumerate(instructions):
            text_surface = self.credit_font.render(instruction, True, self.credit_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_start + i * 25))
            surface.blit(text_surface, text_rect)

        # Version info
        version_text = self.credit_font.render("Enhanced Edition v2.0", True, self.credit_color)
        version_rect = version_text.get_rect(bottomright=(self.screen_width - 20, self.screen_height - 10))
        surface.blit(version_text, version_rect)
