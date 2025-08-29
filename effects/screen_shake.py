"""
Enhanced screen shake system with multiple types and improved visual feedback.
"""
import pygame
import random
import math
import time
from config.settings import *


class ScreenShake:
    """Advanced screen shake system with multiple shake types and smooth interpolation."""

    def __init__(self):
        """Initialize the enhanced screen shake system."""
        self.shakes = []  # List of active shake effects
        self.trauma = 0.0  # Overall trauma level (0-1)
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.rotation_shake = 0
        self.zoom_shake = 1.0

        # Advanced shake properties
        self.frequency_timer = 0
        self.last_update_time = time.time()
        self.shake_reduction_rate = 3.0  # How fast shake decays

        # Noise parameters for smooth shake
        self.noise_x_offset = random.uniform(0, 1000)
        self.noise_y_offset = random.uniform(0, 1000)
        self.noise_rot_offset = random.uniform(0, 1000)

    def add_shake(self, intensity=15, duration=0.5, shake_type="normal"):
        """Add a shake effect with enhanced parameters."""
        shake_data = {
            'intensity': intensity,
            'duration': duration,
            'max_duration': duration,
            'type': shake_type,
            'frequency': self._get_shake_frequency(shake_type),
            'falloff': self._get_shake_falloff(shake_type),
            'id': random.randint(1000, 9999)
        }
        self.shakes.append(shake_data)

        # Add trauma based on intensity
        trauma_amount = min(0.8, intensity / 50.0)
        self.trauma = min(1.0, self.trauma + trauma_amount)

    def add_explosion_shake(self, distance_from_center, intensity=25, max_distance=400):
        """Enhanced explosion shake with distance-based intensity."""
        if distance_from_center < max_distance:
            distance_factor = 1.0 - (distance_from_center / max_distance)
            final_intensity = intensity * distance_factor * distance_factor  # Quadratic falloff

            # Different shake based on explosion size
            if final_intensity > 30:
                self.add_shake(final_intensity, 0.8, "explosion_large")
            elif final_intensity > 15:
                self.add_shake(final_intensity, 0.6, "explosion_medium")
            else:
                self.add_shake(final_intensity, 0.4, "explosion_small")

    def add_impact_shake(self, intensity=10, direction_x=0, direction_y=0):
        """Add directional impact shake."""
        shake_data = {
            'intensity': intensity,
            'duration': 0.3,
            'max_duration': 0.3,
            'type': "impact",
            'frequency': 20.0,
            'falloff': 'linear',
            'direction_x': direction_x,
            'direction_y': direction_y,
            'id': random.randint(1000, 9999)
        }
        self.shakes.append(shake_data)

    def add_continuous_shake(self, intensity=5, frequency=15.0):
        """Add continuous shake for things like engine vibration."""
        self.add_shake(intensity, 0.1, "continuous")

    def add_weapon_fire_shake(self, weapon_type="normal"):
        """Add weapon-specific shake effects."""
        shake_configs = {
            "normal": (3, 0.1),
            "rapid_fire": (2, 0.05),
            "triple_shot": (8, 0.15),
            "heavy": (12, 0.3)
        }
        intensity, duration = shake_configs.get(weapon_type, (3, 0.1))
        self.add_shake(intensity, duration, "weapon")

    def _get_shake_frequency(self, shake_type):
        """Get appropriate frequency for shake type."""
        frequencies = {
            "normal": 25.0,
            "explosion_small": 30.0,
            "explosion_medium": 20.0,
            "explosion_large": 15.0,
            "impact": 35.0,
            "weapon": 40.0,
            "continuous": 10.0
        }
        return frequencies.get(shake_type, 25.0)

    def _get_shake_falloff(self, shake_type):
        """Get appropriate falloff curve for shake type."""
        falloffs = {
            "normal": "exponential",
            "explosion_small": "quadratic",
            "explosion_medium": "quadratic",
            "explosion_large": "exponential",
            "impact": "linear",
            "weapon": "exponential",
            "continuous": "linear"
        }
        return falloffs.get(shake_type, "exponential")

    def update(self, dt):
        """Enhanced update with smooth interpolation and multiple shake types."""
        current_time = time.time()
        self.frequency_timer += dt

        # Update individual shakes
        active_shakes = []
        total_intensity = 0
        total_rotation = 0
        total_zoom_effect = 0

        for shake in self.shakes:
            shake['duration'] -= dt

            if shake['duration'] > 0:
                # Calculate shake progress and apply falloff
                progress = 1.0 - (shake['duration'] / shake['max_duration'])
                falloff_factor = self._calculate_falloff(progress, shake['falloff'])

                # Calculate current intensity
                current_intensity = shake['intensity'] * (1.0 - falloff_factor)
                total_intensity += current_intensity

                # Add rotation shake for large explosions
                if shake['type'] in ['explosion_large', 'explosion_medium']:
                    total_rotation += current_intensity * 0.1

                # Add zoom shake for impacts
                if shake['type'] == 'impact':
                    total_zoom_effect += current_intensity * 0.002

                active_shakes.append(shake)

        self.shakes = active_shakes

        # Decay trauma over time
        self.trauma = max(0, self.trauma - dt * self.shake_reduction_rate)

        # Calculate smooth shake using Perlin-like noise
        if total_intensity > 0 or self.trauma > 0:
            # Use frequency for smooth oscillation
            freq_mult = 30.0 + total_intensity * 0.5

            # Generate smooth noise-like movement
            noise_time = current_time * freq_mult

            # X and Y shake with different phases
            self.shake_offset_x = self._smooth_noise(
                noise_time + self.noise_x_offset
            ) * (total_intensity + self.trauma * 20)

            self.shake_offset_y = self._smooth_noise(
                noise_time + self.noise_y_offset + 100
            ) * (total_intensity + self.trauma * 20)

            # Rotation shake
            self.rotation_shake = self._smooth_noise(
                noise_time * 0.5 + self.noise_rot_offset
            ) * total_rotation * 0.5

            # Zoom shake
            self.zoom_shake = 1.0 + total_zoom_effect
        else:
            # Smooth return to zero
            self.shake_offset_x *= 0.9
            self.shake_offset_y *= 0.9
            self.rotation_shake *= 0.9
            self.zoom_shake = self.zoom_shake * 0.9 + 0.1

    def _calculate_falloff(self, progress, falloff_type):
        """Calculate falloff based on type."""
        if falloff_type == "linear":
            return progress
        elif falloff_type == "quadratic":
            return progress * progress
        elif falloff_type == "exponential":
            return 1.0 - math.exp(-progress * 3)
        else:
            return progress

    def _smooth_noise(self, t):
        """Generate smooth noise for natural shake movement."""
        # Combine multiple sine waves for complex motion
        return (
            math.sin(t) * 0.5 +
            math.sin(t * 2.3) * 0.3 +
            math.sin(t * 4.7) * 0.2 +
            math.sin(t * 8.1) * 0.1
        )

    def get_offset(self):
        """Get current shake offset with sub-pixel precision."""
        return (self.shake_offset_x, self.shake_offset_y)

    def get_rotation(self):
        """Get current rotation shake in degrees."""
        return self.rotation_shake

    def get_zoom_factor(self):
        """Get current zoom shake factor."""
        return self.zoom_shake

    def apply_to_surface(self, surface, target_surface):
        """Apply enhanced shake effects including rotation and zoom."""
        offset_x, offset_y = self.get_offset()
        rotation = self.get_rotation()
        zoom = self.get_zoom_factor()

        if abs(rotation) > 0.1 or abs(zoom - 1.0) > 0.001:
            # Apply rotation and zoom transformations
            center_x = surface.get_width() // 2
            center_y = surface.get_height() // 2

            # Create transformation matrix
            if abs(rotation) > 0.1:
                rotated_surface = pygame.transform.rotate(surface, rotation)
            else:
                rotated_surface = surface

            if abs(zoom - 1.0) > 0.001:
                new_width = int(rotated_surface.get_width() * zoom)
                new_height = int(rotated_surface.get_height() * zoom)
                scaled_surface = pygame.transform.scale(rotated_surface, (new_width, new_height))
            else:
                scaled_surface = rotated_surface

            # Calculate centering offset
            center_offset_x = (target_surface.get_width() - scaled_surface.get_width()) // 2
            center_offset_y = (target_surface.get_height() - scaled_surface.get_height()) // 2

            # Apply final position with shake offset
            final_x = center_offset_x + int(offset_x)
            final_y = center_offset_y + int(offset_y)

            target_surface.blit(scaled_surface, (final_x, final_y))
        else:
            # Simple offset for performance when no rotation/zoom
            target_surface.blit(surface, (int(offset_x), int(offset_y)))

    def is_shaking(self):
        """Check if currently shaking."""
        return len(self.shakes) > 0 or self.trauma > 0.01

    def get_intensity(self):
        """Get current total shake intensity for debugging."""
        return sum(shake['intensity'] for shake in self.shakes) + self.trauma * 20

    def clear_all_shakes(self):
        """Clear all active shakes - useful for cutscenes or pausing."""
        self.shakes.clear()
        self.trauma = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.rotation_shake = 0
        self.zoom_shake = 1.0
