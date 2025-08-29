import pygame
import math
import random


class Enemy:
    """A basic enemy ship with geometric design."""

    def __init__(self, x, y, enemy_type="basic"):
        """
        Initialize an enemy.
        Args:
            x, y: Starting position
            enemy_type: Type of enemy ("basic", "fast", "heavy")
        """
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.active = True

        # Set properties based on enemy type
        if enemy_type == "basic":
            self.speed = 100
            self.health = 1
            self.size = 15
            self.color = (255, 100, 100)  # Red
            self.score_value = 10
        elif enemy_type == "fast":
            self.speed = 180
            self.health = 1
            self.size = 12
            self.color = (100, 255, 100)  # Green
            self.score_value = 20
        elif enemy_type == "heavy":
            self.speed = 60
            self.health = 3
            self.size = 20
            self.color = (100, 100, 255)  # Blue
            self.score_value = 30

        # Movement properties
        self.direction_x = 0
        self.direction_y = 1  # Move downward
        self.wobble_timer = random.uniform(0, math.pi * 2)
        self.wobble_amplitude = 30
        self.original_x = x

        # Visual properties
        self.rotation = 0
        self.rotation_speed = random.uniform(-180, 180)  # Degrees per second

        # Cache integer coordinates
        self.int_x = int(x)
        self.int_y = int(y)

    def update(self, dt, screen_width, screen_height):
        """
        Update enemy position and behavior.
        Args:
            dt: Delta time in seconds
            screen_width, screen_height: Screen boundaries
        Returns:
            bool: True if enemy is still active
        """
        # Update wobble movement
        self.wobble_timer += dt * 2
        wobble_offset = math.sin(self.wobble_timer) * self.wobble_amplitude

        # Update position
        self.x = self.original_x + wobble_offset
        self.y += self.speed * dt

        # Update rotation
        self.rotation += self.rotation_speed * dt
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

        # Cache integer coordinates
        self.int_x = int(self.x)
        self.int_y = int(self.y)

        # Check if enemy has moved off screen
        if self.y > screen_height + 50:
            self.active = False

        return self.active

    def draw(self, surface):
        """Draw the enemy with geometric design."""
        if not self.active:
            return

        # Create enemy surface for rotation
        enemy_size = self.size * 2 + 10
        enemy_surface = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
        center = enemy_size // 2

        # Draw based on enemy type
        if self.enemy_type == "basic":
            # Triangle enemy
            points = [
                (center, center - self.size),
                (center - self.size, center + self.size),
                (center + self.size, center + self.size)
            ]
            pygame.draw.polygon(enemy_surface, self.color, points)
            pygame.draw.polygon(enemy_surface, (255, 255, 255), points, 2)

        elif self.enemy_type == "fast":
            # Diamond enemy
            points = [
                (center, center - self.size),
                (center + self.size, center),
                (center, center + self.size),
                (center - self.size, center)
            ]
            pygame.draw.polygon(enemy_surface, self.color, points)
            pygame.draw.polygon(enemy_surface, (255, 255, 255), points, 2)

        elif self.enemy_type == "heavy":
            # Hexagon enemy
            points = []
            for i in range(6):
                angle = (i * math.pi * 2) / 6
                x = center + self.size * math.cos(angle)
                y = center + self.size * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(enemy_surface, self.color, points)
            pygame.draw.polygon(enemy_surface, (255, 255, 255), points, 2)

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(enemy_surface, self.rotation)

        # Blit to main surface
        rect = rotated_surface.get_rect(center=(self.int_x, self.int_y))
        surface.blit(rotated_surface, rect)

    def take_damage(self, damage=1):
        """
        Apply damage to the enemy.
        Args:
            damage: Amount of damage to apply
        Returns:
            bool: True if enemy was destroyed
        """
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True
        return False

    def get_rect(self):
        """Get collision rectangle for the enemy."""
        return pygame.Rect(self.int_x - self.size, self.int_y - self.size,
                          self.size * 2, self.size * 2)
