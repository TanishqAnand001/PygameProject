"""
Core game manager that handles the main game loop and state management.
"""
import pygame
import sys
import math
from config.settings import *
from entities.player import Player
from background import Background
from systems.enemy_spawner import EnemySpawner
from systems.powerup_system import PowerUpManager
from systems.scoring_system import ScoreManager
from systems.wave_system import WaveManager
from effects.screen_shake import ScreenShake
from ui.controls_menu import ControlsMenu, HUD
from ui.game_over_screen import GameOverScreen
from ui.enhanced_ui import NotificationManager, EnhancedHUD
from ui.start_screen import StartScreen


class GameManager:
    """
    Enhanced game manager with improved UI and start screen.
    """

    def __init__(self):
        """Initialize the enhanced game manager."""
        pygame.init()

        # Display setup
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1200, 800))

        self.screen_width, self.screen_height = self.screen.get_size()
        pygame.display.set_caption("NEXUS ASSAULT - Enhanced Edition")
        pygame.mouse.set_visible(False)

        # Core systems
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Game states
        self.game_state = "start_screen"  # start_screen, playing, game_over, controls
        self.running = True
        self.game_over = False
        self.paused = False
        self.dt = 0

        # Initialize UI systems first
        self.start_screen = StartScreen(self.screen_width, self.screen_height)
        self.notification_manager = NotificationManager(self.screen_width, self.screen_height)
        self.enhanced_hud = EnhancedHUD(self.screen_width, self.screen_height)

        # Game objects (initialized when game starts)
        self.background = None
        self.player = None
        self.enemy_spawner = None
        self.powerup_manager = None
        self.score_manager = None
        self.wave_manager = None
        self.screen_shake = None
        self.controls_menu = None
        self.hud = None
        self.game_over_screen = None

        # Initialize other systems
        self.pause_symbol = self._create_pause_symbol()
        self.pause_symbol_visible = True
        self.pause_timer = 0

        # Performance monitoring
        self.performance_update_timer = 0.0
        self.cached_fps_text = None
        self.show_debug_info = False

    def _initialize_game_objects(self):
        """Initialize or reset all game objects and systems."""
        # Game objects
        self.background = Background(self.screen_width, self.screen_height, star_count=STAR_COUNT)
        self.player = Player(self.screen_width, self.screen_height)
        self.enemy_spawner = EnemySpawner(self.screen_width, self.screen_height)

        # Enhanced systems
        self.powerup_manager = PowerUpManager()
        self.score_manager = ScoreManager()
        self.wave_manager = WaveManager(self.screen_width, self.screen_height)
        self.screen_shake = ScreenShake()

        # UI systems
        self.controls_menu = ControlsMenu(self.screen_width, self.screen_height)
        self.hud = HUD(self.screen_width, self.screen_height)
        self.game_over_screen = GameOverScreen(self.screen_width, self.screen_height)

        # Depth perception overlay
        self.depth_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA).convert_alpha()
        self.depth_overlay.fill((0, 0, 20, 100))

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.enemies = []

        # Start first wave
        self.wave_manager.start_new_wave()

    def _reset_game(self):
        """Reset the game to initial state."""
        self.game_over = False
        self.paused = False
        self.game_state = "playing"
        pygame.mouse.set_visible(False)
        self._initialize_game_objects()
        self.notification_manager.add_notification("🚀 Game Started!", "success")

    def _create_pause_symbol(self):
        """Create the pause symbol surface."""
        pause_surface = pygame.Surface((64, 64), pygame.SRCALPHA).convert_alpha()
        pause_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(pause_surface, (255, 255, 255), (10, 10, 15, 44))
        pygame.draw.rect(pause_surface, (255, 255, 255), (39, 10, 15, 44))
        return pause_surface

    def handle_events(self):
        """Process all game events with enhanced input handling."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "start_screen":
                    # Handle start screen input
                    action = self.start_screen.handle_input(event)
                    if action == "start_game":
                        self._initialize_game_objects()
                        self.game_state = "playing"
                        self.notification_manager.add_notification("🚀 NEXUS ASSAULT Initiated!", "success")
                    elif action == "show_controls":
                        self.game_state = "controls"
                        if not self.controls_menu:
                            self.controls_menu = ControlsMenu(self.screen_width, self.screen_height)
                        self.controls_menu.visible = True
                    elif action == "quit_game":
                        self.running = False
                elif self.game_state == "controls":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_c:
                        self.game_state = "start_screen"
                        if self.controls_menu:
                            self.controls_menu.visible = False
                elif self.game_state == "playing":
                    if self.game_over:
                        # Handle game over screen input
                        keys = pygame.key.get_pressed()
                        action = self.game_over_screen.handle_keys(keys)
                        if action == 'play_again':
                            self._reset_game()
                        elif action == 'quit':
                            self.game_state = "start_screen"
                            self.game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "start_screen"
                    elif event.key == pygame.K_p:
                        if not (self.controls_menu and self.controls_menu.visible) and not self.game_over:
                            self.paused = not self.paused
                            status = "Paused" if self.paused else "Resumed"
                            self.notification_manager.add_notification(f"⏸️ Game {status}", "info")
                    elif event.key == pygame.K_F1:
                        self.show_debug_info = not self.show_debug_info
                    elif event.key == pygame.K_c:
                        if not self.game_over:
                            if self.controls_menu:
                                self.controls_menu.toggle_visibility()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "playing" and self.game_over:
                    action = self.game_over_screen.handle_click(event.pos)
                    if action == 'play_again':
                        self._reset_game()
                    elif action == 'quit':
                        self.game_state = "start_screen"
                        self.game_over = False

    def update(self):
        """Update all enhanced game systems."""
        self.dt = self.clock.tick(TARGET_FPS) / 1000

        if self.game_state == "start_screen":
            self.start_screen.update(self.dt)
            return
        elif self.game_state == "controls":
            return

        if not hasattr(self, 'player') or self.player is None:
            return

        if self.game_over:
            self.game_over_screen.update(self.dt)
            return

        # Update notification system
        self.notification_manager.update(self.dt)

        # Update screen shake
        if self.screen_shake:
            self.screen_shake.update(self.dt)

        # Update enhanced HUD
        self.enhanced_hud.update(self.dt)

        if not self.paused and not (self.controls_menu and self.controls_menu.visible):
            # Update core game systems
            if self.background:
                self.background.update(self.dt)

            # Update power-up system
            if self.powerup_manager:
                self.powerup_manager.update(self.dt)

            # Apply power-up effects to player
            if self.player and self.powerup_manager:
                self.player.apply_powerup_effects(self.powerup_manager)

            # Update player with enhanced systems
            if self.player:
                self.player.update(self.dt)

                # Update invulnerability timer
                if self.player.invulnerability_timer > 0:
                    self.player.invulnerability_timer -= self.dt

            # Enhanced weapon system
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.player:
                if self.player.weapon_system.try_shoot(self.dt):
                    # Add slight screen shake for shooting feedback
                    if self.screen_shake:
                        self.screen_shake.add_shake(2, 0.1)

            # Update wave system
            if self.wave_manager and self.enemy_spawner and self.notification_manager:
                self.wave_manager.update(self.dt, self.enemy_spawner, self.notification_manager)

                # Get new enemies from wave system
                self.enemies = self.wave_manager.enemies_alive

                # Update enemies
                for enemy in self.enemies:
                    enemy.update(self.dt, self.screen_width, self.screen_height)

                # Remove inactive enemies
                for enemy in self.enemies[:]:
                    if not enemy.active:
                        self.enemies.remove(enemy)
                        self.wave_manager.remove_enemy(enemy)

                # Handle collisions with enhanced effects
                self._handle_enhanced_collisions()

            # Update scoring system
            if self.score_manager:
                self.score_manager.update(self.dt)

        elif self.paused:
            # Handle pause symbol blinking
            self.pause_timer += self.dt
            if self.pause_timer >= PAUSE_BLINK_INTERVAL:
                self.pause_symbol_visible = not self.pause_symbol_visible
                self.pause_timer = 0

        # Update performance monitoring
        self.performance_update_timer += self.dt

    def _handle_enhanced_collisions(self):
        """Enhanced collision detection with all new enemy abilities."""
        player_bullets = self.player.weapon_system.get_bullets()

        # Update player position for enemy AI
        if self.wave_manager and self.player:
            self.wave_manager.set_player_position(self.player.rect.centerx, self.player.rect.centery)

        # Bullet vs Enemy collisions
        for bullet in player_bullets[:]:
            bullet_rect = bullet.get_rect()

            for enemy in self.enemies[:]:
                enemy_rect = enemy.get_rect()

                if bullet_rect.colliderect(enemy_rect):
                    bullet.active = False

                    # Apply bullet damage
                    damage_dealt = getattr(bullet, 'damage', 1)
                    enemy_destroyed = enemy.take_damage(damage_dealt)

                    if enemy_destroyed:
                        # Handle special death effects
                        self._handle_enemy_death_effects(enemy)

                        # Score and rewards
                        base_score = getattr(enemy, 'score_value', 100)
                        final_score = self.score_manager.add_kill_score(base_score)

                        # Try to spawn power-up
                        if self.powerup_manager.try_spawn_powerup(enemy.int_x, enemy.int_y):
                            self.notification_manager.add_notification("Power-up spawned!", "powerup", 1.5)

                        # Enhanced explosion effect based on enemy type
                        explosion_size = EXPLOSION_PARTICLE_COUNT + enemy.size // 3
                        self.player.particle_engine.create_explosion(
                            enemy.int_x, enemy.int_y, explosion_size
                        )

                        # Screen shake based on enemy size and type
                        distance = math.sqrt((enemy.int_x - self.screen_width//2)**2 +
                                           (enemy.int_y - self.screen_height//2)**2)
                        shake_intensity = 10 + enemy.size // 2
                        if hasattr(enemy, 'is_boss') and enemy.is_boss:
                            shake_intensity *= 2
                        self.screen_shake.add_explosion_shake(distance, shake_intensity)
                    else:
                        # Enemy damaged but not destroyed - smaller effect
                        self.player.particle_engine.create_explosion(
                            enemy.int_x, enemy.int_y, 3
                        )
                        self.screen_shake.add_shake(3, 0.1)
                    break

        # Enemy Bullet vs Player collisions
        for enemy in self.enemies:
            if hasattr(enemy, 'bullets'):
                for bullet in enemy.bullets[:]:
                    if bullet.active and bullet.get_rect().colliderect(self.player.rect):
                        bullet.active = False

                        # Handle player being hit by enemy bullet
                        if self.player.shield_active and self.player.shield_energy > 0:
                            # Shield absorbs damage
                            self.player.shield_energy -= bullet.damage * 10
                            self.player.simulate_shield_hit()
                            self.screen_shake.add_shake(8, 0.2)
                            self.notification_manager.add_notification("Shield hit!", "warning")
                        else:
                            # Player takes damage
                            if self.player.take_damage(bullet.damage * 15):  # Enemy bullets hurt more
                                self._trigger_game_over()
                            else:
                                self.notification_manager.add_notification("Hull breach!", "warning")
                                self.screen_shake.add_shake(15, 0.4)

        # Power-up collection
        collected_powerups = self.powerup_manager.check_collection(self.player.rect)
        for powerup_type in collected_powerups:
            self.notification_manager.add_powerup_notification(powerup_type)
            # Add score bonus for collecting power-ups
            self.score_manager.add_kill_score(50, "powerup")

        # Enhanced Enemy vs Player collisions
        player_rect = self.player.rect
        for enemy in self.enemies[:]:
            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                # Handle special enemy effects on collision
                self._handle_enemy_collision_effects(enemy)

                if self.player.shield_active and self.player.shield_energy > 0:
                    # Shield absorbs damage
                    damage = 25 + enemy.size
                    self.player.shield_energy -= damage
                    enemy.active = False

                    self.player.simulate_shield_hit()
                    self.screen_shake.add_shake(15, 0.4)

                    self.player.particle_engine.create_explosion(
                        enemy.int_x, enemy.int_y, 12
                    )
                    self.notification_manager.add_notification("Shield absorbed collision!", "info")
                else:
                    # Player takes damage based on enemy type
                    base_damage = 34
                    if hasattr(enemy, 'is_boss') and enemy.is_boss:
                        base_damage *= 2
                    elif enemy.size > 20:  # Large enemies
                        base_damage = int(base_damage * 1.5)

                    if self.player.take_damage(base_damage):  # Player died
                        self._trigger_game_over()
                    else:
                        self.notification_manager.add_notification("Critical hull damage!", "warning")

                    enemy.active = False
                    self.screen_shake.add_shake(25, 0.6)

        # Handle special enemy abilities affecting the player
        self._handle_special_enemy_abilities()

    def _handle_enemy_death_effects(self, enemy):
        """Handle special effects when enemies are destroyed."""
        # Handle splitter enemies
        if hasattr(enemy, 'split_on_death') and enemy.split_on_death:
            split_enemies = enemy.get_split_enemies()
            if split_enemies:
                self.enemies.extend(split_enemies)
                self.wave_manager.enemies_alive.extend(split_enemies)
                self.notification_manager.add_notification("Enemy split!", "warning", 2.0)

        # Handle energy vampire death - restore some player energy
        if hasattr(enemy, 'energy_drain') and enemy.energy_drain:
            if self.player.shield_energy < self.player.max_shield_energy:
                self.player.shield_energy = min(
                    self.player.max_shield_energy,
                    self.player.shield_energy + 20
                )
                self.notification_manager.add_notification("Energy restored!", "success", 1.5)

    def _handle_enemy_collision_effects(self, enemy):
        """Handle special effects when enemies collide with player."""
        # Energy vampire drains player energy on contact
        if hasattr(enemy, 'energy_drain') and enemy.energy_drain:
            if self.player.shield_energy > 0:
                drain_amount = min(30, self.player.shield_energy)
                self.player.shield_energy -= drain_amount
                self.notification_manager.add_notification("Energy drained!", "warning", 1.5)

    def _handle_special_enemy_abilities(self):
        """Handle ongoing special enemy abilities that affect the player."""
        # Energy vampires drain energy over time when close
        for enemy in self.enemies:
            if (hasattr(enemy, 'energy_drain') and enemy.energy_drain and
                enemy.enemy_type == "energy_vampire"):

                # Calculate distance to player
                distance = math.sqrt(
                    (enemy.x - self.player.rect.centerx)**2 +
                    (enemy.y - self.player.rect.centery)**2
                )

                # Drain energy if close enough
                if distance < 150 and self.player.shield_energy > 0:
                    drain_rate = 5 * self.dt  # 5 energy per second
                    self.player.shield_energy = max(0, self.player.shield_energy - drain_rate)

                    # Visual feedback
                    if random.random() < 0.1:  # 10% chance per frame
                        self.notification_manager.add_notification("Energy being drained!", "warning", 0.5)

    def _trigger_game_over(self):
        """Enhanced game over with final statistics."""
        self.game_over = True
        pygame.mouse.set_visible(True)

        # Add final score to game over screen
        stats = self.score_manager.get_stats()
        final_wave = self.wave_manager.current_wave_number - 1

        self.notification_manager.add_notification("Game Over!", "warning", 5.0)
        self.notification_manager.add_notification(f"Final Score: {stats['score']}", "info", 5.0)
        self.notification_manager.add_notification(f"Waves Survived: {final_wave}", "info", 5.0)
        self.notification_manager.add_notification(f"Enemies Defeated: {stats['enemies_defeated']}", "info", 5.0)
        self.notification_manager.add_notification(f"Power-ups Collected: {stats['powerups_collected']}", "info", 5.0)
        self.notification_manager.add_notification(f"Accuracy: {stats['accuracy']:.1f}%", "info", 5.0)

    def draw(self):
        """Enhanced rendering with all new visual effects."""
        # Clear screen with background color
        self.screen.fill(BACKGROUND_COLOR)

        if self.game_state == "start_screen":
            # Draw start screen
            self.start_screen.draw(self.screen)
        elif self.game_state == "controls":
            # Draw controls screen
            if self.controls_menu:
                self.controls_menu.draw(self.screen)
        elif self.game_state == "playing":
            # Draw background stars
            if self.background:
                self.background.draw(self.screen)

            # Apply depth perception overlay
            if hasattr(self, 'depth_overlay'):
                self.screen.blit(self.depth_overlay, (0, 0))

            if self.game_over:
                # Draw game over screen with enhanced stats
                if self.score_manager and self.wave_manager:
                    stats = self.score_manager.get_stats()
                    final_wave = self.wave_manager.current_wave_number - 1
                    self.game_over_screen.draw(self.screen, stats['score'], final_wave)
            else:
                # Create main game surface for screen shake
                if self.screen_shake and self.screen_shake.is_shaking():
                    # Render to temporary surface for shake effect
                    game_surface = pygame.Surface((self.screen_width, self.screen_height))
                    game_surface.fill(BACKGROUND_COLOR)
                    if self.background:
                        self.background.draw(game_surface)
                    if hasattr(self, 'depth_overlay'):
                        game_surface.blit(self.depth_overlay, (0, 0))

                    # Draw game objects on shake surface
                    self._draw_game_objects(game_surface)

                    # Apply screen shake
                    self.screen_shake.apply_to_surface(game_surface, self.screen)
                else:
                    # Normal rendering
                    self._draw_game_objects(self.screen)

                # Draw wave transition effects (not affected by screen shake)
                if self.wave_manager:
                    self.wave_manager.draw_wave_transition(self.screen, self.screen_width, self.screen_height)

                # Draw UI elements (not affected by screen shake)
                self._draw_enhanced_ui()

        pygame.display.flip()

    def _draw_game_objects(self, surface):
        """Draw all game objects on the specified surface."""
        if not (self.controls_menu and self.controls_menu.visible):
            # Draw player with invulnerability flashing
            if (self.player and hasattr(self, 'all_sprites') and
                (self.player.invulnerability_timer <= 0 or int(self.player.invulnerability_timer * 10) % 2)):
                self.all_sprites.draw(surface)

            # Draw enhanced particle effects
            if self.player:
                self.player.draw_particles(surface)
                self.player.draw_shockwaves(surface)
                self.player.draw_shield(surface)

            # Draw enemies
            if hasattr(self, 'enemies'):
                for enemy in self.enemies:
                    enemy.draw(surface)

            # Draw enhanced weapon bullets
            if self.player:
                self.player.weapon_system.draw_bullets(surface)

            # Draw power-ups with effects
            if self.powerup_manager:
                self.powerup_manager.draw(surface)

            # Draw pause symbol if paused
            if self.paused and self.pause_symbol_visible:
                surface.blit(self.pause_symbol, (20, 20))

    def _draw_enhanced_ui(self):
        """Draw all enhanced UI elements with improved positioning."""
        if not self.player or not self.score_manager or not self.wave_manager:
            return

        # Enhanced HUD with animations
        self.enhanced_hud.draw_enhanced_bars(
            self.screen, self.player,
            self.score_manager.score, self.wave_manager.current_wave_number
        )

        # Weapon status indicators - positioned below health/shield bars
        self.enhanced_hud.draw_weapon_status(self.screen, self.player.weapon_system)

        # Mini-map radar - positioned to avoid overlap
        if hasattr(self, 'enemies'):
            self.enhanced_hud.draw_minimap(self.screen, self.player, self.enemies)

        # Combo and score effects - positioned in center
        self.score_manager.draw_score_effects(self.screen, self.screen_width, self.screen_height)

        # Power-up effect timers - repositioned to avoid overlap
        self._draw_powerup_timers_improved()

        # Notifications - positioned on right side
        self.notification_manager.draw(self.screen)

        # Original controls menu
        if self.controls_menu and self.controls_menu.visible:
            self.controls_menu.draw(self.screen)

        # Debug info - positioned on right side
        if self.show_debug_info:
            self._draw_enhanced_debug_info()

    def _draw_powerup_timers_improved(self):
        """Draw active power-up effect timers with improved positioning."""
        if not self.powerup_manager or not self.powerup_manager.active_effects:
            return

        # Position above the health/shield bars (left side)
        start_x = 25  # Same margin as health/shield bars
        start_y = self.screen_height - 200  # Above health bars with some spacing

        for i, (effect_type, remaining_time) in enumerate(self.powerup_manager.active_effects.items()):
            color = {
                "rapid_fire": POWERUP_RAPID_FIRE_COLOR,
                "triple_shot": POWERUP_TRIPLE_COLOR,
                "damage_boost": POWERUP_DAMAGE_COLOR,
                "speed_boost": POWERUP_SPEED_COLOR
            }.get(effect_type, UI_ACCENT_COLOR)

            # Effect name and timer
            effect_name = effect_type.replace('_', ' ').title()
            timer_text = f"{effect_name}: {remaining_time:.1f}s"

            # Position for this timer - stack upward from start position
            x_pos = start_x
            y_pos = start_y - i * 40  # Stack upward instead of downward

            # Background with modern styling
            bar_width = 180
            bar_height = 12
            bg_rect = pygame.Rect(x_pos, y_pos + 20, bar_width, bar_height)

            # Background
            pygame.draw.rect(self.screen, (20, 20, 40), bg_rect, border_radius=6)
            pygame.draw.rect(self.screen, color, bg_rect, width=2, border_radius=6)

            # Timer bar fill
            time_ratio = remaining_time / {
                "rapid_fire": WEAPON_RAPID_FIRE_DURATION,
                "triple_shot": WEAPON_TRIPLE_SHOT_DURATION,
                "damage_boost": WEAPON_DAMAGE_BOOST_DURATION,
                "speed_boost": WEAPON_SPEED_BOOST_DURATION
            }.get(effect_type, 5.0)

            fill_width = int(bar_width * time_ratio)
            if fill_width > 0:
                fill_rect = pygame.Rect(x_pos, y_pos + 20, fill_width, bar_height)
                pygame.draw.rect(self.screen, color, fill_rect, border_radius=6)

            # Text with better font
            text_surface = pygame.font.Font(None, 24).render(timer_text, True, color)
            self.screen.blit(text_surface, (x_pos, y_pos))

    def _draw_enhanced_debug_info(self):
        """Draw enhanced debug information."""
        if self.performance_update_timer >= FPS_UPDATE_INTERVAL:
            fps = self.clock.get_fps()
            self.cached_fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            self.performance_update_timer = 0

        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Enemies: {len(self.enemies)}",
            f"Particles: {len(self.player.particle_engine.particles)}",
            f"Power-ups: {len(self.powerup_manager.powerups)}",
            f"Active Effects: {len(self.powerup_manager.active_effects)}",
            f"Combo: {self.score_manager.combo_count}x",
            f"Wave: {self.wave_manager.current_wave_number}",
            f"Screen Shake: {self.screen_shake.trauma:.2f}"
        ]

        y_start = 60
        for i, info in enumerate(debug_info):
            text = self.font.render(info, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width - 200, y_start + i * 25))

    def run(self):
        """Enhanced main game loop."""
        # Show startup notification
        self.notification_manager.add_notification("Welcome to Enhanced Space Shooter!", "success", 3.0)
        self.notification_manager.add_notification("Collect power-ups and survive the waves!", "info", 4.0)

        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()
