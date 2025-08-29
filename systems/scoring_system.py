"""
Enhanced scoring system with combos, multipliers, and achievements.
"""
import pygame
import time
from config.settings import *


class ScoreManager:
    """Advanced scoring system with combos and multipliers."""

    def __init__(self):
        """Initialize the scoring system."""
        self.score = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.score_multiplier = 1.0
        self.last_kill_time = 0
        self.total_kills = 0
        self.wave_bonus = 0

        # Visual feedback
        self.score_popup_queue = []
        self.combo_display_timer = 0
        self.achievements_unlocked = []

        # Fonts for display
        self.combo_font = pygame.font.Font(None, 48)
        self.score_font = pygame.font.Font(None, 36)
        self.popup_font = pygame.font.Font(None, 32)

    def add_kill_score(self, base_score, enemy_type="normal"):
        """Add score for enemy kill with combo system."""
        current_time = time.time()

        # Check if this continues a combo
        if current_time - self.last_kill_time <= COMBO_DECAY_TIME:
            self.combo_count += 1
            self.combo_timer = COMBO_DISPLAY_DURATION
        else:
            self.combo_count = 1

        self.last_kill_time = current_time
        self.total_kills += 1

        # Calculate multiplier based on combo
        combo_multiplier = 1.0 + (self.combo_count - 1) * COMBO_BONUS_MULTIPLIER
        combo_multiplier = min(combo_multiplier, SCORE_MULTIPLIER_MAX)

        # Apply power-up multipliers
        final_multiplier = combo_multiplier * self.score_multiplier

        # Calculate final score
        final_score = int(base_score * final_multiplier)
        self.score += final_score

        # Add score popup
        self.add_score_popup(final_score, combo_multiplier > 1.0)

        # Check for achievements
        self._check_achievements()

        return final_score

    def add_wave_bonus(self, wave_number):
        """Add bonus score for completing a wave."""
        bonus = wave_number * 100
        self.wave_bonus += bonus
        self.score += bonus
        self.add_score_popup(bonus, special_text=f"Wave {wave_number} Bonus!")

    def add_score_popup(self, score, is_combo=False, special_text=None):
        """Add a visual score popup."""
        popup = {
            'score': score,
            'is_combo': is_combo,
            'special_text': special_text,
            'timer': 2.0,
            'y_offset': 0
        }
        self.score_popup_queue.append(popup)

    def update(self, dt):
        """Update scoring system timers and effects."""
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt

        # Check if combo should decay
        current_time = time.time()
        if current_time - self.last_kill_time > COMBO_DECAY_TIME:
            if self.combo_count > 1:  # Only reset if we had a combo
                self.combo_count = 0

        # Update score popups
        for popup in self.score_popup_queue[:]:
            popup['timer'] -= dt
            popup['y_offset'] += 50 * dt  # Float upward
            if popup['timer'] <= 0:
                self.score_popup_queue.remove(popup)

    def _check_achievements(self):
        """Check for unlocked achievements."""
        achievements = []

        # Combo achievements
        if self.combo_count == 5 and "combo_5" not in self.achievements_unlocked:
            achievements.append("5x Combo!")
            self.achievements_unlocked.append("combo_5")
        elif self.combo_count == 10 and "combo_10" not in self.achievements_unlocked:
            achievements.append("10x Combo Master!")
            self.achievements_unlocked.append("combo_10")
        elif self.combo_count == 20 and "combo_20" not in self.achievements_unlocked:
            achievements.append("20x Combo Legend!")
            self.achievements_unlocked.append("combo_20")

        # Kill count achievements
        if self.total_kills == 50 and "kills_50" not in self.achievements_unlocked:
            achievements.append("Destroyer - 50 Kills!")
            self.achievements_unlocked.append("kills_50")
        elif self.total_kills == 100 and "kills_100" not in self.achievements_unlocked:
            achievements.append("Annihilator - 100 Kills!")
            self.achievements_unlocked.append("kills_100")

        # Score achievements
        if self.score >= 10000 and "score_10k" not in self.achievements_unlocked:
            achievements.append("High Scorer - 10,000 Points!")
            self.achievements_unlocked.append("score_10k")
        elif self.score >= 50000 and "score_50k" not in self.achievements_unlocked:
            achievements.append("Elite Pilot - 50,000 Points!")
            self.achievements_unlocked.append("score_50k")

        # Add achievement popups
        for achievement in achievements:
            self.add_score_popup(0, special_text=achievement)

    def draw_score_effects(self, surface, screen_width, screen_height):
        """Draw combo displays and score popups."""
        # Draw combo indicator
        if self.combo_count > 1 and self.combo_timer > 0:
            combo_text = f"{self.combo_count}x COMBO!"
            alpha = min(255, int(self.combo_timer / COMBO_DISPLAY_DURATION * 255))

            # Create surface with alpha
            combo_surface = self.combo_font.render(combo_text, True, COMBO_TEXT_COLOR)
            combo_surface.set_alpha(alpha)

            # Position in upper center
            combo_rect = combo_surface.get_rect(center=(screen_width // 2, 100))
            surface.blit(combo_surface, combo_rect)

        # Draw score popups
        popup_y_start = screen_height // 2
        for i, popup in enumerate(self.score_popup_queue):
            if popup['special_text']:
                text = popup['special_text']
                color = UI_SUCCESS_COLOR
            else:
                if popup['is_combo']:
                    text = f"+{popup['score']} (COMBO!)"
                    color = COMBO_TEXT_COLOR
                else:
                    text = f"+{popup['score']}"
                    color = (255, 255, 255)

            alpha = min(255, int(popup['timer'] / 2.0 * 255))

            popup_surface = self.popup_font.render(text, True, color)
            popup_surface.set_alpha(alpha)

            y_pos = popup_y_start - popup['y_offset'] - i * 30
            popup_rect = popup_surface.get_rect(center=(screen_width - 150, y_pos))
            surface.blit(popup_surface, popup_rect)

    def get_stats(self):
        """Get current scoring statistics."""
        return {
            'score': self.score,
            'combo': self.combo_count,
            'multiplier': self.score_multiplier,
            'total_kills': self.total_kills,
            'enemies_defeated': self.total_kills,  # Alias for compatibility
            'achievements': len(self.achievements_unlocked),
            'powerups_collected': 0,  # Placeholder - would be tracked separately
            'accuracy': 85.0  # Placeholder - would be calculated from shots fired/hit
        }

    def reset(self):
        """Reset scoring for new game."""
        self.score = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.score_multiplier = 1.0
        self.last_kill_time = 0
        self.total_kills = 0
        self.wave_bonus = 0
        self.score_popup_queue.clear()
        # Keep achievements across games
