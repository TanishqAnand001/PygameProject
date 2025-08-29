# Game Settings Configuration
"""
Central configuration file for all game settings and constants.
"""

# Display Settings
FULLSCREEN = True
VSYNC = True
TARGET_FPS = 60

# Player Settings
PLAYER_ACCELERATION = 1200.0
PLAYER_MAX_SPEED = 450.0
PLAYER_FRICTION = 1800.0
PLAYER_TILT_SPEED = 300.0
PLAYER_MAX_TILT = 25.0

# Particle System Settings
MAX_PARTICLES = 1000  # Increased for better effects
THRUSTER_PARTICLE_SPAWN_RATE = 0.02
EXPLOSION_PARTICLE_COUNT = 15

# Background Settings
STAR_COUNT = 400  # More stars for richer background
STAR_SPEED_MULTIPLIER = 1.0

# Enemy Settings
ENEMY_SPAWN_RATE = 2.0
ENEMY_SPEED_BASE = 200.0

# New Power-Up System
POWERUP_SPAWN_CHANCE = 0.3  # 30% chance per enemy kill
POWERUP_LIFETIME = 8.0  # Seconds before disappearing
POWERUP_TYPES = ["rapid_fire", "shield_boost", "damage_boost", "speed_boost", "triple_shot"]

# New Weapon System
WEAPON_RAPID_FIRE_DURATION = 5.0
WEAPON_TRIPLE_SHOT_DURATION = 8.0
WEAPON_DAMAGE_BOOST_DURATION = 10.0
WEAPON_SPEED_BOOST_DURATION = 6.0

# New Wave System
WAVE_ENEMY_MULTIPLIER = 1.3  # Enemies increase by 30% each wave
WAVE_BREAK_DURATION = 3.0
WAVE_BOSS_FREQUENCY = 5  # Boss every 5 waves

# Screen Shake System
SCREEN_SHAKE_INTENSITY = 8
SCREEN_SHAKE_DURATION = 0.3

# Sound Settings (for future audio implementation)
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.6

# UI Settings
PAUSE_BLINK_INTERVAL = 0.5
FPS_UPDATE_INTERVAL = 0.5
NOTIFICATION_DURATION = 2.0
COMBO_DISPLAY_DURATION = 1.5

# New Scoring System
SCORE_MULTIPLIER_MAX = 10.0
COMBO_DECAY_TIME = 2.0
COMBO_BONUS_MULTIPLIER = 0.1

# Controls
QUIT_KEY = "escape"
PAUSE_KEY = "p"
CONTROLS_KEY = "c"
DEBUG_KEY = "f1"
POWERUP_KEY = "q"  # Special ability activation

# Colors (RGB tuples)
BACKGROUND_COLOR = (0, 0, 50)
PLAYER_COLOR_OUTER = (100, 150, 255)
PLAYER_COLOR_MIDDLE = (150, 200, 255)
PLAYER_COLOR_INNER = (200, 220, 255)
THRUSTER_COLOR_HOT = (255, 100, 0)
THRUSTER_COLOR_WARM = (255, 150, 50)
BULLET_COLOR = (255, 255, 100)
ENEMY_COLOR = (255, 50, 50)

# New Power-Up Colors
POWERUP_RAPID_FIRE_COLOR = (255, 0, 255)  # Magenta
POWERUP_SHIELD_COLOR = (0, 255, 255)      # Cyan
POWERUP_DAMAGE_COLOR = (255, 165, 0)      # Orange
POWERUP_SPEED_COLOR = (0, 255, 0)         # Green
POWERUP_TRIPLE_COLOR = (255, 255, 0)      # Yellow

# UI Enhancement Colors
UI_ACCENT_COLOR = (100, 200, 255)
UI_WARNING_COLOR = (255, 100, 100)
UI_SUCCESS_COLOR = (100, 255, 100)
UI_BACKGROUND_ALPHA = 120
COMBO_TEXT_COLOR = (255, 255, 100)
