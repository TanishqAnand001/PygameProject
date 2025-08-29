"""
Enhanced wave system with escalating difficulty, special events, and boss encounters.
"""
import pygame
import math
import random
from config.settings import *


class Wave:
    """Individual wave configuration with enhanced difficulty scaling."""

    def __init__(self, wave_number):
        """Initialize wave properties with enhanced scaling."""
        self.wave_number = wave_number
        self.enemies_to_spawn = self._calculate_enemy_count()
        self.enemies_spawned = 0
        self.spawn_rate = self._calculate_spawn_rate()
        self.enemy_speed_multiplier = self._calculate_speed_multiplier()
        self.enemy_health_multiplier = self._calculate_health_multiplier()
        self.is_boss_wave = (wave_number % WAVE_BOSS_FREQUENCY == 0)
        self.is_special_event = self._determine_special_event()
        self.completed = False

        # Enhanced difficulty modifiers
        self.elite_chance = min(0.4, wave_number * 0.03)
        self.formation_chance = min(0.5, wave_number * 0.04)
        self.special_spawn_chance = min(0.3, wave_number * 0.02)

    def _calculate_enemy_count(self):
        """Calculate number of enemies with better scaling."""
        if self.wave_number <= 5:
            base_count = 6 + self.wave_number * 2
        elif self.wave_number <= 10:
            base_count = 16 + (self.wave_number - 5) * 3
        else:
            base_count = 31 + (self.wave_number - 10) * 2

        # Add some randomization
        variation = random.randint(-2, 3)
        return max(5, base_count + variation)

    def _calculate_spawn_rate(self):
        """Calculate enemy spawn rate with smoother progression."""
        base_rate = 1.2
        if self.wave_number <= 3:
            return base_rate
        elif self.wave_number <= 8:
            return base_rate + (self.wave_number - 3) * 0.15
        else:
            return base_rate + 0.75 + (self.wave_number - 8) * 0.1

    def _calculate_speed_multiplier(self):
        """Calculate enemy speed multiplier with caps."""
        base_multiplier = 1.0
        if self.wave_number <= 5:
            return base_multiplier + (self.wave_number - 1) * 0.1
        else:
            return base_multiplier + 0.4 + (self.wave_number - 5) * 0.05

    def _calculate_health_multiplier(self):
        """Calculate enemy health multiplier."""
        if self.wave_number <= 3:
            return 1.0
        elif self.wave_number <= 8:
            return 1.0 + (self.wave_number - 3) * 0.15
        else:
            return 1.75 + (self.wave_number - 8) * 0.1

    def _determine_special_event(self):
        """Determine if this wave has a special event."""
        if self.is_boss_wave:
            return None

        # Special events start appearing from wave 4
        if self.wave_number < 4:
            return None

        event_chance = min(0.25, (self.wave_number - 3) * 0.03)
        if random.random() < event_chance:
            events = ["invasion", "elite_squad"]
            if self.wave_number >= 8:
                events.append("boss_rush")
            return random.choice(events)

        return None


class WaveManager:
    """Enhanced wave manager with special events and difficulty scaling."""

    def __init__(self, screen_width, screen_height):
        """Initialize enhanced wave manager."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_wave_number = 1
        self.current_wave = None
        self.wave_active = False
        self.wave_break_timer = 0
        self.spawn_timer = 0
        self.enemies_alive = []

        # Enhanced tracking
        self.special_event_timer = 0
        self.event_enemies = []
        self.minions_spawned = []
        self.split_enemies_pending = []

        # Wave transition effects
        self.wave_start_timer = 0
        self.wave_warning_shown = False
        self.difficulty_ramp_timer = 0

    def start_new_wave(self):
        """Start a new wave with enhanced features."""
        self.current_wave = Wave(self.current_wave_number)
        self.wave_active = True
        self.wave_break_timer = 0
        self.spawn_timer = 0
        self.wave_start_timer = 2.5  # Longer wave start display
        self.wave_warning_shown = False
        self.difficulty_ramp_timer = 0

        # Clear special tracking
        self.event_enemies.clear()
        self.split_enemies_pending.clear()

    def update(self, dt, enemy_spawner, notification_manager):
        """Enhanced wave system update."""
        if not self.wave_active:
            # Wave break period
            self.wave_break_timer += dt

            # Show wave warning with enemy type preview
            if self.wave_break_timer >= 1.0 and not self.wave_warning_shown:
                self._show_wave_preview(notification_manager, enemy_spawner)
                self.wave_warning_shown = True

            if self.wave_break_timer >= WAVE_BREAK_DURATION:
                self.start_new_wave()
                return

        if self.wave_active and self.current_wave:
            # Update wave start timer
            if self.wave_start_timer > 0:
                self.wave_start_timer -= dt

            # Handle special events
            if self.current_wave.is_special_event:
                self._handle_special_event(dt, enemy_spawner, notification_manager)

            # Regular enemy spawning
            elif (self.current_wave.enemies_spawned < self.current_wave.enemies_to_spawn and
                  self.wave_start_timer <= 0):
                self._handle_regular_spawning(dt, enemy_spawner)

            # Handle pending split enemies
            self._handle_split_enemies()

            # Handle minion spawning for spawner enemies
            self._handle_minion_spawning(dt, enemy_spawner)

            # Update all enemies with enhanced parameters
            self._update_enemies(dt)

            # Check wave completion
            if (self.current_wave.enemies_spawned >= self.current_wave.enemies_to_spawn and
                len(self.enemies_alive) == 0 and len(self.event_enemies) == 0):
                self._complete_wave(notification_manager)

    def _show_wave_preview(self, notification_manager, enemy_spawner):
        """Show preview of incoming wave with enemy types."""
        wave_info = f"Wave {self.current_wave_number}"

        if self.current_wave.is_boss_wave:
            notification_manager.add_notification(f"🔥 {wave_info} - BOSS INCOMING!", "warning", 3.0)
        elif self.current_wave.is_special_event:
            event_name = self.current_wave.is_special_event.replace('_', ' ').title()
            notification_manager.add_notification(f"⚡ {wave_info} - {event_name}!", "warning", 3.0)
        else:
            # Show enemy variety info
            variety = enemy_spawner.get_enemy_variety_for_wave(self.current_wave_number)
            if variety["elite_types"] > 0:
                notification_manager.add_notification(f"🌊 {wave_info} - Elite Enemies Detected!", "warning", 2.5)
            elif variety["advanced_types"] > 0:
                notification_manager.add_notification(f"🌊 {wave_info} - Advanced Hostiles!", "warning", 2.5)
            else:
                notification_manager.add_notification(f"🌊 {wave_info} - Incoming!", "info", 2.0)

    def _handle_special_event(self, dt, enemy_spawner, notification_manager):
        """Handle special event spawning."""
        self.special_event_timer += dt

        if self.special_event_timer >= 1.0 and not self.event_enemies:
            # Spawn special event enemies
            event_enemies = enemy_spawner.spawn_special_event(
                self.current_wave.is_special_event,
                self.current_wave_number,
                self.current_wave.enemy_speed_multiplier,
                self.current_wave.enemy_health_multiplier
            )

            self.event_enemies.extend(event_enemies)
            self.enemies_alive.extend(event_enemies)

            # Show event notification
            event_name = self.current_wave.is_special_event.replace('_', ' ').title()
            notification_manager.add_notification(f"🚨 {event_name} Active!", "warning", 4.0)

    def _handle_regular_spawning(self, dt, enemy_spawner):
        """Handle regular enemy spawning with enhanced patterns."""
        self.spawn_timer += dt
        spawn_interval = 1.0 / self.current_wave.spawn_rate

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0

            # Pass wave number to spawner for enemy type selection
            new_enemies = enemy_spawner.spawn_wave_enemy(
                self.current_wave.enemy_speed_multiplier,
                self.current_wave.enemy_health_multiplier,
                self.current_wave.is_boss_wave,
                self.current_wave_number
            )

            if new_enemies:
                self.enemies_alive.extend(new_enemies)
                self.current_wave.enemies_spawned += len(new_enemies)

    def _handle_split_enemies(self):
        """Handle enemies that split when destroyed."""
        for split_data in self.split_enemies_pending[:]:
            enemy, split_enemies = split_data
            if not enemy.active:  # Original enemy is destroyed
                self.enemies_alive.extend(split_enemies)
                self.split_enemies_pending.remove(split_data)

    def _handle_minion_spawning(self, dt, enemy_spawner):
        """Handle minion spawning from spawner enemies."""
        for enemy in self.enemies_alive:
            if (hasattr(enemy, 'spawn_minions') and enemy.spawn_minions and
                enemy.enemy_type == "spawner" and enemy.creation_time > 3.0):

                # Check if it's time to spawn a minion
                if len([e for e in self.enemies_alive if hasattr(e, 'is_minion')]) < 4:
                    if random.random() < 0.01:  # 1% chance per frame
                        minion = enemy_spawner._create_enemy(
                            enemy.x + random.randint(-30, 30),
                            enemy.y + random.randint(-20, 20),
                            "fast",
                            self.current_wave.enemy_speed_multiplier,
                            self.current_wave.enemy_health_multiplier * 0.5
                        )
                        minion.is_minion = True
                        minion.size = 8  # Smaller minions
                        minion.score_value = 5  # Less points
                        self.enemies_alive.append(minion)

    def _update_enemies(self, dt):
        """Update all enemies with enhanced AI."""
        player_pos = getattr(self, '_player_pos', None)

        for enemy in self.enemies_alive[:]:
            # Update with player position for AI
            if not enemy.update(dt, self.screen_width, self.screen_height, player_pos):
                self.enemies_alive.remove(enemy)
                continue

            # Handle enemy bullets vs player collision (would be done in game manager)
            # Handle special death effects
            if not enemy.active:
                self._handle_enemy_death(enemy)

        # Update event enemies
        for enemy in self.event_enemies[:]:
            if not enemy.update(dt, self.screen_width, self.screen_height, player_pos):
                self.event_enemies.remove(enemy)

    def _handle_enemy_death(self, enemy):
        """Handle special effects when enemies die."""
        # Handle splitter enemies
        if hasattr(enemy, 'split_on_death') and enemy.split_on_death:
            split_enemies = enemy.get_split_enemies()
            if split_enemies:
                # Add split enemies to pending list
                self.split_enemies_pending.append((enemy, split_enemies))

    def _complete_wave(self, notification_manager):
        """Complete the current wave with enhanced feedback."""
        self.wave_active = False
        self.current_wave_number += 1

        # Enhanced completion notifications
        if self.current_wave.is_boss_wave:
            notification_manager.add_notification("🏆 Boss Defeated! Legendary!", "achievement", 4.0)
        elif self.current_wave.is_special_event:
            notification_manager.add_notification("⚡ Special Event Completed!", "success", 3.0)
        else:
            notification_manager.add_notification(f"✅ Wave {self.current_wave_number - 1} Cleared!", "success", 2.0)

        # Difficulty milestone notifications
        if self.current_wave_number == 5:
            notification_manager.add_notification("🔥 Elite Enemies Unlocked!", "info", 3.0)
        elif self.current_wave_number == 10:
            notification_manager.add_notification("💀 Destroyer Class Detected!", "warning", 3.0)
        elif self.current_wave_number % 10 == 0:
            notification_manager.add_notification(f"🌟 Wave {self.current_wave_number - 1} Milestone!", "achievement", 3.0)

    def set_player_position(self, x, y):
        """Set player position for enemy AI targeting."""
        self._player_pos = (x, y)

    def remove_enemy(self, enemy):
        """Remove an enemy from tracking."""
        if enemy in self.enemies_alive:
            self.enemies_alive.remove(enemy)
        if enemy in self.event_enemies:
            self.event_enemies.remove(enemy)

    def get_wave_info(self):
        """Get current wave information for UI."""
        if not self.current_wave:
            return {
                'wave_number': self.current_wave_number,
                'in_break': True,
                'break_time_remaining': WAVE_BREAK_DURATION - self.wave_break_timer,
                'enemies_spawned': 0,
                'enemies_per_wave': 0,
                'is_boss_wave': False,
                'special_event': None
            }

        return {
            'wave_number': self.current_wave_number,
            'in_break': not self.wave_active,
            'break_time_remaining': max(0, WAVE_BREAK_DURATION - self.wave_break_timer),
            'enemies_spawned': self.current_wave.enemies_spawned,
            'enemies_per_wave': self.current_wave.enemies_to_spawn,
            'enemies_alive': len(self.enemies_alive),
            'is_boss_wave': self.current_wave.is_boss_wave,
            'special_event': self.current_wave.is_special_event,
            'difficulty_multipliers': {
                'speed': round(self.current_wave.enemy_speed_multiplier, 2),
                'health': round(self.current_wave.enemy_health_multiplier, 2),
                'spawn_rate': round(self.current_wave.spawn_rate, 2)
            }
        }

    def draw_wave_transition(self, surface, screen_width, screen_height):
        """Draw enhanced wave transition effects."""
        if self.wave_start_timer > 0:
            # Wave start announcement with better effects
            alpha = min(255, int(self.wave_start_timer * 200))

            # Create overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 20, 40, alpha // 3))
            surface.blit(overlay, (0, 0))

            # Wave text with glow effect
            font = pygame.font.Font(None, 80)
            wave_text = f"WAVE {self.current_wave_number}"

            if self.current_wave.is_boss_wave:
                wave_text += " - BOSS"
                color = (255, 100, 100)
            elif self.current_wave.is_special_event:
                event_name = self.current_wave.is_special_event.replace('_', ' ').upper()
                wave_text = f"SPECIAL EVENT\n{event_name}"
                color = (255, 200, 0)
            else:
                color = (100, 200, 255)

            # Draw with glow effect
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                glow_surface = font.render(wave_text, True, (*color, alpha // 4))
                glow_rect = glow_surface.get_rect(center=(screen_width//2 + offset[0],
                                                        screen_height//2 + offset[1]))
                surface.blit(glow_surface, glow_rect)

            # Main text
            text_surface = font.render(wave_text, True, (*color, alpha))
            text_rect = text_surface.get_rect(center=(screen_width//2, screen_height//2))
            surface.blit(text_surface, text_rect)

            # Difficulty indicators
            if self.current_wave_number > 1:
                diff_font = pygame.font.Font(None, 32)
                diff_text = f"Speed: {self.current_wave.enemy_speed_multiplier:.1f}x  Health: {self.current_wave.enemy_health_multiplier:.1f}x"
                diff_surface = diff_font.render(diff_text, True, (200, 200, 200, alpha))
                diff_rect = diff_surface.get_rect(center=(screen_width//2, screen_height//2 + 60))
                surface.blit(diff_surface, diff_rect)
