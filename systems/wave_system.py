"""
Dynamic wave system with escalating difficulty and boss encounters.
"""
import pygame
import math
import random
from config.settings import *


class Wave:
    """Individual wave configuration."""

    def __init__(self, wave_number):
        """Initialize wave properties."""
        self.wave_number = wave_number
        self.enemies_to_spawn = self._calculate_enemy_count()
        self.enemies_spawned = 0
        self.spawn_rate = self._calculate_spawn_rate()
        self.enemy_speed_multiplier = self._calculate_speed_multiplier()
        self.is_boss_wave = (wave_number % WAVE_BOSS_FREQUENCY == 0)
        self.completed = False

    def _calculate_enemy_count(self):
        """Calculate number of enemies for this wave."""
        base_count = 8
        return int(base_count * (WAVE_ENEMY_MULTIPLIER ** (self.wave_number - 1)))

    def _calculate_spawn_rate(self):
        """Calculate enemy spawn rate (enemies per second)."""
        base_rate = 1.5
        # Gradually increase spawn rate but cap it
        return min(4.0, base_rate + (self.wave_number - 1) * 0.1)

    def _calculate_speed_multiplier(self):
        """Calculate enemy speed multiplier."""
        return 1.0 + (self.wave_number - 1) * 0.15

    def get_enemy_health_multiplier(self):
        """Get health multiplier for enemies in this wave."""
        return 1.0 + (self.wave_number - 1) * 0.2


class WaveManager:
    """Manages wave progression and enemy spawning."""

    def __init__(self, screen_width, screen_height):
        """Initialize wave manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_wave_number = 1
        self.current_wave = None
        self.wave_active = False
        self.wave_break_timer = 0
        self.spawn_timer = 0
        self.enemies_alive = []

        # Wave transition effects
        self.wave_start_timer = 0
        self.wave_warning_shown = False

    def start_new_wave(self):
        """Start a new wave."""
        self.current_wave = Wave(self.current_wave_number)
        self.wave_active = True
        self.wave_break_timer = 0
        self.spawn_timer = 0
        self.wave_start_timer = 2.0  # 2 second wave start display
        self.wave_warning_shown = False

    def update(self, dt, enemy_spawner, notification_manager):
        """Update wave system."""
        if not self.wave_active:
            # Wave break period
            self.wave_break_timer += dt

            # Show wave warning
            if self.wave_break_timer >= 1.0 and not self.wave_warning_shown:
                notification_manager.add_wave_notification(self.current_wave_number)
                self.wave_warning_shown = True

            if self.wave_break_timer >= WAVE_BREAK_DURATION:
                self.start_new_wave()
                return

        if self.wave_active and self.current_wave:
            # Update wave start timer
            if self.wave_start_timer > 0:
                self.wave_start_timer -= dt

            # Spawn enemies during active wave
            if (self.current_wave.enemies_spawned < self.current_wave.enemies_to_spawn and
                self.wave_start_timer <= 0):
                self.spawn_timer += dt

                spawn_interval = 1.0 / self.current_wave.spawn_rate
                if self.spawn_timer >= spawn_interval:
                    self.spawn_timer = 0

                    # Spawn enemy with wave modifiers
                    new_enemies = enemy_spawner.spawn_wave_enemy(
                        self.current_wave.enemy_speed_multiplier,
                        self.current_wave.get_enemy_health_multiplier(),
                        self.current_wave.is_boss_wave and
                        self.current_wave.enemies_spawned == self.current_wave.enemies_to_spawn - 1
                    )

                    self.enemies_alive.extend(new_enemies)
                    self.current_wave.enemies_spawned += len(new_enemies)

            # Check if wave is completed
            if (self.current_wave.enemies_spawned >= self.current_wave.enemies_to_spawn and
                len(self.enemies_alive) == 0):
                self._complete_wave()

    def _complete_wave(self):
        """Complete the current wave."""
        self.current_wave.completed = True
        self.wave_active = False
        self.current_wave_number += 1
        self.wave_break_timer = 0

    def remove_enemy(self, enemy):
        """Remove an enemy from the alive list."""
        if enemy in self.enemies_alive:
            self.enemies_alive.remove(enemy)

    def get_wave_info(self):
        """Get current wave information for UI."""
        if not self.current_wave:
            return {
                "wave_number": self.current_wave_number,
                "in_break": True,
                "break_time_remaining": max(0, WAVE_BREAK_DURATION - self.wave_break_timer),
                "enemies_spawned": 0,
                "enemies_per_wave": 0,
                "enemies_remaining": 0
            }

        return {
            "wave_number": self.current_wave.wave_number,
            "in_break": False,
            "break_time_remaining": 0,
            "enemies_spawned": self.current_wave.enemies_spawned,
            "enemies_per_wave": self.current_wave.enemies_to_spawn,
            "enemies_remaining": len(self.enemies_alive)
        }

    def draw_wave_transition(self, surface, screen_width, screen_height):
        """Draw wave transition effects."""
        if self.wave_start_timer > 0:
            # Wave start announcement
            alpha = min(255, int(self.wave_start_timer / 2.0 * 255))

            # Create overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(150, alpha)))
            surface.blit(overlay, (0, 0))

            # Wave text
            font = pygame.font.Font(None, 72)
            if self.current_wave.is_boss_wave:
                text = f"BOSS WAVE {self.current_wave.wave_number}!"
                color = UI_WARNING_COLOR
            else:
                text = f"WAVE {self.current_wave.wave_number}"
                color = UI_ACCENT_COLOR

            wave_surface = font.render(text, True, color)
            wave_surface.set_alpha(alpha)
            wave_rect = wave_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            surface.blit(wave_surface, wave_rect)

            # Enemy count info
            info_font = pygame.font.Font(None, 36)
            info_text = f"Incoming: {self.current_wave.enemies_to_spawn} Enemies"
            info_surface = info_font.render(info_text, True, (255, 255, 255))
            info_surface.set_alpha(alpha)
            info_rect = info_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
            surface.blit(info_surface, info_rect)

    def reset(self):
        """Reset wave system for new game."""
        self.current_wave_number = 1
        self.current_wave = None
        self.wave_active = False
        self.wave_break_timer = 0
        self.spawn_timer = 0
        self.enemies_alive.clear()
        self.wave_start_timer = 0
        self.wave_warning_shown = False
