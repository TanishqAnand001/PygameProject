"""
Power-up system for enhanced gameplay mechanics.
"""
import pygame
import random
import math
from config.settings import *


class PowerUp:
    """Individual power-up collectible with visual effects."""

    def __init__(self, x, y, powerup_type):
        """Initialize a power-up."""
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.lifetime = POWERUP_LIFETIME
        self.max_lifetime = POWERUP_LIFETIME
        self.active = True

        # Visual properties
        self.size = 20
        self.pulse_timer = 0
        self.rotation = 0
        self.float_offset = 0
        self.float_speed = 3.0
        self.blink_visible = True  # Initialize blink visibility

        # Color based on type
        self.colors = {
            "rapid_fire": POWERUP_RAPID_FIRE_COLOR,
            "shield_boost": POWERUP_SHIELD_COLOR,
            "damage_boost": POWERUP_DAMAGE_COLOR,
            "speed_boost": POWERUP_SPEED_COLOR,
            "triple_shot": POWERUP_TRIPLE_COLOR
        }
        self.color = self.colors.get(powerup_type, (255, 255, 255))

        # Collection area
        self.rect = pygame.Rect(x - self.size, y - self.size, self.size * 2, self.size * 2)

    def update(self, dt):
        """Update power-up animation and lifetime."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return False

        # Floating animation
        self.float_offset = math.sin(self.pulse_timer * self.float_speed) * 5

        # Rotation animation
        self.rotation += 90 * dt  # 90 degrees per second

        # Pulsing effect
        self.pulse_timer += dt

        # Blink when about to expire
        if self.lifetime < 2.0:
            self.blink_visible = (self.lifetime * 4) % 1 > 0.5
        else:
            self.blink_visible = True

        # Update position
        self.rect.center = (self.x, self.y + self.float_offset)

        return True

    def draw(self, surface):
        """Draw the power-up with effects."""
        if not self.blink_visible:
            return

        # Calculate alpha based on lifetime
        alpha_ratio = min(1.0, self.lifetime / 2.0)

        # Draw outer glow
        glow_size = self.size + 10 + math.sin(self.pulse_timer * 2) * 3
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_color = (*self.color, int(50 * alpha_ratio))
        pygame.draw.circle(glow_surface, glow_color[:3], (glow_size, glow_size), glow_size)

        glow_rect = glow_surface.get_rect(center=(self.x, self.y + self.float_offset))
        surface.blit(glow_surface, glow_rect)

        # Draw main power-up shape (diamond/square rotated)
        points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            px = self.x + math.cos(angle) * self.size
            py = self.y + self.float_offset + math.sin(angle) * self.size
            points.append((px, py))

        pygame.draw.polygon(surface, self.color, points)

        # Draw inner highlight
        inner_points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            px = self.x + math.cos(angle) * (self.size * 0.6)
            py = self.y + self.float_offset + math.sin(angle) * (self.size * 0.6)
            inner_points.append((px, py))

        highlight_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.polygon(surface, highlight_color, inner_points)

        # Draw type indicator (first letter)
        font = pygame.font.Font(None, 24)
        letter = self.powerup_type[0].upper()
        text = font.render(letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y + self.float_offset))
        surface.blit(text, text_rect)


class PowerUpManager:
    """Manages power-up spawning and collection."""

    def __init__(self):
        """Initialize the power-up manager."""
        self.powerups = []
        self.active_effects = {}  # Track active power-up effects

    def try_spawn_powerup(self, x, y):
        """Try to spawn a power-up at the given location."""
        if random.random() < POWERUP_SPAWN_CHANCE:
            powerup_type = random.choice(POWERUP_TYPES)
            powerup = PowerUp(x, y, powerup_type)
            self.powerups.append(powerup)
            return True
        return False

    def update(self, dt):
        """Update all power-ups."""
        # Update existing power-ups
        self.powerups = [p for p in self.powerups if p.update(dt)]

        # Update active effects timers
        expired_effects = []
        for effect_type, remaining_time in self.active_effects.items():
            remaining_time -= dt
            if remaining_time <= 0:
                expired_effects.append(effect_type)
            else:
                self.active_effects[effect_type] = remaining_time

        # Remove expired effects
        for effect in expired_effects:
            del self.active_effects[effect]

    def check_collection(self, player_rect):
        """Check if player collected any power-ups."""
        collected = []
        for powerup in self.powerups[:]:
            if powerup.rect.colliderect(player_rect):
                collected.append(powerup.powerup_type)
                self.activate_effect(powerup.powerup_type)
                self.powerups.remove(powerup)
        return collected

    def activate_effect(self, powerup_type):
        """Activate a power-up effect."""
        durations = {
            "rapid_fire": WEAPON_RAPID_FIRE_DURATION,
            "shield_boost": 0,  # Instant effect
            "damage_boost": WEAPON_DAMAGE_BOOST_DURATION,
            "speed_boost": WEAPON_SPEED_BOOST_DURATION,
            "triple_shot": WEAPON_TRIPLE_SHOT_DURATION
        }

        if powerup_type in durations and durations[powerup_type] > 0:
            # Add or extend effect duration
            if powerup_type in self.active_effects:
                self.active_effects[powerup_type] += durations[powerup_type]
            else:
                self.active_effects[powerup_type] = durations[powerup_type]

    def is_effect_active(self, effect_type):
        """Check if an effect is currently active."""
        return effect_type in self.active_effects

    def get_effect_time_remaining(self, effect_type):
        """Get remaining time for an effect."""
        return self.active_effects.get(effect_type, 0)

    def draw(self, surface):
        """Draw all power-ups."""
        for powerup in self.powerups:
            powerup.draw(surface)

    def clear_all(self):
        """Clear all power-ups and effects."""
        self.powerups.clear()
        self.active_effects.clear()
