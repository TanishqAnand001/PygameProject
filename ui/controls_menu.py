import pygame


class ControlsMenu:
    """Displays game controls and instructions."""

    def __init__(self, screen_width, screen_height):
        """
        Initialize the controls menu.
        Args:
            screen_width, screen_height: Screen dimensions
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False

        # Font setup
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.bg_color = (0, 0, 30, 180)  # Semi-transparent dark blue
        self.title_color = (255, 255, 100)  # Yellow
        self.header_color = (100, 200, 255)  # Light blue
        self.text_color = (255, 255, 255)   # White
        self.accent_color = (255, 100, 100) # Red for warnings

        # Create background surface
        self.background = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.background.fill(self.bg_color)

        # Control mappings
        self.controls = {
            "Movement": [
                ("W", "Move Up"),
                ("A", "Move Left"),
                ("S", "Move Down"),
                ("D", "Move Right")
            ],
            "Combat": [
                ("SPACE", "Shoot Bullets"),
                ("LEFT SHIFT", "Activate Shield")
            ],
            "Game Controls": [
                ("ESC", "Quit Game"),
                ("P", "Pause Game"),
                ("C", "Toggle Controls Menu"),
                ("F1", "Toggle Debug Info")
            ],
            "Ship Features": [
                ("Automatic", "Thruster Particles"),
                ("Automatic", "Banking Animation"),
                ("Energy Based", "Shield System"),
                ("On Impact", "Shockwave Effects")
            ]
        }

    def toggle_visibility(self):
        """Toggle the visibility of the controls menu."""
        self.visible = not self.visible

    def draw(self, screen):
        """Draw the controls menu if visible."""
        if not self.visible:
            return

        # Draw semi-transparent background
        screen.blit(self.background, (0, 0))

        # Calculate layout
        menu_width = 800
        menu_height = 600
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2

        # Draw menu background
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, (20, 20, 50), menu_rect)
        pygame.draw.rect(screen, (100, 150, 255), menu_rect, 3)

        # Draw title
        title_text = self.title_font.render("GAME CONTROLS", True, self.title_color)
        title_rect = title_text.get_rect(centerx=self.screen_width // 2, y=menu_y + 20)
        screen.blit(title_text, title_rect)

        # Draw controls sections
        current_y = menu_y + 80
        col_width = (menu_width - 60) // 2
        left_col_x = menu_x + 30
        right_col_x = menu_x + 30 + col_width + 20

        sections = list(self.controls.items())

        # Left column
        for i in range(0, len(sections), 2):
            if i < len(sections):
                current_y = self._draw_section(screen, sections[i][0], sections[i][1],
                                             left_col_x, current_y, col_width)

        # Right column
        current_y = menu_y + 80
        for i in range(1, len(sections), 2):
            if i < len(sections):
                current_y = self._draw_section(screen, sections[i][0], sections[i][1],
                                             right_col_x, current_y, col_width)

        # Draw footer
        footer_y = menu_y + menu_height - 60
        footer_text = self.small_font.render("Press C to close this menu", True, self.accent_color)
        footer_rect = footer_text.get_rect(centerx=self.screen_width // 2, y=footer_y)
        screen.blit(footer_text, footer_rect)

        # Game info
        info_text = self.small_font.render("Geometric Space Shooter v1.0", True, self.text_color)
        info_rect = info_text.get_rect(centerx=self.screen_width // 2, y=footer_y + 25)
        screen.blit(info_text, info_rect)

    def _draw_section(self, screen, section_name, controls_list, x, y, width):
        """
        Draw a section of controls.
        Args:
            screen: Surface to draw on
            section_name: Name of the control section
            controls_list: List of (key, action) tuples
            x, y: Position to draw at
            width: Width of the section
        Returns:
            int: New Y position after drawing
        """
        # Draw section header
        header_text = self.header_font.render(section_name, True, self.header_color)
        screen.blit(header_text, (x, y))
        y += 40

        # Draw underline
        pygame.draw.line(screen, self.header_color, (x, y - 5), (x + width - 20, y - 5), 2)

        # Draw controls
        for key, action in controls_list:
            # Draw key
            key_text = self.text_font.render(f"{key}:", True, self.title_color)
            screen.blit(key_text, (x + 10, y))

            # Draw action
            action_text = self.text_font.render(action, True, self.text_color)
            screen.blit(action_text, (x + 120, y))

            y += 30

        return y + 20  # Add some spacing after section


class HUD:
    """Heads-Up Display for game information."""

    def __init__(self, screen_width, screen_height):
        """Initialize the HUD."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.text_color = (255, 255, 255)
        self.warning_color = (255, 100, 100)
        self.good_color = (100, 255, 100)
        self.bar_bg_color = (50, 50, 50)
        self.shield_color = (100, 200, 255)

        # HUD elements positioning
        self.shield_bar_rect = pygame.Rect(20, screen_height - 60, 200, 20)
        self.wave_info_pos = (20, 20)
        self.score_pos = (screen_width - 200, 20)

    def draw(self, screen, player, wave_info, score=0):
        """
        Draw HUD elements.
        Args:
            screen: Surface to draw on
            player: Player object for shield info
            wave_info: Dictionary with wave information
            score: Current player score
        """
        # Draw shield energy bar
        self._draw_shield_bar(screen, player)

        # Draw wave information
        self._draw_wave_info(screen, wave_info)

        # Draw score
        score_text = self.font.render(f"Score: {score}", True, self.text_color)
        screen.blit(score_text, self.score_pos)

        # Draw active bullets count
        bullet_count = len(player.get_bullets())
        bullet_text = self.small_font.render(f"Bullets: {bullet_count}/{player.max_bullets}", True, self.text_color)
        screen.blit(bullet_text, (20, self.screen_height - 100))

    def _draw_shield_bar(self, screen, player):
        """Draw the shield energy bar."""
        # Background
        pygame.draw.rect(screen, self.bar_bg_color, self.shield_bar_rect)

        # Shield energy
        energy_ratio = player.shield_energy / player.max_shield_energy
        energy_width = int(self.shield_bar_rect.width * energy_ratio)
        energy_rect = pygame.Rect(self.shield_bar_rect.x, self.shield_bar_rect.y,
                                 energy_width, self.shield_bar_rect.height)

        # Color based on energy level
        if energy_ratio > 0.6:
            color = self.good_color
        elif energy_ratio > 0.3:
            color = (255, 255, 100)  # Yellow
        else:
            color = self.warning_color

        pygame.draw.rect(screen, color, energy_rect)

        # Border and label
        pygame.draw.rect(screen, self.shield_color, self.shield_bar_rect, 2)
        shield_text = self.small_font.render("Shield Energy", True, self.text_color)
        screen.blit(shield_text, (self.shield_bar_rect.x, self.shield_bar_rect.y - 25))

        # Shield status
        status = "ACTIVE" if player.shield_active else "INACTIVE"
        status_color = self.good_color if player.shield_active else self.warning_color
        status_text = self.small_font.render(f"Shield: {status}", True, status_color)
        screen.blit(status_text, (self.shield_bar_rect.x + 220, self.shield_bar_rect.y - 2))

    def _draw_wave_info(self, screen, wave_info):
        """Draw wave progression information."""
        if wave_info['in_break']:
            # Wave break countdown
            time_left = int(wave_info['break_time_remaining'])
            wave_text = self.font.render(f"Wave {wave_info['wave_number']} Starting in: {time_left}s", True, self.warning_color)
        else:
            # Current wave progress
            progress = f"{wave_info['enemies_spawned']}/{wave_info['enemies_per_wave']}"
            wave_text = self.font.render(f"Wave {wave_info['wave_number']} - Enemies: {progress}", True, self.text_color)

        screen.blit(wave_text, self.wave_info_pos)
