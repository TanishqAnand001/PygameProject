import pygame
import math
import random
from config.settings import *
from systems.particle_engine import ParticleEngine
from systems.weapon_system import WeaponSystem
from effects.shockwave import Shockwave


class Player(pygame.sprite.Sprite):
    """
    Enhanced player spaceship with power-up integration and advanced weapon systems.
    """

    def __init__(self, screen_width, screen_height):
        """Initialize the enhanced player sprite."""
        super().__init__()

        # --- Player Appearance ---
        self.base_image = self._create_ship_surface()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(screen_width / 2, screen_height - 100))

        # --- Screen Boundaries ---
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- Physics Properties ---
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # --- Movement Constants (can be modified by power-ups) ---
        self.base_acceleration = PLAYER_ACCELERATION
        self.base_max_speed = PLAYER_MAX_SPEED
        self.ACCELERATION_RATE = self.base_acceleration
        self.MAX_SPEED = self.base_max_speed
        self.FRICTION_RATE = PLAYER_FRICTION

        # --- Animation Properties ---
        self.current_tilt = 0.0
        self.target_tilt = 0.0
        self.tilt_speed = PLAYER_TILT_SPEED
        self.max_tilt = PLAYER_MAX_TILT

        # --- Enhanced Particle System ---
        self.particle_engine = ParticleEngine(max_particles=MAX_PARTICLES)
        self.thruster_on = False
        self.particle_spawn_timer = 0.0
        self.particle_spawn_rate = THRUSTER_PARTICLE_SPAWN_RATE
        self.thrust_direction = pygame.math.Vector2(0, 0)

        # Cache for rotated images
        self.rotated_images_cache = {}
        self.cache_precision = 5

        # --- Enhanced Shield System ---
        self.shield_active = False
        self.shield_energy = 100.0
        self.max_shield_energy = 100.0
        self.shield_recharge_rate = 15.0
        self.shield_drain_rate = 25.0
        self.shield_pulse_timer = 0.0
        self.shield_opacity = 150
        self.shield_radius = 45
        self.last_shield_hit = 0.0

        # --- Shockwave System ---
        self.shockwaves = []
        self.shockwave_max_radius = 150

        # --- Enhanced Weapon System ---
        self.weapon_system = WeaponSystem(self)

        # --- Health System ---
        self.health = 100
        self.max_health = 100

        # --- Power-up Effects ---
        self.speed_boost_active = False
        self.invulnerability_timer = 0  # Brief invulnerability after taking damage

    def apply_powerup_effects(self, powerup_manager):
        """Apply active power-up effects to player."""
        # Speed boost
        if powerup_manager.is_effect_active("speed_boost"):
            if not self.speed_boost_active:
                self.ACCELERATION_RATE = self.base_acceleration * 1.5
                self.MAX_SPEED = self.base_max_speed * 1.3
                self.speed_boost_active = True
        else:
            if self.speed_boost_active:
                self.ACCELERATION_RATE = self.base_acceleration
                self.MAX_SPEED = self.base_max_speed
                self.speed_boost_active = False

        # Shield boost (instant effect)
        if powerup_manager.is_effect_active("shield_boost"):
            self.shield_energy = min(self.max_shield_energy, self.shield_energy + 50)
            # Remove the effect after applying
            if "shield_boost" in powerup_manager.active_effects:
                del powerup_manager.active_effects["shield_boost"]

        # Update weapon system
        self.weapon_system.update_power_effects(powerup_manager)

    def take_damage(self, damage):
        """Take damage with invulnerability frames."""
        if self.invulnerability_timer > 0:
            return False

        self.health -= damage
        self.invulnerability_timer = 1.0  # 1 second of invulnerability

        # Create damage effect
        self.particle_engine.create_explosion(
            self.rect.centerx, self.rect.centery, 8
        )

        return self.health <= 0  # Return True if player died

    def heal(self, amount):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)

    def _create_ship_surface(self):
        """Creates an optimized concentric circles ship design."""
        size = 70
        ship_surface = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()

        # Pre-computed colors for concentric circles
        outer_color = (30, 100, 130)        # Dark Cyan (outermost)
        main_color = (60, 200, 255)         # Bright Cyan (main body)
        inner_color = (100, 220, 255)       # Light Cyan (inner ring)
        core_color = (180, 240, 255)        # Very Light Cyan (core)
        accent_color = (255, 255, 255)      # White (center ring)

        center_x, center_y = size // 2, size // 2

        # Define circle radii from largest to smallest
        radii = [
            (32, outer_color),      # Outermost ring
            (26, main_color),       # Main body
            (20, inner_color),      # Inner ring
            (14, core_color),       # Core ring
        ]

        # Draw concentric circles from largest to smallest
        for radius, color in radii:
            pygame.draw.circle(ship_surface, color, (center_x, center_y), radius)

        # Draw hollow center circle (ring only, not filled)
        pygame.draw.circle(ship_surface, accent_color, (center_x, center_y), 8, 2)  # 2-pixel wide ring

        # Add geometric accent details
        # Small directional indicators on the outer ring
        accent_radius = 28
        for angle_deg in [0, 90, 180, 270]:  # Cardinal directions
            angle_rad = math.radians(angle_deg)
            x = center_x + accent_radius * math.cos(angle_rad)
            y = center_y + accent_radius * math.sin(angle_rad)
            pygame.draw.circle(ship_surface, accent_color, (int(x), int(y)), 3)

        # Add smaller accent points on diagonal directions
        for angle_deg in [45, 135, 225, 315]:  # Diagonal directions
            angle_rad = math.radians(angle_deg)
            x = center_x + 24 * math.cos(angle_rad)
            y = center_y + 24 * math.sin(angle_rad)
            pygame.draw.circle(ship_surface, accent_color, (int(x), int(y)), 2)

        # Add a central directional indicator (pointing up)
        pygame.draw.circle(ship_surface, outer_color, (center_x, center_y - 4), 2)

        return ship_surface

    def _update_tilt_animation(self, dt, keys):
        """Updates the ship's tilt animation with optimizations."""
        # Determine target tilt
        if keys[pygame.K_a]:
            self.target_tilt = -self.max_tilt
        elif keys[pygame.K_d]:
            self.target_tilt = self.max_tilt
        else:
            self.target_tilt = 0.0

        # Optimized interpolation
        tilt_diff = self.target_tilt - self.current_tilt
        if abs(tilt_diff) > 0.1:
            tilt_change = self.tilt_speed * dt
            self.current_tilt += max(-tilt_change, min(tilt_change, tilt_diff))
        else:
            self.current_tilt = self.target_tilt

    def _update_thruster_animation(self, dt, keys):
        """Updates thruster animation with optimized particle spawning."""
        # Determine thrust direction
        thrust_input = pygame.math.Vector2(0, 0)
        if keys[pygame.K_a]:
            thrust_input.x = -1
        if keys[pygame.K_d]:
            thrust_input.x = 1
        if keys[pygame.K_w]:
            thrust_input.y = -1
        if keys[pygame.K_s]:
            thrust_input.y = 1

        # Thruster activates when any movement key is pressed
        self.thruster_on = thrust_input.length() > 0

        if self.thruster_on:
            # Normalize thrust direction
            thrust_input.normalize_ip()
            self.thrust_direction = thrust_input

            # Optimized particle spawning with rate limiting
            self.particle_spawn_timer += dt
            if self.particle_spawn_timer >= self.particle_spawn_rate:
                self.particle_spawn_timer = 0

                # Spawn fewer particles for better performance
                ship_x = self.rect.centerx
                ship_y = self.rect.centery

                opposite_x = -self.thrust_direction.x
                opposite_y = -self.thrust_direction.y

                # Reduced particle count for better performance
                self.particle_engine.create_thruster_burst(ship_x, ship_y, opposite_x, opposite_y, 3)

        # Update particle engine
        self.particle_engine.update(dt)

    def _create_rotated_image(self):
        """Creates rotated image with caching for performance."""
        if abs(self.current_tilt) < 0.1:
            return self.base_image.copy()

        # Round tilt to cache precision
        cache_key = round(self.current_tilt / self.cache_precision) * self.cache_precision

        # Check cache first
        if cache_key in self.rotated_images_cache:
            return self.rotated_images_cache[cache_key].copy()

        # Create new rotated image
        rotated = pygame.transform.rotate(self.base_image, -cache_key)

        # Cache the result (limit cache size)
        if len(self.rotated_images_cache) < 20:
            self.rotated_images_cache[cache_key] = rotated

        return rotated.copy()

    def _activate_shield(self, dt):
        """Activates the shield if enough energy is available."""
        if self.shield_energy > 0:
            self.shield_active = True
            self.shield_energy -= self.shield_drain_rate * dt

            # Shield pulse effect
            self.shield_pulse_timer += dt
            if self.shield_pulse_timer >= 0.1:  # Pulse every 100 ms
                self.shield_pulse_timer = 0
                self.shield_opacity = 255 if self.shield_opacity == 150 else 150  # Toggle opacity

    def _deactivate_shield(self, dt):
        """Deactivates the shield and recharges energy."""
        self.shield_active = False
        if self.shield_energy < self.max_shield_energy:
            self.shield_energy += self.shield_recharge_rate * dt

    def _update_shield_effects(self, dt):
        """Updates shield visual effects and timers."""
        self.last_shield_hit += dt

        # Reset shield opacity if not recently hit
        if self.last_shield_hit > 0.5:
            self.shield_opacity = 150

        # Ensure shield energy stays within bounds
        self.shield_energy = max(0, min(self.max_shield_energy, self.shield_energy))

    def draw_shield(self, screen):
        """Draw the shield visual effect."""
        if self.shield_active and self.shield_energy > 0:
            # Calculate shield color based on energy level
            energy_ratio = self.shield_energy / self.max_shield_energy

            if energy_ratio > 0.6:
                shield_color = (0, 255, 255)  # Cyan when healthy
            elif energy_ratio > 0.3:
                shield_color = (255, 255, 0)  # Yellow when moderate
            else:
                shield_color = (255, 100, 0)  # Orange when low

            # Create shield surface with transparency
            shield_surface = pygame.Surface((self.shield_radius * 2 + 10, self.shield_radius * 2 + 10), pygame.SRCALPHA)

            # Draw multiple rings for a layered effect
            for i in range(3):
                ring_radius = self.shield_radius - i * 3
                ring_opacity = self.shield_opacity - i * 30
                ring_color = (*shield_color, max(0, min(255, ring_opacity)))

                # Draw ring
                center = (shield_surface.get_width() // 2, shield_surface.get_height() // 2)
                pygame.draw.circle(shield_surface, ring_color[:3], center, ring_radius, 2)

            # Add geometric accent points on the shield
            if self.shield_pulse_timer % 0.2 < 0.1:  # Flickering effect
                for angle_deg in range(0, 360, 45):  # 8 points around shield
                    angle_rad = math.radians(angle_deg)
                    x = shield_surface.get_width() // 2 + (self.shield_radius - 5) * math.cos(angle_rad)
                    y = shield_surface.get_height() // 2 + (self.shield_radius - 5) * math.sin(angle_rad)
                    pygame.draw.circle(shield_surface, shield_color, (int(x), int(y)), 2)

            # Blit shield to screen
            shield_rect = shield_surface.get_rect(center=self.rect.center)
            screen.blit(shield_surface, shield_rect)

    def simulate_shield_hit(self):
        """Simulate a shield hit for testing/demonstration."""
        if self.shield_active:
            self.last_shield_hit = 0.0
            self.shield_opacity = 255  # Flash bright on hit

            # Create a shockwave expanding from the ship center
            shockwave = Shockwave(self.rect.centerx, self.rect.centery,
                                self.shockwave_max_radius, 0.8)
            self.shockwaves.append(shockwave)

            # Create impact particles
            for _ in range(12):  # More particles for bigger impact
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(40, 80)
                x = self.rect.centerx + self.shield_radius * 0.8 * math.cos(angle)
                y = self.rect.centery + self.shield_radius * 0.8 * math.sin(angle)
                self.particle_engine.create_spark_trail(x, y, math.cos(angle), math.sin(angle), 2)

    def _update_shockwaves(self, dt):
        """Update all active shockwaves."""
        self.shockwaves = [wave for wave in self.shockwaves if wave.update(dt)]

    def draw_shockwaves(self, screen):
        """Draw all active shockwaves."""
        for shockwave in self.shockwaves:
            shockwave.draw(screen)

    def get_bullets(self):
        """Get list of active bullets for collision detection."""
        return self.weapon_system.get_bullets()

    def update(self, dt):
        """
        Enhanced player update with weapon system integration.
        """
        keys = pygame.key.get_pressed()

        # --- Handle Input & Set Acceleration ---
        self.acceleration.x = 0
        self.acceleration.y = 0

        if keys[pygame.K_a]:
            self.acceleration.x = -1
        if keys[pygame.K_d]:
            self.acceleration.x = 1
        if keys[pygame.K_w]:
            self.acceleration.y = -1
        if keys[pygame.K_s]:
            self.acceleration.y = 1

        # --- Shield Control (moved to LEFT SHIFT) ---
        if keys[pygame.K_LSHIFT]:
            self._activate_shield(dt)
        else:
            self._deactivate_shield(dt)

        # --- Enhanced Weapon System Control ---
        if keys[pygame.K_SPACE]:
            self.weapon_system.try_shoot(dt)

        # --- Update Systems ---
        self._update_tilt_animation(dt, keys)
        self._update_thruster_animation(dt, keys)
        self._update_shield_effects(dt)
        self._update_shockwaves(dt)

        # Update weapon system
        self.weapon_system.update_bullets(dt, self.screen_width, self.screen_height)

        # Update invulnerability timer
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= dt

        # Create the final image with rotation and effects
        self.image = self._create_rotated_image()

        # Update rect to maintain center position
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        # --- Optimized Physics ---
        if self.acceleration.length_squared() > 0:
            self.acceleration.normalize_ip()
            self.velocity += self.acceleration * self.ACCELERATION_RATE * dt
        else:
            if self.velocity.length_squared() > 0:
                friction_magnitude = self.FRICTION_RATE * dt
                if self.velocity.length_squared() > friction_magnitude * friction_magnitude:
                    friction = -self.velocity.normalize() * friction_magnitude
                    self.velocity += friction
                else:
                    self.velocity.x = 0
                    self.velocity.y = 0

        # --- Limit Speed ---
        if self.velocity.length_squared() > self.MAX_SPEED * self.MAX_SPEED:
            self.velocity.scale_to_length(self.MAX_SPEED)

        # --- Update Position ---
        self.position += self.velocity * dt
        self.rect.center = (int(self.position.x), int(self.position.y))

        # --- Optimized Boundary Checking ---
        if self.rect.left < 0:
            self.rect.left = 0
            self.position.x = self.rect.centerx
            self.velocity.x = 0
        elif self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
            self.position.x = self.rect.centerx
            self.velocity.x = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.position.y = self.rect.centery
            self.velocity.y = 0
        elif self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.position.y = self.rect.centery
            self.velocity.y = 0

    def draw_particles(self, screen):
        """Draw thruster particles with optimization."""
        self.particle_engine.draw(screen)

    def get_particle_engine(self):
        """Get access to the particle engine for external use."""
        return self.particle_engine

    def get_performance_info(self):
        """Get performance information for debugging."""
        return {
            'cache_size': len(self.rotated_images_cache),
            'particle_info': self.particle_engine.get_performance_info()
        }
