"""
Geometric Space Shooter - Main Entry Point
A modern space shooter with geometric design and particle effects.
"""
from core.game_manager import GameManager


def main():
    """Initialize and run the game."""
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
