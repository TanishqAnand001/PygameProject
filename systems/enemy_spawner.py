import random
import math
from config.settings import *
from entities.enemy import Enemy


class EnemySpawner:
    """Enhanced enemy spawner with diverse enemy types and sophisticated patterns."""

    def __init__(self, screen_width, screen_height):
        """Initialize the enhanced enemy spawner."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Spawn configuration
        self.spawn_timer = 0.0
        self.formation_timer = 0.0
        self.elite_spawn_timer = 0.0

        # Enemy type definitions with unlock waves
        self.enemy_types = {
            # Basic enemies (available from wave 1)
            "basic": {"unlock_wave": 1, "weight": 1.0, "tier": "basic"},
            "fast": {"unlock_wave": 1, "weight": 0.8, "tier": "basic"},
            "heavy": {"unlock_wave": 2, "weight": 0.6, "tier": "basic"},

            # Advanced enemies
            "hunter": {"unlock_wave": 3, "weight": 0.4, "tier": "advanced"},
            "sniper": {"unlock_wave": 4, "weight": 0.3, "tier": "advanced"},
            "shielded": {"unlock_wave": 4, "weight": 0.4, "tier": "advanced"},
            "berserker": {"unlock_wave": 5, "weight": 0.3, "tier": "advanced"},

            # Elite enemies
            "phantom": {"unlock_wave": 6, "weight": 0.2, "tier": "elite"},
            "splitter": {"unlock_wave": 7, "weight": 0.25, "tier": "elite"},
            "spawner": {"unlock_wave": 8, "weight": 0.15, "tier": "elite"},
            "energy_vampire": {"unlock_wave": 8, "weight": 0.2, "tier": "elite"},

            # Boss enemies
            "mini_boss": {"unlock_wave": 5, "weight": 0.1, "tier": "boss"},
            "destroyer": {"unlock_wave": 10, "weight": 0.05, "tier": "boss"},
            "void_lord": {"unlock_wave": 12, "weight": 0.05, "tier": "boss"}
        }

        # Formation patterns
        self.formation_patterns = [
            "single", "line", "v_formation", "circle", "diamond", "wave", "spiral"
        ]

    def spawn_wave_enemy(self, speed_multiplier=1.0, health_multiplier=1.0, is_boss=False, wave_number=1):
        """
        Spawn enemies for the wave system with enhanced variety.
        Args:
            speed_multiplier: Multiplier for enemy speed
            health_multiplier: Multiplier for enemy health
            is_boss: Whether to spawn a boss enemy
            wave_number: Current wave number for unlocking enemy types
        Returns:
            list: List of new enemies
        """
        if is_boss:
            return self._spawn_boss_wave(speed_multiplier, health_multiplier, wave_number)
        else:
            # Determine spawn pattern based on wave number
            if wave_number >= 6 and random.random() < 0.3:
                return self._spawn_formation(speed_multiplier, health_multiplier, wave_number)
            elif wave_number >= 4 and random.random() < 0.2:
                return self._spawn_elite_group(speed_multiplier, health_multiplier, wave_number)
            else:
                return self._spawn_regular_enemy(speed_multiplier, health_multiplier, wave_number)

    def _spawn_boss_wave(self, speed_multiplier, health_multiplier, wave_number):
        """Spawn a boss with potential minions."""
        boss_types = self._get_available_boss_types(wave_number)
        if not boss_types:
            boss_types = ["mini_boss"]

        boss_type = random.choice(boss_types)

        # Spawn boss at top center
        x = self.screen_width // 2
        y = -80

        boss = Enemy(x, y, boss_type)
        boss.health = int(boss.health * health_multiplier * 1.5)  # Extra boss health
        boss.max_health = boss.health
        boss.speed *= speed_multiplier * 0.8  # Bosses are slightly slower
        boss.score_value *= 2  # Bosses give more points
        boss.is_boss = True

        enemies = [boss]

        # Some bosses spawn with escort
        if boss_type in ["destroyer", "void_lord"] and wave_number >= 8:
            escort_count = random.randint(2, 4)
            for i in range(escort_count):
                angle = (i * 2 * math.pi) / escort_count
                escort_x = x + math.cos(angle) * 120
                escort_y = y + math.sin(angle) * 60

                escort = Enemy(escort_x, escort_y, random.choice(["fast", "hunter"]))
                escort.health = int(escort.health * health_multiplier)
                escort.max_health = escort.health
                escort.speed *= speed_multiplier
                enemies.append(escort)

        return enemies

    def _spawn_formation(self, speed_multiplier, health_multiplier, wave_number):
        """Spawn enemies in formation patterns."""
        formation = random.choice(self.formation_patterns)
        enemy_type = self._select_enemy_type(wave_number, prefer_tier="basic")

        enemies = []
        formation_size = random.randint(3, 6)

        if formation == "line":
            # Horizontal line formation
            start_x = self.screen_width // 2 - (formation_size * 60) // 2
            y = random.randint(-100, -50)
            for i in range(formation_size):
                x = start_x + i * 60
                enemies.append(self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier))

        elif formation == "v_formation":
            # V-shaped formation
            center_x = self.screen_width // 2
            y = random.randint(-100, -50)
            for i in range(formation_size):
                offset = (i - formation_size // 2) * 40
                x = center_x + offset
                y_offset = abs(offset) * 0.5
                enemies.append(self._create_enemy(x, y - y_offset, enemy_type, speed_multiplier, health_multiplier))

        elif formation == "circle":
            # Circular formation
            center_x = self.screen_width // 2
            center_y = -50
            radius = 80
            for i in range(formation_size):
                angle = (i * 2 * math.pi) / formation_size
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                enemies.append(self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier))

        elif formation == "diamond":
            # Diamond formation
            center_x = self.screen_width // 2
            center_y = -50
            positions = [
                (0, -40), (-30, 0), (30, 0), (0, 40)
            ]
            for i, (dx, dy) in enumerate(positions[:formation_size]):
                x = center_x + dx
                y = center_y + dy
                enemies.append(self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier))

        elif formation == "wave":
            # Wave pattern
            start_x = 50
            y = random.randint(-100, -50)
            for i in range(formation_size):
                x = start_x + i * (self.screen_width - 100) / formation_size
                wave_offset = math.sin(i * 0.8) * 30
                enemies.append(self._create_enemy(x, y + wave_offset, enemy_type, speed_multiplier, health_multiplier))

        elif formation == "spiral":
            # Spiral formation
            center_x = self.screen_width // 2
            center_y = -50
            for i in range(formation_size):
                angle = i * 0.8
                radius = i * 15 + 20
                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius
                enemies.append(self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier))

        else:  # single
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(-100, -50)
            enemies.append(self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier))

        return enemies

    def _spawn_elite_group(self, speed_multiplier, health_multiplier, wave_number):
        """Spawn a small group of elite enemies."""
        elite_types = self._get_available_enemy_types(wave_number, tier="elite")
        if not elite_types:
            return self._spawn_regular_enemy(speed_multiplier, health_multiplier, wave_number)

        group_size = random.randint(1, 3)
        enemies = []

        for i in range(group_size):
            enemy_type = random.choice(elite_types)
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(-150, -50) - i * 80  # Stagger vertically

            enemy = self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier)
            enemies.append(enemy)

        return enemies

    def _spawn_regular_enemy(self, speed_multiplier, health_multiplier, wave_number):
        """Spawn a single regular enemy."""
        enemy_type = self._select_enemy_type(wave_number)
        x = random.randint(50, self.screen_width - 50)
        y = random.randint(-100, -50)

        return [self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier)]

    def _create_enemy(self, x, y, enemy_type, speed_multiplier, health_multiplier):
        """Create and configure an enemy."""
        enemy = Enemy(x, y, enemy_type)
        enemy.health = int(enemy.health * health_multiplier)
        enemy.max_health = enemy.health
        enemy.speed *= speed_multiplier

        # Add some randomization to make enemies more unique
        enemy.speed *= random.uniform(0.85, 1.15)
        if enemy.wobble_amplitude > 0:
            enemy.wobble_amplitude *= random.uniform(0.7, 1.3)
        enemy.rotation_speed *= random.uniform(0.8, 1.2)

        return enemy

    def _select_enemy_type(self, wave_number, prefer_tier=None):
        """Select an appropriate enemy type based on wave number and preferences."""
        available_types = self._get_available_enemy_types(wave_number, prefer_tier)

        # Create weighted selection based on wave number
        weights = []
        types = []

        for enemy_type in available_types:
            config = self.enemy_types[enemy_type]
            # Reduce weight for older enemy types as waves progress
            wave_factor = max(0.3, 1.0 - (wave_number - config["unlock_wave"]) * 0.1)
            weight = config["weight"] * wave_factor

            weights.append(weight)
            types.append(enemy_type)

        if not types:
            return "basic"

        return random.choices(types, weights=weights)[0]

    def _get_available_enemy_types(self, wave_number, tier=None):
        """Get list of enemy types available for the current wave."""
        available = []

        for enemy_type, config in self.enemy_types.items():
            if config["unlock_wave"] <= wave_number:
                if tier is None or config["tier"] == tier:
                    available.append(enemy_type)

        return available

    def _get_available_boss_types(self, wave_number):
        """Get available boss types for the current wave."""
        return self._get_available_enemy_types(wave_number, tier="boss")

    def spawn_special_event(self, event_type, wave_number, speed_multiplier=1.0, health_multiplier=1.0):
        """Spawn enemies for special events."""
        enemies = []

        if event_type == "invasion":
            # Spawn many weak enemies
            for i in range(12):
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(-200, -50) - i * 30
                enemy = self._create_enemy(x, y, "basic", speed_multiplier * 1.2, health_multiplier * 0.7)
                enemies.append(enemy)

        elif event_type == "elite_squad":
            # Spawn a group of elite enemies
            for i in range(4):
                elite_types = self._get_available_enemy_types(wave_number, tier="elite")
                if elite_types:
                    enemy_type = random.choice(elite_types)
                    x = 100 + i * (self.screen_width - 200) // 3
                    y = -100 - i * 50
                    enemy = self._create_enemy(x, y, enemy_type, speed_multiplier, health_multiplier * 1.2)
                    enemies.append(enemy)

        elif event_type == "boss_rush":
            # Spawn multiple mini-bosses
            boss_count = min(3, wave_number // 5)
            for i in range(boss_count):
                x = (i + 1) * self.screen_width // (boss_count + 1)
                y = -100 - i * 80
                enemy = self._create_enemy(x, y, "mini_boss", speed_multiplier, health_multiplier)
                enemies.append(enemy)

        return enemies

    def update(self, dt):
        """Legacy update method for compatibility."""
        return []

    def get_enemy_variety_for_wave(self, wave_number):
        """Get information about enemy variety for the current wave."""
        available = self._get_available_enemy_types(wave_number)
        return {
            "total_types": len(available),
            "basic_types": len(self._get_available_enemy_types(wave_number, "basic")),
            "advanced_types": len(self._get_available_enemy_types(wave_number, "advanced")),
            "elite_types": len(self._get_available_enemy_types(wave_number, "elite")),
            "boss_types": len(self._get_available_enemy_types(wave_number, "boss")),
            "available_types": available
        }
