"""
Enhanced weapon system with multiple firing modes and power-ups.
"""
import pygame
import math
import random
from config.settings import *
from entities.bullet import Bullet


class WeaponSystem:
    """Advanced weapon system with multiple firing modes."""

    def __init__(self, player):
        """Initialize the weapon system."""
        self.player = player
        self.bullets = []
        self.shoot_timer = 0
        self.max_bullets = 30  # Increased bullet limit

        # Weapon modes
        self.rapid_fire_active = False
        self.triple_shot_active = False
        self.damage_boost_active = False

        # Firing rates
        self.normal_fire_rate = 0.15
        self.rapid_fire_rate = 0.05
        self.current_fire_rate = self.normal_fire_rate

        # Bullet properties
        self.bullet_damage = 1
        self.bullet_speed = 600
        self.boosted_damage = 2

    def update_power_effects(self, powerup_manager):
        """Update weapon based on active power-ups."""
        # Check rapid fire
        if powerup_manager.is_effect_active("rapid_fire"):
            self.rapid_fire_active = True
            self.current_fire_rate = self.rapid_fire_rate
        else:
            self.rapid_fire_active = False
            self.current_fire_rate = self.normal_fire_rate

        # Check triple shot
        self.triple_shot_active = powerup_manager.is_effect_active("triple_shot")

        # Check damage boost
        if powerup_manager.is_effect_active("damage_boost"):
            self.damage_boost_active = True
            self.bullet_damage = self.boosted_damage
        else:
            self.damage_boost_active = False
            self.bullet_damage = 1

    def try_shoot(self, dt):
        """Attempt to fire weapon."""
        self.shoot_timer += dt

        if self.shoot_timer >= self.current_fire_rate:
            self.shoot_timer = 0

            if len(self.bullets) < self.max_bullets:
                if self.triple_shot_active:
                    self._fire_triple_shot()
                else:
                    self._fire_single_shot()
                return True
        return False

    def _fire_single_shot(self):
        """Fire a single bullet."""
        bullet = self._create_bullet(
            self.player.rect.centerx,
            self.player.rect.top - 10,
            0, -1
        )
        self.bullets.append(bullet)

        # Muzzle flash effect
        self._create_muzzle_flash(self.player.rect.centerx, self.player.rect.top - 5)

    def _fire_triple_shot(self):
        """Fire three bullets in a spread pattern."""
        center_x = self.player.rect.centerx
        top_y = self.player.rect.top - 10

        # Center bullet
        bullet1 = self._create_bullet(center_x, top_y, 0, -1)

        # Left bullet (15 degree angle)
        angle_left = math.radians(-15)
        bullet2 = self._create_bullet(
            center_x - 5, top_y,
            math.sin(angle_left), -math.cos(angle_left)
        )

        # Right bullet (15 degree angle)
        angle_right = math.radians(15)
        bullet3 = self._create_bullet(
            center_x + 5, top_y,
            math.sin(angle_right), -math.cos(angle_right)
        )

        self.bullets.extend([bullet1, bullet2, bullet3])

        # Enhanced muzzle flash for triple shot
        self._create_muzzle_flash(center_x, top_y, count=5)

    def _create_bullet(self, x, y, dir_x, dir_y):
        """Create a bullet with current weapon properties."""
        bullet = Bullet(x, y, dir_x, dir_y, self.bullet_speed)
        bullet.damage = self.bullet_damage

        # Visual enhancement for boosted bullets
        if self.damage_boost_active:
            bullet.color = (255, 100, 0)  # Orange for damage boost
            bullet.size = 6  # Larger bullets
        elif self.rapid_fire_active:
            bullet.color = (255, 0, 255)  # Magenta for rapid fire

        return bullet

    def _create_muzzle_flash(self, x, y, count=3):
        """Create muzzle flash particles."""
        for _ in range(count):
            self.player.particle_engine.create_spark_trail(
                x + random.uniform(-3, 3),
                y,
                random.uniform(-0.3, 0.3),
                -1,
                1
            )

    def update_bullets(self, dt, screen_width, screen_height):
        """Update all bullets."""
        for bullet in self.bullets:
            bullet.update(dt, screen_width, screen_height)

        # Remove inactive bullets
        self.bullets = [bullet for bullet in self.bullets if bullet.active]

    def draw_bullets(self, surface):
        """Draw all bullets."""
        for bullet in self.bullets:
            bullet.draw(surface)

    def get_bullets(self):
        """Get list of active bullets."""
        return self.bullets

    def clear_bullets(self):
        """Clear all bullets."""
        self.bullets.clear()

    def get_weapon_status(self):
        """Get current weapon status for UI display."""
        status = []
        if self.rapid_fire_active:
            status.append("RAPID FIRE")
        if self.triple_shot_active:
            status.append("TRIPLE SHOT")
        if self.damage_boost_active:
            status.append("DAMAGE BOOST")
        return status
