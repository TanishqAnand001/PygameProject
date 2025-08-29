"""
Enhanced power-up system with advanced visual effects and improved mechanics.
"""
import pygame
import random
import math
import time
from config.settings import *


class PowerUp:
    """Enhanced power-up collectible with spectacular visual effects."""

    def __init__(self, x, y, powerup_type):
        """Initialize an enhanced power-up."""
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.powerup_type = powerup_type
        self.lifetime = POWERUP_LIFETIME
        self.max_lifetime = POWERUP_LIFETIME
        self.active = True

        # Enhanced visual properties
        self.size = 24
        self.pulse_timer = 0
        self.rotation = 0
        self.float_offset = 0
        self.float_speed = 2.5
        self.blink_visible = True
        self.spawn_animation_timer = 0.5  # Spawn animation duration
        self.collection_animation_timer = 0

        # Advanced animation properties
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_speed = 2.0
        self.orbit_radius = 8
        self.energy_pulse_timer = 0
        self.particle_spawn_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # Energy field effect
        self.energy_rings = []
        self.spark_particles = []

        # Enhanced color schemes based on type
        self.color_schemes = {
            "rapid_fire": {
                "primary": (255, 100, 50),
                "secondary": (255, 200, 100),
                "glow": (255, 150, 0),
                "energy": (255, 80, 20)
            },
            "shield_boost": {
                "primary": (50, 150, 255),
                "secondary": (100, 200, 255),
                "glow": (0, 180, 255),
                "energy": (20, 120, 255)
            },
            "damage_boost": {
                "primary": (255, 50, 100),
                "secondary": (255, 100, 150),
                "glow": (255, 0, 100),
                "energy": (200, 20, 80)
            },
            "speed_boost": {
                "primary": (100, 255, 50),
                "secondary": (150, 255, 100),
                "glow": (80, 255, 0),
                "energy": (60, 200, 20)
            },
            "triple_shot": {
                "primary": (255, 200, 50),
                "secondary": (255, 255, 100),
                "glow": (255, 220, 0),
                "energy": (200, 180, 20)
            }
        }

        self.colors = self.color_schemes.get(powerup_type, self.color_schemes["rapid_fire"])
        self.color = self.colors["primary"]

        # Collection area with slight randomization
        collection_size = self.size + 8
        self.rect = pygame.Rect(x - collection_size, y - collection_size,
                               collection_size * 2, collection_size * 2)

        # Initialize energy rings
        for i in range(3):
            self.energy_rings.append({
                'radius': 5 + i * 8,
                'alpha': 100 - i * 30,
                'speed': 1.5 + i * 0.5,
                'phase': i * 2.1
            })

    def update(self, dt):
        """Enhanced update with advanced animations."""
        if not self.active:
            return False

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return False

        # Update all timers
        self.pulse_timer += dt
        self.energy_pulse_timer += dt * 3
        self.particle_spawn_timer += dt

        # Spawn animation (first 0.5 seconds)
        if self.spawn_animation_timer > 0:
            self.spawn_animation_timer -= dt
            spawn_progress = 1.0 - (self.spawn_animation_timer / 0.5)

            # Scale and rotation during spawn
            self.size = int(24 * spawn_progress)
            self.rotation = (1.0 - spawn_progress) * 720  # 2 full rotations

            # Energy burst effect during spawn
            if self.spawn_animation_timer <= 0:
                self._create_spawn_burst()

        # Advanced floating animation with orbital motion
        base_float = math.sin(self.pulse_timer * self.float_speed) * 8
        orbit_x = math.cos(self.orbit_angle) * self.orbit_radius
        orbit_y = math.sin(self.orbit_angle) * self.orbit_radius * 0.5

        self.float_offset = base_float
        self.x = self.original_x + orbit_x
        self.y = self.original_y + orbit_y + self.float_offset

        # Update orbit
        self.orbit_angle += self.orbit_speed * dt
        if self.orbit_angle > 2 * math.pi:
            self.orbit_angle -= 2 * math.pi

        # Enhanced rotation with acceleration
        rotation_speed = 90 + math.sin(self.pulse_timer * 2) * 30
        self.rotation += rotation_speed * dt

        # Energy field pulsing
        for ring in self.energy_rings:
            ring['phase'] += ring['speed'] * dt
            ring['radius'] = (5 + self.energy_rings.index(ring) * 8) + math.sin(ring['phase']) * 3

        # Create spark particles periodically
        if self.particle_spawn_timer >= 0.1:  # Every 0.1 seconds
            self._create_spark_particle()
            self.particle_spawn_timer = 0

        # Update spark particles
        for particle in self.spark_particles[:]:
            particle['lifetime'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] *= 0.95

            if particle['lifetime'] <= 0 or particle['alpha'] < 10:
                self.spark_particles.remove(particle)

        # Blink warning when about to expire
        if self.lifetime < 3.0:
            blink_speed = 4 + (3.0 - self.lifetime) * 2  # Faster as time runs out
            self.blink_visible = (self.lifetime * blink_speed) % 1 > 0.5
        else:
            self.blink_visible = True

        # Desperate shaking when about to expire
        if self.lifetime < 1.0:
            shake_intensity = (1.0 - self.lifetime) * 5
            self.shake_offset_x = math.sin(self.pulse_timer * 20) * shake_intensity
            self.shake_offset_y = math.cos(self.pulse_timer * 25) * shake_intensity

        # Update position
        self.rect.center = (int(self.x + self.shake_offset_x),
                           int(self.y + self.shake_offset_y))

        return True

    def _create_spawn_burst(self):
        """Create energy burst effect when powerup spawns."""
        for i in range(12):
            angle = (i / 12.0) * 2 * math.pi
            speed = random.uniform(80, 120)
            self.spark_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': 0.8,
                'alpha': 255,
                'color': self.colors['energy'],
                'size': random.uniform(2, 4)
            })

    def _create_spark_particle(self):
        """Create a single spark particle."""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 40)
        self.spark_particles.append({
            'x': self.x + random.uniform(-5, 5),
            'y': self.y + random.uniform(-5, 5),
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'lifetime': random.uniform(0.3, 0.6),
            'alpha': random.uniform(150, 255),
            'color': self.colors['secondary'],
            'size': random.uniform(1, 2)
        })

    def draw(self, surface):
        """Enhanced drawing with spectacular visual effects."""
        if not self.blink_visible:
            return

        current_x = self.x + self.shake_offset_x
        current_y = self.y + self.shake_offset_y

        # Calculate alpha based on lifetime and spawn animation
        alpha_ratio = min(1.0, self.lifetime / 3.0)
        spawn_alpha = 1.0 if self.spawn_animation_timer <= 0 else (1.0 - self.spawn_animation_timer / 0.5)
        final_alpha = alpha_ratio * spawn_alpha

        # Draw energy field rings
        self._draw_energy_rings(surface, current_x, current_y, final_alpha)

        # Draw outer energy glow with pulsing
        glow_intensity = 0.7 + math.sin(self.energy_pulse_timer) * 0.3
        glow_size = self.size + 15 + math.sin(self.pulse_timer * 3) * 5
        self._draw_glow_effect(surface, current_x, current_y, glow_size, glow_intensity, final_alpha)

        # Draw main powerup shape with enhanced geometry
        self._draw_main_shape(surface, current_x, current_y, final_alpha)

        # Draw inner core with energy effect
        self._draw_energy_core(surface, current_x, current_y, final_alpha)

        # Draw spark particles
        self._draw_spark_particles(surface, final_alpha)

        # Draw collection indicator when close to expiring
        if self.lifetime < 2.0:
            self._draw_urgency_indicator(surface, current_x, current_y, final_alpha)

        # Draw type symbol
        self._draw_type_symbol(surface, current_x, current_y, final_alpha)

    def _draw_energy_rings(self, surface, x, y, alpha):
        """Draw animated energy rings around the powerup."""
        for ring in self.energy_rings:
            ring_alpha = int(ring['alpha'] * alpha)
            if ring_alpha > 10:
                # Create ring surface
                ring_surface = pygame.Surface((ring['radius'] * 4, ring['radius'] * 4), pygame.SRCALPHA)
                ring_color = (*self.colors['energy'], ring_alpha)

                # Draw ring with thickness
                pygame.draw.circle(ring_surface, ring_color[:3],
                                 (ring['radius'] * 2, ring['radius'] * 2),
                                 int(ring['radius']), 2)

                ring_rect = ring_surface.get_rect(center=(int(x), int(y)))
                surface.blit(ring_surface, ring_rect)

    def _draw_glow_effect(self, surface, x, y, glow_size, intensity, alpha):
        """Draw enhanced glow effect."""
        glow_alpha = int(80 * intensity * alpha)
        if glow_alpha > 5:
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)

            # Multi-layer glow for depth
            for i in range(3):
                layer_size = glow_size - i * 5
                layer_alpha = glow_alpha // (i + 1)
                glow_color = (*self.colors['glow'], layer_alpha)

                if layer_size > 0:
                    pygame.draw.circle(glow_surface, glow_color[:3],
                                     (glow_size, glow_size), int(layer_size))

            glow_rect = glow_surface.get_rect(center=(int(x), int(y)))
            surface.blit(glow_surface, glow_rect)

    def _draw_main_shape(self, surface, x, y, alpha):
        """Draw the main powerup shape with enhanced geometry."""
        shape_alpha = int(255 * alpha)

        if self.powerup_type == "rapid_fire":
            # Dynamic flame-like shape
            self._draw_flame_shape(surface, x, y, shape_alpha)
        elif self.powerup_type == "shield_boost":
            # Hexagonal shield shape
            self._draw_shield_shape(surface, x, y, shape_alpha)
        elif self.powerup_type == "damage_boost":
            # Star burst shape
            self._draw_star_shape(surface, x, y, shape_alpha)
        elif self.powerup_type == "speed_boost":
            # Arrow/wing shape
            self._draw_arrow_shape(surface, x, y, shape_alpha)
        else:  # triple_shot
            # Triple diamond shape
            self._draw_triple_diamond(surface, x, y, shape_alpha)

    def _draw_flame_shape(self, surface, x, y, alpha):
        """Draw flame-like shape for rapid fire."""
        points = []
        for i in range(8):
            angle = math.radians(self.rotation + i * 45)
            # Vary radius for flame effect
            radius_mult = 1.0 + math.sin(self.pulse_timer * 4 + i) * 0.3
            radius = self.size * radius_mult
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))

        color = (*self.colors['primary'], alpha)
        pygame.draw.polygon(surface, color[:3], points)

    def _draw_shield_shape(self, surface, x, y, alpha):
        """Draw hexagonal shield shape."""
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            px = x + math.cos(angle) * self.size
            py = y + math.sin(angle) * self.size
            points.append((px, py))

        # Outer shield
        pygame.draw.polygon(surface, self.colors['primary'], points)
        # Inner shield
        inner_points = [(x + (px - x) * 0.6, y + (py - y) * 0.6) for px, py in points]
        pygame.draw.polygon(surface, self.colors['secondary'], inner_points)

    def _draw_star_shape(self, surface, x, y, alpha):
        """Draw star shape for damage boost."""
        points = []
        for i in range(10):
            angle = math.radians(self.rotation + i * 36)
            radius = self.size if i % 2 == 0 else self.size * 0.5
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))

        pygame.draw.polygon(surface, self.colors['primary'], points)

    def _draw_arrow_shape(self, surface, x, y, alpha):
        """Draw arrow/wing shape for speed boost."""
        # Dynamic arrow with speed lines
        arrow_points = [
            (x, y - self.size),
            (x + self.size * 0.7, y + self.size * 0.7),
            (x, y + self.size * 0.3),
            (x - self.size * 0.7, y + self.size * 0.7)
        ]
        pygame.draw.polygon(surface, self.colors['primary'], arrow_points)

    def _draw_triple_diamond(self, surface, x, y, alpha):
        """Draw triple diamond for triple shot."""
        for i in range(3):
            offset_x = (i - 1) * self.size * 0.6
            diamond_points = [
                (x + offset_x, y - self.size * 0.8),
                (x + offset_x + self.size * 0.5, y),
                (x + offset_x, y + self.size * 0.8),
                (x + offset_x - self.size * 0.5, y)
            ]
            alpha_val = alpha - i * 60
            if alpha_val > 0:
                color = (*self.colors['primary'], alpha_val)
                pygame.draw.polygon(surface, color[:3], diamond_points)

    def _draw_energy_core(self, surface, x, y, alpha):
        """Draw pulsing energy core."""
        core_size = self.size * 0.4 + math.sin(self.energy_pulse_timer * 2) * 3
        core_alpha = int(200 * alpha)

        if core_alpha > 10:
            pygame.draw.circle(surface, self.colors['secondary'],
                             (int(x), int(y)), int(core_size))
            pygame.draw.circle(surface, (255, 255, 255),
                             (int(x), int(y)), int(core_size * 0.5))

    def _draw_spark_particles(self, surface, alpha):
        """Draw floating spark particles."""
        for particle in self.spark_particles:
            particle_alpha = int(particle['alpha'] * alpha)
            if particle_alpha > 10:
                size = int(particle['size'])
                color = (*particle['color'], particle_alpha)
                pygame.draw.circle(surface, color[:3],
                                 (int(particle['x']), int(particle['y'])), size)

    def _draw_urgency_indicator(self, surface, x, y, alpha):
        """Draw urgency indicator when powerup is about to expire."""
        urgency = 1.0 - (self.lifetime / 2.0)
        indicator_size = self.size + 20 + math.sin(self.pulse_timer * 8) * 10 * urgency
        indicator_alpha = int(100 * urgency * alpha)

        if indicator_alpha > 10:
            pygame.draw.circle(surface, (255, 100, 100),
                             (int(x), int(y)), int(indicator_size), 3)

    def _draw_type_symbol(self, surface, x, y, alpha):
        """Draw enhanced type symbol."""
        symbols = {
            "rapid_fire": "⚡",
            "shield_boost": "🛡",
            "damage_boost": "💥",
            "speed_boost": "⚡",
            "triple_shot": "⋆"
        }

        symbol = symbols.get(self.powerup_type, "?")
        font = pygame.font.Font(None, 32)
        text_alpha = int(255 * alpha)

        # Text with outline for visibility
        outline_color = (0, 0, 0, text_alpha)
        main_color = (255, 255, 255, text_alpha)

        # Draw outline
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_text = font.render(symbol, True, outline_color[:3])
            outline_text.set_alpha(text_alpha)
            outline_rect = outline_text.get_rect(center=(int(x + offset[0]), int(y + offset[1])))
            surface.blit(outline_text, outline_rect)

        # Draw main text
        main_text = font.render(symbol, True, main_color[:3])
        main_text.set_alpha(text_alpha)
        main_rect = main_text.get_rect(center=(int(x), int(y)))
        surface.blit(main_text, main_rect)

    def trigger_collection_effect(self):
        """Trigger special effect when powerup is collected."""
        self.collection_animation_timer = 0.3
        # Create collection burst
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 200)
            self.spark_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': 1.0,
                'alpha': 255,
                'color': self.colors['glow'],
                'size': random.uniform(3, 6)
            })


class PowerUpManager:
    """Enhanced power-up manager with improved spawning and effects."""

    def __init__(self):
        """Initialize the enhanced power-up manager."""
        self.powerups = []
        self.active_effects = {}  # Track active power-up effects
        self.collection_effects = []  # Visual effects for collection
        self.spawn_effect_timer = 0

    def try_spawn_powerup(self, x, y):
        """Enhanced powerup spawning with visual effects."""
        if random.random() < POWERUP_SPAWN_CHANCE:
            powerup_type = random.choice(POWERUP_TYPES)
            powerup = PowerUp(x, y, powerup_type)
            self.powerups.append(powerup)

            # Create spawn effect
            self._create_spawn_effect(x, y)
            return True
        return False

    def _create_spawn_effect(self, x, y):
        """Create visual effect when powerup spawns."""
        effect = {
            'x': x,
            'y': y,
            'timer': 0.5,
            'max_timer': 0.5,
            'particles': []
        }

        # Create spawn particles
        for i in range(15):
            angle = (i / 15.0) * 2 * math.pi
            speed = random.uniform(60, 100)
            effect['particles'].append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': 0.6,
                'alpha': 255,
                'size': random.uniform(2, 4),
                'color': (100, 200, 255)  # Add default blue color for spawn particles
            })

        self.collection_effects.append(effect)

    def update(self, dt):
        """Enhanced update with visual effects."""
        # Update existing power-ups
        active_powerups = []
        for powerup in self.powerups:
            if powerup.update(dt):
                active_powerups.append(powerup)
        self.powerups = active_powerups

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

        # Update collection effects
        active_effects = []
        for effect in self.collection_effects:
            effect['timer'] -= dt
            if effect['timer'] > 0:
                # Update particles
                for particle in effect['particles'][:]:
                    particle['lifetime'] -= dt
                    particle['x'] += particle['vx'] * dt
                    particle['y'] += particle['vy'] * dt
                    particle['alpha'] *= 0.95

                    if particle['lifetime'] <= 0:
                        effect['particles'].remove(particle)

                active_effects.append(effect)

        self.collection_effects = active_effects

    def check_collection(self, player_rect):
        """Enhanced collection with visual feedback."""
        collected = []

        for powerup in self.powerups[:]:
            if powerup.rect.colliderect(player_rect):
                collected.append(powerup.powerup_type)

                # Trigger collection effect
                powerup.trigger_collection_effect()

                # Add effect duration
                effect_durations = {
                    "rapid_fire": WEAPON_RAPID_FIRE_DURATION,
                    "shield_boost": 0,  # Instant effect
                    "damage_boost": WEAPON_DAMAGE_BOOST_DURATION,
                    "speed_boost": WEAPON_SPEED_BOOST_DURATION,
                    "triple_shot": WEAPON_TRIPLE_SHOT_DURATION
                }

                duration = effect_durations.get(powerup.powerup_type, 5.0)
                if duration > 0:
                    self.active_effects[powerup.powerup_type] = duration

                # Create collection visual effect
                self._create_collection_effect(powerup.x, powerup.y, powerup.colors)

                self.powerups.remove(powerup)

        return collected

    def _create_collection_effect(self, x, y, colors):
        """Create enhanced collection effect."""
        effect = {
            'x': x,
            'y': y,
            'timer': 1.0,
            'max_timer': 1.0,
            'particles': [],
            'colors': colors
        }

        # Create collection burst
        for i in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 150)
            effect['particles'].append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.uniform(0.8, 1.2),
                'alpha': 255,
                'size': random.uniform(2, 5),
                'color': random.choice([colors['primary'], colors['secondary'], colors['glow']])
            })

        self.collection_effects.append(effect)

    def update_effects(self, dt):
        """Update active power-up effects."""
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

    def draw(self, surface):
        """Enhanced drawing with all visual effects."""
        # Draw collection effects first (behind powerups)
        for effect in self.collection_effects:
            for particle in effect['particles']:
                if particle['alpha'] > 10:
                    pygame.draw.circle(surface, particle['color'],
                                     (int(particle['x']), int(particle['y'])),
                                     int(particle['size']))

        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(surface)

    def get_active_effect_names(self):
        """Get list of currently active effect names."""
        return list(self.active_effects.keys())

    def clear_all_effects(self):
        """Clear all active effects."""
        self.active_effects.clear()

    def extend_effect_duration(self, effect_type, additional_time):
        """Extend the duration of an active effect."""
        if effect_type in self.active_effects:
            self.active_effects[effect_type] += additional_time

    def is_effect_active(self, effect_type):
        """Check if a specific power-up effect is currently active."""
        return effect_type in self.active_effects

    def remove_effect(self, effect_type):
        """Remove a specific active effect."""
        if effect_type in self.active_effects:
            del self.active_effects[effect_type]

    def get_effect_time_remaining(self, effect_type):
        """Get remaining time for a specific effect."""
        return self.active_effects.get(effect_type, 0.0)

    def add_effect(self, effect_type, duration):
        """Manually add an effect with specified duration."""
        self.active_effects[effect_type] = duration
