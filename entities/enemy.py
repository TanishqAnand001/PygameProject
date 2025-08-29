import pygame
import math
import random


class Enemy:
    """Enhanced enemy system with multiple types and advanced behaviors."""

    def __init__(self, x, y, enemy_type="basic"):
        """
        Initialize an enemy with enhanced variety and behaviors.
        Args:
            x, y: Starting position
            enemy_type: Type of enemy with many varieties
        """
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.active = True
        self.max_health = 1
        self.creation_time = 0

        # Advanced movement properties
        self.direction_x = 0
        self.direction_y = 1
        self.acceleration = 0
        self.max_speed = 0
        self.wobble_timer = random.uniform(0, math.pi * 2)
        self.wobble_amplitude = 0
        self.original_x = x
        self.target_x = x
        self.target_y = y
        self.ai_timer = 0
        self.ai_state = "moving"

        # Visual and combat properties
        self.rotation = 0
        self.rotation_speed = 0
        self.pulse_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.can_shoot = False
        self.shoot_timer = 0
        self.shoot_cooldown = 0
        self.bullets = []

        # Special abilities
        self.teleport_timer = 0
        self.split_on_death = False
        self.spawn_minions = False
        self.energy_drain = False
        self.phase_ability = False
        self.phase_timer = 0

        # Set properties based on enemy type
        self._initialize_enemy_type()

        # Cache coordinates
        self.int_x = int(x)
        self.int_y = int(y)

    def _initialize_enemy_type(self):
        """Initialize enemy properties based on type."""
        enemy_configs = {
            # Basic enemies
            "basic": {
                "speed": 80, "health": 1, "size": 15, "color": (255, 100, 100),
                "score": 10, "rotation_speed": 90, "wobble": 20
            },
            "fast": {
                "speed": 200, "health": 1, "size": 12, "color": (100, 255, 100),
                "score": 20, "rotation_speed": 180, "wobble": 40
            },
            "heavy": {
                "speed": 50, "health": 4, "size": 22, "color": (100, 100, 255),
                "score": 40, "rotation_speed": 60, "wobble": 10
            },

            # Advanced enemies
            "hunter": {
                "speed": 120, "health": 2, "size": 16, "color": (255, 150, 0),
                "score": 60, "rotation_speed": 120, "wobble": 0, "ai_targeting": True
            },
            "sniper": {
                "speed": 40, "health": 2, "size": 14, "color": (150, 0, 255),
                "score": 80, "rotation_speed": 45, "can_shoot": True, "shoot_cooldown": 2.5
            },
            "shielded": {
                "speed": 70, "health": 3, "size": 18, "color": (0, 200, 200),
                "score": 70, "rotation_speed": 90, "shield_active": True, "shield_timer": 8.0
            },
            "berserker": {
                "speed": 60, "health": 2, "size": 20, "color": (255, 0, 0),
                "score": 90, "rotation_speed": 200, "acceleration": 150
            },

            # Elite enemies
            "phantom": {
                "speed": 100, "health": 3, "size": 17, "color": (128, 0, 128),
                "score": 120, "phase_ability": True, "teleport_timer": 4.0
            },
            "splitter": {
                "speed": 90, "health": 2, "size": 19, "color": (255, 100, 255),
                "score": 100, "split_on_death": True, "rotation_speed": 150
            },
            "spawner": {
                "speed": 30, "health": 5, "size": 25, "color": (255, 255, 0),
                "score": 150, "spawn_minions": True, "wobble": 30
            },
            "energy_vampire": {
                "speed": 110, "health": 2, "size": 16, "color": (200, 0, 100),
                "score": 110, "energy_drain": True, "rotation_speed": 160
            },

            # Boss enemies
            "mini_boss": {
                "speed": 80, "health": 8, "size": 35, "color": (255, 200, 0),
                "score": 300, "can_shoot": True, "shoot_cooldown": 1.5, "shield_active": True
            },
            "destroyer": {
                "speed": 50, "health": 15, "size": 45, "color": (200, 0, 0),
                "score": 500, "can_shoot": True, "shoot_cooldown": 1.0, "spawn_minions": True
            },
            "void_lord": {
                "speed": 70, "health": 12, "size": 40, "color": (100, 0, 100),
                "score": 450, "phase_ability": True, "energy_drain": True, "can_shoot": True
            }
        }

        config = enemy_configs.get(self.enemy_type, enemy_configs["basic"])

        # Apply configuration
        self.speed = config["speed"]
        self.health = config["health"]
        self.max_health = self.health
        self.size = config["size"]
        self.color = config["color"]
        self.score_value = config["score"]
        self.rotation_speed = config.get("rotation_speed", 90)
        self.wobble_amplitude = config.get("wobble", 20)

        # Special abilities
        self.can_shoot = config.get("can_shoot", False)
        self.shoot_cooldown = config.get("shoot_cooldown", 2.0)
        self.shield_active = config.get("shield_active", False)
        self.shield_timer = config.get("shield_timer", 5.0)
        self.split_on_death = config.get("split_on_death", False)
        self.spawn_minions = config.get("spawn_minions", False)
        self.energy_drain = config.get("energy_drain", False)
        self.phase_ability = config.get("phase_ability", False)
        self.teleport_timer = config.get("teleport_timer", 5.0)
        self.acceleration = config.get("acceleration", 0)
        self.ai_targeting = config.get("ai_targeting", False)

    def update(self, dt, screen_width, screen_height, player_pos=None):
        """Enhanced update with advanced AI behaviors."""
        if not self.active:
            return False

        self.creation_time += dt
        self.ai_timer += dt
        self.pulse_timer += dt

        # Update special ability timers
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False

        if self.phase_timer > 0:
            self.phase_timer -= dt

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        # AI behavior updates
        self._update_ai_behavior(dt, player_pos, screen_width, screen_height)

        # Movement updates
        self._update_movement(dt)

        # Special ability updates
        self._update_special_abilities(dt, screen_width, screen_height)

        # Shooting behavior
        if self.can_shoot and self.shoot_timer <= 0 and player_pos:
            self._try_shoot(player_pos)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)

        # Update rotation
        self.rotation += self.rotation_speed * dt
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360

        # Cache coordinates
        self.int_x = int(self.x)
        self.int_y = int(self.y)

        # Check bounds
        if self.y > screen_height + 100 or self.y < -100:
            self.active = False

        return self.active

    def _update_ai_behavior(self, dt, player_pos, screen_width, screen_height):
        """Update AI targeting and behavior patterns."""
        if not player_pos or not hasattr(self, 'ai_targeting') or not self.ai_targeting:
            return

        player_x, player_y = player_pos

        # Hunter AI - tracks player
        if self.enemy_type == "hunter":
            if self.ai_timer > 0.5:  # Update target every 0.5 seconds
                self.target_x = player_x
                self.ai_timer = 0

        # Berserker AI - charges at player when close
        elif self.enemy_type == "berserker":
            distance = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
            if distance < 200 and self.ai_state == "moving":
                self.ai_state = "charging"
                self.speed += self.acceleration
                self.target_x = player_x
                self.target_y = player_y

    def _update_movement(self, dt):
        """Update enemy movement patterns."""
        # Basic downward movement
        self.y += self.speed * dt

        # Wobble movement
        if self.wobble_amplitude > 0:
            self.wobble_timer += dt * 2
            wobble_offset = math.sin(self.wobble_timer) * self.wobble_amplitude
            self.x = self.original_x + wobble_offset

        # AI targeting movement
        if hasattr(self, 'ai_targeting') and self.ai_targeting:
            # Move towards target
            dx = self.target_x - self.x
            if abs(dx) > 5:
                self.x += (dx / abs(dx)) * min(abs(dx), self.speed * dt * 0.5)

    def _update_special_abilities(self, dt, screen_width, screen_height):
        """Update special enemy abilities."""
        # Phantom teleportation
        if self.enemy_type == "phantom" and self.phase_ability:
            self.teleport_timer -= dt
            if self.teleport_timer <= 0:
                # Teleport to random position
                self.x = random.randint(50, screen_width - 50)
                self.teleport_timer = random.uniform(3.0, 6.0)
                self.phase_timer = 0.5  # Brief phase out effect

        # Spawner minion creation
        if (self.enemy_type == "spawner" and self.spawn_minions and
            self.creation_time > 2.0 and len(self.get_minions()) < 3):
            if random.random() < 0.02:  # 2% chance per frame
                self._spawn_minion()

    def _try_shoot(self, player_pos):
        """Attempt to shoot at player."""
        if self.shoot_timer > 0:
            return

        player_x, player_y = player_pos

        # Calculate direction to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance

            # Create bullet
            bullet = EnemyBullet(self.x, self.y, dx, dy)
            self.bullets.append(bullet)

            self.shoot_timer = self.shoot_cooldown

    def _spawn_minion(self):
        """Spawn a minion enemy."""
        # This would be handled by the game manager
        pass

    def get_minions(self):
        """Get list of active minions (placeholder)."""
        return []

    def draw(self, surface):
        """Enhanced drawing with special effects."""
        if not self.active:
            return

        # Phase effect
        if self.phase_timer > 0:
            alpha = int(128 * (self.phase_timer / 0.5))
        else:
            alpha = 255

        # Create enemy surface
        enemy_size = self.size * 2 + 20
        enemy_surface = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
        center = enemy_size // 2

        # Draw based on enemy type with enhanced visuals
        self._draw_enemy_shape(enemy_surface, center, alpha)

        # Special effects
        self._draw_special_effects(enemy_surface, center, alpha)

        # Rotate the surface
        rotated_surface = pygame.transform.rotate(enemy_surface, self.rotation)
        rotated_surface.set_alpha(alpha)

        # Draw to main surface
        rect = rotated_surface.get_rect(center=(self.int_x, self.int_y))
        surface.blit(rotated_surface, rect)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)

    def _draw_enemy_shape(self, surface, center, alpha):
        """Draw the main enemy shape based on type."""
        color = (*self.color, alpha) if alpha < 255 else self.color

        if self.enemy_type in ["basic", "hunter", "berserker"]:
            # Triangle variants
            if self.enemy_type == "hunter":
                # Sharp triangle with targeting reticle
                points = [
                    (center, center - self.size),
                    (center - self.size//2, center + self.size),
                    (center + self.size//2, center + self.size)
                ]
            elif self.enemy_type == "berserker":
                # Jagged triangle
                points = [
                    (center, center - self.size),
                    (center - self.size, center + self.size//2),
                    (center - self.size//2, center + self.size),
                    (center + self.size//2, center + self.size),
                    (center + self.size, center + self.size//2)
                ]
            else:
                # Basic triangle
                points = [
                    (center, center - self.size),
                    (center - self.size, center + self.size),
                    (center + self.size, center + self.size)
                ]
            pygame.draw.polygon(surface, color[:3], points)

        elif self.enemy_type in ["fast", "phantom", "energy_vampire"]:
            # Diamond variants
            if self.enemy_type == "phantom":
                # Hollow diamond
                points = [
                    (center, center - self.size),
                    (center + self.size, center),
                    (center, center + self.size),
                    (center - self.size, center)
                ]
                pygame.draw.polygon(surface, color[:3], points, 3)
            else:
                # Solid diamond
                points = [
                    (center, center - self.size),
                    (center + self.size, center),
                    (center, center + self.size),
                    (center - self.size, center)
                ]
                pygame.draw.polygon(surface, color[:3], points)

        elif self.enemy_type in ["heavy", "shielded", "splitter"]:
            # Hexagon variants
            points = []
            sides = 6 if self.enemy_type != "splitter" else 8
            for i in range(sides):
                angle = (i * math.pi * 2) / sides
                x = center + self.size * math.cos(angle)
                y = center + self.size * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, color[:3], points)

        elif self.enemy_type in ["sniper"]:
            # Cross shape
            pygame.draw.rect(surface, color[:3],
                           (center - self.size//4, center - self.size, self.size//2, self.size*2))
            pygame.draw.rect(surface, color[:3],
                           (center - self.size, center - self.size//4, self.size*2, self.size//2))

        elif self.enemy_type in ["spawner", "mini_boss", "destroyer", "void_lord"]:
            # Complex boss shapes
            if self.enemy_type == "spawner":
                # Star shape
                points = []
                for i in range(10):
                    angle = (i * math.pi * 2) / 10
                    radius = self.size if i % 2 == 0 else self.size // 2
                    x = center + radius * math.cos(angle)
                    y = center + radius * math.sin(angle)
                    points.append((x, y))
                pygame.draw.polygon(surface, color[:3], points)
            else:
                # Large hexagon with inner details
                outer_points = []
                inner_points = []
                for i in range(8):
                    angle = (i * math.pi * 2) / 8
                    x_outer = center + self.size * math.cos(angle)
                    y_outer = center + self.size * math.sin(angle)
                    x_inner = center + (self.size//2) * math.cos(angle)
                    y_inner = center + (self.size//2) * math.sin(angle)
                    outer_points.append((x_outer, y_outer))
                    inner_points.append((x_inner, y_inner))

                pygame.draw.polygon(surface, color[:3], outer_points)
                pygame.draw.polygon(surface, (255, 255, 255), inner_points, 2)

    def _draw_special_effects(self, surface, center, alpha):
        """Draw special visual effects."""
        # Shield effect
        if self.shield_active:
            shield_color = (0, 200, 255, alpha//2)
            pygame.draw.circle(surface, shield_color[:3], (center, center),
                             self.size + 8, 3)

        # Energy drain effect
        if self.energy_drain and self.enemy_type == "energy_vampire":
            pulse = math.sin(self.pulse_timer * 4) * 0.3 + 0.7
            glow_color = (200, 0, 100, int(alpha * pulse * 0.5))
            pygame.draw.circle(surface, glow_color[:3], (center, center),
                             int(self.size * 1.5 * pulse), 2)

        # Health indicator for damaged enemies
        if self.health < self.max_health and self.max_health > 1:
            health_ratio = self.health / self.max_health
            bar_width = self.size * 2
            bar_height = 4
            bar_x = center - bar_width // 2
            bar_y = center - self.size - 15

            # Background
            pygame.draw.rect(surface, (100, 100, 100),
                           (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int(bar_width * health_ratio)
            health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.7 else (0, 255, 0)
            pygame.draw.rect(surface, health_color,
                           (bar_x, bar_y, health_width, bar_height))

    def take_damage(self, damage=1):
        """Enhanced damage system with special effects."""
        if self.shield_active and self.shield_timer > 0:
            # Shield absorbs damage
            self.shield_timer -= damage * 0.5
            if self.shield_timer <= 0:
                self.shield_active = False
            return False

        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True
        return False

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.int_x - self.size, self.int_y - self.size,
                          self.size * 2, self.size * 2)

    def get_split_enemies(self):
        """Return smaller enemies when splitter dies."""
        if not self.split_on_death:
            return []

        smaller_enemies = []
        for i in range(2):
            angle = i * math.pi
            offset_x = math.cos(angle) * 30
            offset_y = math.sin(angle) * 30

            smaller = Enemy(self.x + offset_x, self.y + offset_y, "fast")
            smaller.size = self.size // 2
            smaller.health = 1
            smaller.score_value = self.score_value // 3
            smaller_enemies.append(smaller)

        return smaller_enemies


class EnemyBullet:
    """Enemy projectile system."""

    def __init__(self, x, y, dx, dy, speed=150):
        """Initialize enemy bullet."""
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.active = True
        self.size = 3
        self.color = (255, 100, 100)
        self.damage = 1

    def update(self, dt):
        """Update bullet position."""
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        # Remove if off screen
        if (self.x < -50 or self.x > 1250 or
            self.y < -50 or self.y > 850):
            self.active = False

    def draw(self, surface):
        """Draw the bullet."""
        if self.active:
            pygame.draw.circle(surface, self.color,
                             (int(self.x), int(self.y)), self.size)

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(self.x - self.size, self.y - self.size,
                          self.size * 2, self.size * 2)

