"""
Game Over screen with play again functionality.
"""
import pygame
from config.settings import *


class GameOverScreen:
    """Game over screen with play again option."""

    def __init__(self, screen_width, screen_height):
        """Initialize the game over screen."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.text_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)

        # Colors
        self.title_color = (255, 100, 100)  # Red
        self.text_color = (255, 255, 255)   # White
        self.highlight_color = (255, 255, 100)  # Yellow
        self.overlay_color = (0, 0, 0, 180)  # Semi-transparent black

        # Create overlay surface
        self.overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.overlay.fill(self.overlay_color)

        # Button areas for collision detection
        self.play_again_rect = pygame.Rect(0, 0, 300, 60)
        self.quit_rect = pygame.Rect(0, 0, 200, 60)

        # Center buttons
        self.play_again_rect.center = (screen_width // 2, screen_height // 2 + 80)
        self.quit_rect.center = (screen_width // 2, screen_height // 2 + 160)

        # Animation
        self.fade_alpha = 0
        self.max_fade = 200
        self.fade_speed = 300  # Alpha per second

    def update(self, dt):
        """Update the game over screen animation."""
        if self.fade_alpha < self.max_fade:
            self.fade_alpha = min(self.max_fade, self.fade_alpha + self.fade_speed * dt)

    def handle_click(self, pos):
        """
        Handle mouse clicks on the game over screen.
        Returns: 'play_again', 'quit', or None
        """
        if self.play_again_rect.collidepoint(pos):
            return 'play_again'
        elif self.quit_rect.collidepoint(pos):
            return 'quit'
        return None

    def handle_keys(self, keys):
        """
        Handle keyboard input.
        Returns: 'play_again', 'quit', or None
        """
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            return 'play_again'
        elif keys[pygame.K_ESCAPE]:
            return 'quit'
        return None

    def draw(self, screen, score, final_wave):
        """Draw the game over screen."""
        # Draw overlay
        current_overlay = self.overlay.copy()
        current_overlay.set_alpha(int(self.fade_alpha))
        screen.blit(current_overlay, (0, 0))

        if self.fade_alpha < 50:  # Don't draw text until overlay is visible
            return

        # Calculate text alpha based on fade
        text_alpha = min(255, int((self.fade_alpha / self.max_fade) * 255))

        # Game Over title
        title_text = self.title_font.render("GAME OVER", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        screen.blit(title_text, title_rect)

        # Score display
        score_text = self.text_font.render(f"Final Score: {score}", True, self.text_color)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40))
        screen.blit(score_text, score_rect)

        # Wave reached
        wave_text = self.small_font.render(f"Wave Reached: {final_wave}", True, self.text_color)
        wave_rect = wave_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(wave_text, wave_rect)

        # Play Again button
        pygame.draw.rect(screen, (50, 50, 50), self.play_again_rect)
        pygame.draw.rect(screen, self.highlight_color, self.play_again_rect, 3)

        play_text = self.text_font.render("PLAY AGAIN", True, self.text_color)
        play_text_rect = play_text.get_rect(center=self.play_again_rect.center)
        screen.blit(play_text, play_text_rect)

        # Quit button
        pygame.draw.rect(screen, (50, 50, 50), self.quit_rect)
        pygame.draw.rect(screen, self.text_color, self.quit_rect, 2)

        quit_text = self.text_font.render("QUIT", True, self.text_color)
        quit_text_rect = quit_text.get_rect(center=self.quit_rect.center)
        screen.blit(quit_text, quit_text_rect)

        # Instructions
        if text_alpha > 150:
            instruction_text = self.small_font.render("SPACE/ENTER: Play Again  |  ESC: Quit", True, self.text_color)
            instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 240))
            screen.blit(instruction_text, instruction_rect)
