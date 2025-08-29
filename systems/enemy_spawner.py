import random
import math
from config.settings import *
from entities.enemy import Enemy


class EnemySpawner:
    """Enhanced enemy spawner that works with the wave system."""

    def __init__(self, screen_width, screen_height):
        """Initialize the enemy spawner."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Spawn configuration
        self.spawn_timer = 0.0
        self.base_spawn_interval = 2.0
        self.current_spawn_interval = self.base_spawn_interval

        # Enemy type probabilities (basic, fast, heavy)
        self.enemy_type_weights = {
            1: [0.8, 0.2, 0.0],    # Wave 1: mostly basic
            3: [0.6, 0.3, 0.1],    # Wave 3: introduce heavy
            5: [0.5, 0.3, 0.2],    # Wave 5: more variety
            10: [0.4, 0.4, 0.2],   # Wave 10+: balanced mix
        }

    def spawn_wave_enemy(self, speed_multiplier=1.0, health_multiplier=1.0, is_boss=False):
        """
        Spawn an enemy for the wave system.
        Args:
            speed_multiplier: Multiplier for enemy speed
            health_multiplier: Multiplier for enemy health
            is_boss: Whether to spawn a boss enemy
        Returns:
            list: List containing the new enemy
        """
        if is_boss:
            return self._spawn_boss_enemy(speed_multiplier, health_multiplier)
        else:
            return self._spawn_regular_enemy(speed_multiplier, health_multiplier)

    def _spawn_boss_enemy(self, speed_multiplier, health_multiplier):
        """Spawn a boss enemy."""
        # Spawn boss at top center
        x = self.screen_width // 2
        y = -50

        # Create boss enemy with enhanced stats
        boss = Enemy(x, y)
        boss.health *= int(health_multiplier * 3)  # Bosses have 3x health
        boss.max_health = boss.health
        boss.speed *= speed_multiplier * 0.7  # Bosses are slower
        boss.score_value *= 5  # Bosses give more points
        boss.size = 40  # Larger size for bosses
        boss.is_boss = True

        return [boss]

    def _spawn_regular_enemy(self, speed_multiplier, health_multiplier):
        """Spawn a regular enemy."""
        # Random spawn position at top of screen
        x = random.randint(50, self.screen_width - 50)
        y = random.randint(-100, -50)

        # Create enemy
        enemy = Enemy(x, y)
        enemy.health = int(enemy.health * health_multiplier)
        enemy.max_health = enemy.health
        enemy.speed *= speed_multiplier

        return [enemy]

    def update(self, dt):
        """
        Legacy update method for compatibility.
        Returns empty list since wave system handles spawning now.
        """
        return []

    def get_enemy_type_for_wave(self, wave_number):
        """Get appropriate enemy type weights for the wave."""
        for threshold in sorted(self.enemy_type_weights.keys(), reverse=True):
            if wave_number >= threshold:
                return self.enemy_type_weights[threshold]
        return self.enemy_type_weights[1]
