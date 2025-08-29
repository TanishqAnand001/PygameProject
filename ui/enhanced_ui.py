"""
Enhanced notification and UI system with improved spacing and animations.
"""
import pygame
import math
from config.settings import *


class Notification:
    """Individual notification with smooth animations and better positioning."""

    def __init__(self, text, notification_type="info", duration=NOTIFICATION_DURATION):
        """Initialize a notification."""
        self.text = text
        self.type = notification_type
        self.duration = duration
        self.max_duration = duration
        self.y_offset = 0
        self.alpha = 0
        self.slide_progress = 0

        # Colors based on type
        self.colors = {
            "info": UI_ACCENT_COLOR,
            "warning": UI_WARNING_COLOR,
            "success": UI_SUCCESS_COLOR,
            "powerup": COMBO_TEXT_COLOR,
            "achievement": (255, 215, 0)  # Gold
        }
        self.color = self.colors.get(notification_type, UI_ACCENT_COLOR)

        # Font with better readability
        self.font = pygame.font.Font(None, 28)

    def update(self, dt):
        """Update notification animation with smooth transitions."""
        self.duration -= dt

        # Slide in animation (first 0.3 seconds)
        if self.max_duration - self.duration < 0.3:
            self.slide_progress = min(1.0, (self.max_duration - self.duration) / 0.3)
            self.alpha = int(255 * self.slide_progress)
        # Fade out in last 0.5 seconds
        elif self.duration < 0.5:
            fade_progress = self.duration / 0.5
            self.alpha = int(255 * fade_progress)
        else:
            self.alpha = 255

        # Floating animation
        self.y_offset = math.sin((self.max_duration - self.duration) * 2) * 2

        return self.duration > 0

    def draw(self, surface, x, y, index):
        """Draw the notification with improved styling."""
        if self.alpha <= 0:
            return

        # Create text surface
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)

        # Background with rounded corners effect
        padding = 15
        bg_width = text_surface.get_width() + padding * 2
        bg_height = text_surface.get_height() + padding

        # Slide animation
        slide_offset = (1 - self.slide_progress) * 200
        final_x = x - slide_offset
        final_y = y + self.y_offset + index * 50  # Better spacing between notifications

        # Create background with glow effect
        bg_surface = pygame.Surface((bg_width + 10, bg_height + 10), pygame.SRCALPHA)

        # Glow effect
        glow_alpha = min(self.alpha // 3, 60)
        glow_color = (*self.color, glow_alpha)
        pygame.draw.rect(bg_surface, glow_color[:3],
                        pygame.Rect(5, 5, bg_width, bg_height), border_radius=8)

        # Main background
        bg_alpha = min(self.alpha // 2, 120)
        bg_color = (20, 20, 40, bg_alpha)
        pygame.draw.rect(bg_surface, bg_color[:3],
                        pygame.Rect(0, 0, bg_width, bg_height), border_radius=5)

        # Border
        border_alpha = min(self.alpha, 180)
        border_color = (*self.color, border_alpha)
        pygame.draw.rect(bg_surface, border_color[:3],
                        pygame.Rect(0, 0, bg_width, bg_height), width=2, border_radius=5)

        # Position and draw
        bg_rect = bg_surface.get_rect()
        bg_rect.topright = (final_x, final_y)
        surface.blit(bg_surface, bg_rect)

        # Draw text
        text_rect = text_surface.get_rect(center=(bg_rect.centerx, bg_rect.centery))
        surface.blit(text_surface, text_rect)


class NotificationManager:
    """Enhanced notification manager with better positioning."""

    def __init__(self, screen_width, screen_height):
        """Initialize the notification manager."""
        self.notifications = []
        self.screen_width = screen_width
        self.screen_height = screen_height

    def add_notification(self, text, notification_type="info", duration=NOTIFICATION_DURATION):
        """Add a new notification."""
        notification = Notification(text, notification_type, duration)
        self.notifications.append(notification)

        # Limit number of notifications to prevent overlap
        if len(self.notifications) > 5:
            self.notifications.pop(0)

    def add_powerup_notification(self, powerup_type):
        """Add a power-up specific notification."""
        powerup_names = {
            "rapid_fire": "🔥 RAPID FIRE Activated!",
            "shield_boost": "🛡️ SHIELD Recharged!",
            "damage_boost": "💥 DAMAGE BOOST Active!",
            "speed_boost": "⚡ SPEED BOOST Active!",
            "triple_shot": "🎯 TRIPLE SHOT Unlocked!"
        }
        text = powerup_names.get(powerup_type, f"{powerup_type.upper()} Activated!")
        self.add_notification(text, "powerup", 3.0)

    def add_wave_notification(self, wave_number):
        """Add wave progression notification."""
        self.add_notification(f"🌊 Wave {wave_number} - Incoming!", "warning", 2.5)

    def add_achievement_notification(self, achievement_text):
        """Add achievement notification."""
        self.add_notification(f"🏆 {achievement_text}", "achievement", 4.0)

    def update(self, dt):
        """Update all notifications."""
        self.notifications = [n for n in self.notifications if n.update(dt)]

    def draw(self, surface):
        """Draw all notifications with proper spacing."""
        start_x = self.screen_width - 10
        start_y = 80  # Move down to avoid overlap with score

        for i, notification in enumerate(self.notifications):
            notification.draw(surface, start_x, start_y, i)


class EnhancedHUD:
    """Enhanced HUD with better spacing and animations."""

    def __init__(self, screen_width, screen_height):
        """Initialize the enhanced HUD."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Modern fonts
        self.large_font = pygame.font.Font(None, 56)
        self.medium_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)

        # Colors with better contrast
        self.primary_color = (255, 255, 255)
        self.accent_color = (100, 200, 255)
        self.warning_color = (255, 100, 100)
        self.success_color = (100, 255, 150)
        self.bg_color = (10, 15, 25)

        # Animation timers
        self.health_flash_timer = 0
        self.shield_pulse_timer = 0
        self.score_pulse_timer = 0

        # Layout constants for better spacing
        self.bar_height = 18
        self.bar_width = 220
        self.margin = 25

    def update(self, dt):
        """Update HUD animations."""
        self.health_flash_timer += dt
        self.shield_pulse_timer += dt
        self.score_pulse_timer += dt

    def draw_enhanced_bars(self, surface, player, score, wave_number, wave_info=None):
        """Draw enhanced health/shield bars with better positioning and wave timer."""
        # Health bar - bottom left
        health_ratio = player.health / player.max_health
        health_color = self.success_color if health_ratio > 0.6 else (
            (255, 255, 100) if health_ratio > 0.3 else self.warning_color
        )

        health_y = self.screen_height - 80
        self._draw_animated_bar(surface, self.margin, health_y,
                              health_ratio, health_color, "HULL INTEGRITY")

        # Health flash effect when critical
        if health_ratio < 0.3 and math.sin(self.health_flash_timer * 8) > 0:
            flash_surface = pygame.Surface((self.bar_width + 20, 40), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, 30))
            surface.blit(flash_surface, (self.margin - 10, health_y - 10))

        # Shield bar - bottom left, below health
        shield_ratio = player.shield_energy / player.max_shield_energy
        shield_color = self.accent_color

        # Pulsing effect when shield is active
        if player.shield_active:
            pulse = math.sin(self.shield_pulse_timer * 6) * 0.3 + 0.7
            shield_color = tuple(int(c * pulse) for c in shield_color)

        shield_y = health_y + 45
        self._draw_animated_bar(surface, self.margin, shield_y,
                              shield_ratio, shield_color, "SHIELD ENERGY")

        # Shield status indicator
        status = "ACTIVE" if player.shield_active else "READY" if shield_ratio > 0.2 else "DEPLETED"
        status_color = self.success_color if player.shield_active else (
            self.accent_color if shield_ratio > 0.2 else self.warning_color
        )
        status_text = self.tiny_font.render(status, True, status_color)
        surface.blit(status_text, (self.margin + self.bar_width + 10, shield_y + 5))

        # Score display - top right with glow effect
        score_text = f"{score:,}"
        score_pulse = math.sin(self.score_pulse_timer * 2) * 0.1 + 1.0

        # Glow effect for score
        glow_surface = self.large_font.render(score_text, True, self.accent_color)
        glow_surface.set_alpha(50)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = glow_surface.get_rect(topright=(self.screen_width - self.margin + offset[0],
                                                       self.margin + offset[1]))
            surface.blit(glow_surface, glow_rect)

        # Main score text
        score_surface = self.large_font.render(score_text, True, self.primary_color)
        score_rect = score_surface.get_rect(topright=(self.screen_width - self.margin, self.margin))
        surface.blit(score_surface, score_rect)

        # Score label
        score_label = self.small_font.render("SCORE", True, self.accent_color)
        label_rect = score_label.get_rect(topright=(self.screen_width - self.margin, self.margin - 25))
        surface.blit(score_label, label_rect)

        # Enhanced Wave display with timer - top left
        wave_text = f"WAVE {wave_number}"
        wave_surface = self.medium_font.render(wave_text, True, self.accent_color)

        # Calculate timer display
        timer_text = ""
        timer_color = self.primary_color
        if wave_info and 'wave_time_remaining' in wave_info:
            time_remaining = wave_info['wave_time_remaining']
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            timer_text = f"{minutes:01d}:{seconds:02d}"

            # Color based on remaining time
            if time_remaining <= 10:
                timer_color = self.warning_color
            elif time_remaining <= 30:
                timer_color = (255, 255, 100)  # Yellow warning
            else:
                timer_color = self.success_color

        # Create combined wave info background
        timer_surface = self.small_font.render(timer_text, True, timer_color) if timer_text else None

        # Calculate total width needed
        total_width = wave_surface.get_width()
        if timer_surface:
            total_width = max(total_width, timer_surface.get_width())

        total_height = wave_surface.get_height()
        if timer_surface:
            total_height += timer_surface.get_height() + 5

        # Wave background
        wave_bg = pygame.Surface((total_width + 20, total_height + 15), pygame.SRCALPHA)
        wave_bg.fill((0, 50, 100, 80))
        wave_bg_rect = wave_bg.get_rect(topleft=(self.margin - 10, self.margin - 5))
        surface.blit(wave_bg, wave_bg_rect)

        # Wave border with color based on timer
        border_color = timer_color if time_remaining <= 10 else self.accent_color
        pygame.draw.rect(surface, border_color, wave_bg_rect, width=2, border_radius=5)

        # Draw wave text
        wave_rect = wave_surface.get_rect(topleft=(self.margin, self.margin))
        surface.blit(wave_surface, wave_rect)

        # Draw timer text below wave
        if timer_surface:
            timer_rect = timer_surface.get_rect(topleft=(self.margin, self.margin + wave_surface.get_height() + 5))
            surface.blit(timer_surface, timer_rect)

    def _draw_animated_bar(self, surface, x, y, ratio, color, label):
        """Draw an animated progress bar with modern styling."""
        # Background
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(surface, self.bg_color, bg_rect, border_radius=self.bar_height//2)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, width=2, border_radius=self.bar_height//2)

        # Fill with gradient effect
        if ratio > 0:
            fill_width = int(self.bar_width * ratio)
            fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)

            # Create gradient surface
            gradient_surface = pygame.Surface((fill_width, self.bar_height))
            for i in range(fill_width):
                gradient_ratio = i / fill_width if fill_width > 0 else 0
                gradient_color = tuple(int(c * (0.7 + 0.3 * gradient_ratio)) for c in color)
                pygame.draw.line(gradient_surface, gradient_color, (i, 0), (i, self.bar_height))

            surface.blit(gradient_surface, fill_rect)

            # Shine effect
            if ratio > 0.1:
                shine_width = max(2, fill_width // 10)
                shine_x = x + fill_width - shine_width
                shine_rect = pygame.Rect(shine_x, y + 2, shine_width, self.bar_height - 4)
                shine_color = tuple(min(255, c + 80) for c in color)
                pygame.draw.rect(surface, shine_color, shine_rect, border_radius=2)

        # Label
        label_surface = self.tiny_font.render(label, True, self.primary_color)
        surface.blit(label_surface, (x, y - 18))

        # Percentage
        percentage = f"{int(ratio * 100)}%"
        perc_surface = self.tiny_font.render(percentage, True, self.primary_color)
        perc_rect = perc_surface.get_rect(right=x + self.bar_width, centery=y + self.bar_height//2)
        surface.blit(perc_surface, perc_rect)

    def draw_weapon_status(self, surface, weapon_system):
        """Draw active weapon status with better positioning."""
        status_list = weapon_system.get_weapon_status()
        if not status_list:
            return

        # Position on left side, below bars, with better spacing
        y_start = self.screen_height - 180
        for i, status in enumerate(status_list):
            color = {
                "RAPID FIRE": POWERUP_RAPID_FIRE_COLOR,
                "TRIPLE SHOT": POWERUP_TRIPLE_COLOR,
                "DAMAGE BOOST": POWERUP_DAMAGE_COLOR
            }.get(status, self.accent_color)

            status_surface = self.small_font.render(status, True, color)

            # Background with glow
            bg_width = status_surface.get_width() + 16
            bg_height = status_surface.get_height() + 8
            bg_rect = pygame.Rect(self.margin, y_start - i * 35, bg_width, bg_height)

            # Glow effect
            glow_surface = pygame.Surface((bg_width + 4, bg_height + 4), pygame.SRCALPHA)
            glow_surface.fill((*color, 30))
            glow_rect = glow_surface.get_rect(center=bg_rect.center)
            surface.blit(glow_surface, glow_rect)

            # Background
            pygame.draw.rect(surface, (20, 20, 40, 100), bg_rect, border_radius=5)
            pygame.draw.rect(surface, color, bg_rect, width=2, border_radius=5)

            # Text
            text_rect = status_surface.get_rect(center=bg_rect.center)
            surface.blit(status_surface, text_rect)

    def draw_minimap(self, surface, player, enemies):
        """Draw an enhanced mini-map with better positioning."""
        if not enemies:
            return

        # Minimap properties - moved to avoid overlap
        minimap_size = 140
        minimap_x = self.screen_width - minimap_size - self.margin
        minimap_y = self.screen_height - minimap_size - self.margin
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)

        # Background with border
        minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap_surface.fill((0, 20, 40, 150))
        pygame.draw.rect(minimap_surface, self.accent_color,
                        minimap_surface.get_rect(), width=3, border_radius=8)

        # Grid lines for tech look
        grid_color = (50, 100, 150, 100)
        for i in range(0, minimap_size, 20):
            pygame.draw.line(minimap_surface, grid_color[:3], (i, 0), (i, minimap_size))
            pygame.draw.line(minimap_surface, grid_color[:3], (0, i), (minimap_size, i))

        # Player position (center bottom)
        player_x = minimap_size // 2
        player_y = minimap_size - 15
        pygame.draw.circle(minimap_surface, self.success_color, (player_x, player_y), 4)
        pygame.draw.circle(minimap_surface, self.primary_color, (player_x, player_y), 2)

        # Enemy positions
        for enemy in enemies[:12]:  # Limit for clarity
            map_x = int((enemy.int_x / self.screen_width) * minimap_size)
            map_y = int((enemy.int_y / self.screen_height) * minimap_size)

            if 0 <= map_x < minimap_size and 0 <= map_y < minimap_size:
                # Different colors for different enemy types
                enemy_color = self.warning_color if hasattr(enemy, 'is_boss') and enemy.is_boss else (255, 150, 50)
                pygame.draw.circle(minimap_surface, enemy_color, (map_x, map_y), 3)

        surface.blit(minimap_surface, minimap_rect)

        # Minimap label with modern styling
        label_bg = pygame.Surface((80, 20), pygame.SRCALPHA)
        label_bg.fill((0, 50, 100, 120))
        label_bg_rect = label_bg.get_rect(centerx=minimap_rect.centerx, bottom=minimap_rect.top - 5)
        surface.blit(label_bg, label_bg_rect)

        label = self.small_font.render("RADAR", True, self.accent_color)
        label_rect = label.get_rect(center=label_bg_rect.center)
        surface.blit(label, label_rect)
