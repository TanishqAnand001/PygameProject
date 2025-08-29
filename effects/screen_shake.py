"""
Screen shake system for dynamic visual feedback.
"""
import pygame
import random
import math
from config.settings import *


class ScreenShake:
    """Manages screen shake effects for visual impact."""

    def __init__(self):
        """Initialize the screen shake system."""
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.trauma = 0  # 0-1 trauma level for smooth shake

    def add_shake(self, intensity=None, duration=None):
        """Add screen shake with specified intensity and duration."""
        intensity = intensity or SCREEN_SHAKE_INTENSITY
        duration = duration or SCREEN_SHAKE_DURATION

        # Add trauma (accumulates for multiple explosions)
        self.trauma = min(1.0, self.trauma + intensity / 100.0)

        if self.shake_duration < duration:
            self.shake_duration = duration

    def add_explosion_shake(self, distance_from_center, max_distance=500):
        """Add shake based on explosion distance from screen center."""
        if distance_from_center < max_distance:
            # Closer explosions cause more shake
            intensity_factor = 1.0 - (distance_from_center / max_distance)
            intensity = SCREEN_SHAKE_INTENSITY * intensity_factor
            self.add_shake(intensity, SCREEN_SHAKE_DURATION * intensity_factor)

    def update(self, dt):
        """Update shake effect."""
        if self.shake_duration > 0:
            self.shake_duration -= dt

            # Decay trauma over time
            self.trauma = max(0, self.trauma - dt * 2)  # Decay rate

            if self.shake_duration <= 0:
                self.trauma = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                # Calculate shake based on trauma
                shake_power = self.trauma * self.trauma  # Quadratic falloff

                # Generate random shake offset
                max_offset = SCREEN_SHAKE_INTENSITY * shake_power
                self.shake_offset_x = random.uniform(-max_offset, max_offset)
                self.shake_offset_y = random.uniform(-max_offset, max_offset)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

    def get_offset(self):
        """Get current shake offset."""
        return (int(self.shake_offset_x), int(self.shake_offset_y))

    def apply_to_surface(self, surface, target_surface):
        """Apply shake effect by blitting with offset."""
        offset_x, offset_y = self.get_offset()
        target_surface.blit(surface, (offset_x, offset_y))

    def is_shaking(self):
        """Check if currently shaking."""
        return self.shake_duration > 0 or self.trauma > 0
