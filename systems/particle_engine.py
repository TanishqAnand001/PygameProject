import pygame
import random
import math
from config.settings import *
from effects.particle import Particle
from effects.thruster_particle import ThrusterParticle


class ParticleEngine:
    """Optimized particle engine with memory management."""

    def __init__(self, max_particles=1000):
        self.particles = []
        self.max_particles = max_particles
        self.dead_particles = []  # Reuse dead particles to reduce garbage collection
        self.frame_count = 0

    def add_particle(self, particle):
        """Add a particle with memory management."""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
        # If at limit, replace oldest particle
        elif self.particles:
            self.particles.pop(0)
            self.particles.append(particle)

    def create_thruster_burst(self, x, y, direction_x, direction_y, count=4):
        """Create optimized thruster particles."""
        for _ in range(min(count, self.max_particles - len(self.particles))):
            particle = ThrusterParticle(x, y, direction_x, direction_y)
            self.add_particle(particle)

    def create_explosion(self, x, y, count=15, speed_range=(50, 120)):
        """Create an optimized explosion effect."""
        count = min(count, self.max_particles - len(self.particles))
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_range[0], speed_range[1])
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed

            size = random.uniform(2, 5)
            life = random.uniform(0.5, 1.2)

            # Use pre-defined safe colors (RGB tuples)
            color = random.choice([THRUSTER_COLOR_HOT, THRUSTER_COLOR_WARM, BULLET_COLOR])

            particle = Particle(x, y, velocity_x, velocity_y, size, life, color, "circle")
            particle.fade_rate = 2.5
            particle.shrink_rate = 2.5
            self.add_particle(particle)

    def create_spark_trail(self, x, y, direction_x, direction_y, count=1):
        """Create spark trail particles."""
        for _ in range(min(count, self.max_particles - len(self.particles))):
            # Add some randomness to direction
            rand_x = direction_x + random.uniform(-0.2, 0.2)
            rand_y = direction_y + random.uniform(-0.2, 0.2)

            speed = random.uniform(30, 60)
            velocity_x = rand_x * speed
            velocity_y = rand_y * speed

            size = random.uniform(1, 3)
            life = random.uniform(0.3, 0.6)
            color = random.choice([BULLET_COLOR, THRUSTER_COLOR_WARM])

            particle = Particle(x, y, velocity_x, velocity_y, size, life, color, "circle")
            particle.fade_rate = 3.0
            particle.shrink_rate = 3.0
            self.add_particle(particle)

    def update(self, dt):
        """Update all particles with optimization."""
        self.frame_count += 1

        # Update particles in-place for better performance
        active_particles = []
        for particle in self.particles:
            if particle.update(dt):
                active_particles.append(particle)

        self.particles = active_particles

    def draw(self, screen):
        """Draw all particles with optimized rendering."""
        for particle in self.particles:
            particle.draw(screen)

    def get_performance_info(self):
        """Get performance information for debugging."""
        return {
            'active_particles': len(self.particles),
            'max_particles': self.max_particles,
            'frame_count': self.frame_count
        }

    def clear_all(self):
        """Clear all particles."""
        self.particles.clear()
