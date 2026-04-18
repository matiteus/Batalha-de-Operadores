"""
Main entry point for the Math Logic Game.
"""

import pygame
import os
from screen import Screen
from game_manager import GameManager, GameState
from card import CardState
from config_loader import ConfigLoader
from asset_manager import AssetManager


def main():
    """Main game loop."""
    # Initialize configuration loader
    config_loader = ConfigLoader(config_dir=os.path.join(os.path.dirname(__file__), "config"))
    
    # Load configuration
    if not config_loader.load_all():
        print("Warning: Could not load configuration files. Using defaults.")
    
    # Validate configuration
    errors = config_loader.validate_config()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    
    # Initialize screen with config
    screen = Screen(config_loader)
    
    # Initialize game manager with config
    game_manager = GameManager(config_loader)
    
    # Main game loop
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    handle_click(game_manager, mouse_pos)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game_manager.state == GameState.MENU:
                        game_manager.start_game()
                    elif game_manager.state == GameState.LEVEL_COMPLETE:
                        game_manager.next_level()
                    elif game_manager.state == GameState.GAME_OVER:
                        game_manager.reset_game()
                    elif game_manager.state == GameState.VICTORY:
                        game_manager.reset_game()
        
        # Update game state
        delta_time = screen.tick()
        game_manager.update_timer(delta_time)
        game_manager.update_feedback(delta_time)
        
        # Update card hover state
        if game_manager.current_card and game_manager.state == GameState.PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            game_manager.current_card.update(mouse_pos)
        
        # Draw everything
        screen.clear()
        draw_game(screen, game_manager, config_loader)
        screen.update()
    
    pygame.quit()


def handle_click(game_manager: GameManager, mouse_pos: tuple) -> None:
    """Handle mouse click events."""
    state = game_manager.state
    
    if state == GameState.MENU:
        game_manager.start_game()
        
    elif state == GameState.PLAYING:
        if game_manager.current_card:
            answer = game_manager.current_card.check_click(mouse_pos)
            if answer:
                game_manager.handle_answer(answer)
                
    elif state == GameState.LEVEL_COMPLETE:
        game_manager.next_level()
        
    elif state == GameState.GAME_OVER:
        game_manager.reset_game()
        
    elif state == GameState.VICTORY:
        game_manager.reset_game()


def draw_game(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the current game state."""
    state = game_manager.state
    
    if state == GameState.MENU:
        draw_menu(screen, config_loader)
        
    elif state == GameState.PLAYING:
        draw_playing(screen, game_manager, config_loader)
        
    elif state == GameState.ANSWER_FEEDBACK:
        draw_answer_feedback(screen, game_manager, config_loader)
        
    elif state == GameState.LEVEL_COMPLETE:
        draw_level_complete(screen, game_manager, config_loader)
        
    elif state == GameState.GAME_OVER:
        draw_game_over(screen, game_manager, config_loader)
        
    elif state == GameState.VICTORY:
        draw_victory(screen, game_manager, config_loader)


def draw_menu(screen: Screen, config_loader: ConfigLoader) -> None:
    """Draw the main menu."""
    center = screen.get_center()
    
    # Get colors from config
    title_color = config_loader.get_color("victory") if config_loader else (100, 200, 255)
    text_color = config_loader.get_color("text_secondary") if config_loader else (200, 200, 200)
    accent_color = config_loader.get_color("level_complete") if config_loader else (150, 255, 150)
    
    # Get font sizes from config
    title_size = config_loader.get_font_size("title_size") if config_loader else 64
    text_size = config_loader.get_font_size("text_size") if config_loader else 32
    small_size = config_loader.get_font_size("small_text_size") if config_loader else 24
    
    # Title
    screen.draw_text(
        "Math Logic Game",
        (center[0], center[1] - 100),
        font_size=title_size,
        color=title_color,
        center=True
    )
    
    # Instructions
    screen.draw_text(
        "Solve math expressions by choosing the correct operator or answer",
        (center[0], center[1]),
        font_size=small_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        "Press SPACE or Click to Start",
        (center[0], center[1] + 80),
        font_size=text_size,
        color=accent_color,
        center=True
    )


def draw_playing(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the playing state."""
    # Draw HUD
    draw_hud(screen, game_manager, config_loader)
    
    # Draw current card
    if game_manager.current_card:
        game_manager.current_card.draw(screen.get_surface())


def draw_answer_feedback(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the answer feedback screen."""
    center = screen.get_center()
    
    # Get colors from config
    if game_manager.last_answer_correct:
        feedback_color = config_loader.get_color("level_complete") if config_loader else (100, 255, 100)
        text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
        feedback_text = "CORRECT!"
        emoji = "✓"
    else:
        feedback_color = config_loader.get_color("card_wrong") if config_loader else (255, 100, 100)
        text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
        feedback_text = "WRONG!"
        emoji = "✗"
    
    # Get font sizes from config
    title_size = config_loader.get_font_size("title_size") if config_loader else 64
    text_size = config_loader.get_font_size("text_size") if config_loader else 36
    
    # Draw feedback background
    screen.draw_rect(
        (center[0], center[1]),
        (400, 200),
        feedback_color,
        border_radius=20,
        center=True
    )
    
    # Draw result text
    screen.draw_text(
        emoji,
        (center[0], center[1] - 40),
        font_size=title_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        feedback_text,
        (center[0], center[1] + 20),
        font_size=text_size,
        color=text_color,
        center=True
    )
    
    # Show correct answer if wrong
    if not game_manager.last_answer_correct and game_manager.current_card:
        screen.draw_text(
            f"Correct answer: {game_manager.current_card.correct_answer}",
            (center[0], center[1] + 60),
            font_size=24,
            color=text_color,
            center=True
        )


def draw_hud(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the heads-up display."""
    # Get colors from config
    text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
    timer_warning_color = config_loader.get_color("timer_warning") if config_loader else (255, 100, 100)
    lives_color = config_loader.get_color("lives") if config_loader else (255, 100, 100)
    
    # Get font sizes from config
    text_size = config_loader.get_font_size("text_size") if config_loader else 28
    small_size = config_loader.get_font_size("small_text_size") if config_loader else 24
    
    # Level
    screen.draw_text(
        f"Level: {game_manager.current_level_num}",
        (70, 30),
        font_size=text_size,
        color=text_color
    )
    
    # Level name (if available)
    level_name = game_manager.get_level_name()
    if level_name:
        screen.draw_text(
            level_name,
            (70, 55),
            font_size=small_size,
            color=config_loader.get_color("text_secondary") if config_loader else (200, 200, 200)
        )
    
    # Score
    screen.draw_text(
        f"Score: {game_manager.score}",
        (screen.width - 100, 30),
        font_size=text_size,
        color=text_color
    )
    
    # Lives
    lives_text = "❤ " * game_manager.lives
    screen.draw_text(
        lives_text,
        (screen.width // 2, 30),
        font_size=text_size,
        color=lives_color
    )
    
    # Timer
    time_color = text_color if game_manager.time_remaining > 10 else timer_warning_color
    screen.draw_text(
        f"Time: {int(game_manager.time_remaining)}s",
        (70, 85),
        font_size=small_size,
        color=time_color
    )
    
    # Progress
    current, total = game_manager.get_level_progress()
    screen.draw_text(
        f"Question: {current}/{total}",
        (screen.width - 100, 60),
        font_size=small_size,
        color=config_loader.get_color("text_secondary") if config_loader else (200, 200, 200)
    )


def draw_answer_feedback(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the answer feedback screen."""
    center = screen.get_center()
    
    # Get colors from config
    if game_manager.last_answer_correct:
        feedback_color = config_loader.get_color("level_complete") if config_loader else (100, 255, 100)
        text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
        feedback_text = "CORRECT!"
        emoji = "✓"
    else:
        feedback_color = config_loader.get_color("card_wrong") if config_loader else (255, 100, 100)
        text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
        feedback_text = "WRONG!"
        emoji = "✗"
    
    # Get font sizes from config
    title_size = config_loader.get_font_size("title_size") if config_loader else 64
    text_size = config_loader.get_font_size("text_size") if config_loader else 36
    
    # Draw feedback background
    screen.draw_rect(
        (center[0], center[1]),
        (400, 200),
        feedback_color,
        border_radius=20,
        center=True
    )
    
    # Draw result text
    screen.draw_text(
        emoji,
        (center[0], center[1] - 40),
        font_size=title_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        feedback_text,
        (center[0], center[1] + 20),
        font_size=text_size,
        color=text_color,
        center=True
    )
    
    # Show correct answer if wrong
    if not game_manager.last_answer_correct and game_manager.current_card:
        screen.draw_text(
            f"Correct answer: {game_manager.current_card.correct_answer}",
            (center[0], center[1] + 60),
            font_size=24,
            color=text_color,
            center=True
        )


def draw_level_complete(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the level complete screen."""
    center = screen.get_center()
    
    # Get colors from config
    complete_color = config_loader.get_color("level_complete") if config_loader else (100, 255, 100)
    text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
    accent_color = config_loader.get_color("level_complete") if config_loader else (150, 255, 150)
    
    # Get font sizes from config
    heading_size = config_loader.get_font_size("heading_size") if config_loader else 48
    text_size = config_loader.get_font_size("text_size") if config_loader else 32
    small_size = config_loader.get_font_size("small_text_size") if config_loader else 28
    
    screen.draw_text(
        f"Level {game_manager.current_level_num} Complete!",
        (center[0], center[1] - 50),
        font_size=heading_size,
        color=complete_color,
        center=True
    )
    
    screen.draw_text(
        f"Score: {game_manager.score}",
        (center[0], center[1] + 20),
        font_size=text_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        "Press SPACE or Click to continue",
        (center[0], center[1] + 80),
        font_size=small_size,
        color=accent_color,
        center=True
    )


def draw_game_over(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the game over screen."""
    center = screen.get_center()
    
    # Get colors from config
    wrong_color = config_loader.get_color("card_wrong") if config_loader else (255, 100, 100)
    text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
    secondary_color = config_loader.get_color("text_secondary") if config_loader else (200, 200, 200)
    accent_color = config_loader.get_color("level_complete") if config_loader else (150, 255, 150)
    
    # Get font sizes from config
    title_size = config_loader.get_font_size("title_size") if config_loader else 64
    text_size = config_loader.get_font_size("text_size") if config_loader else 36
    small_size = config_loader.get_font_size("small_text_size") if config_loader else 28
    
    screen.draw_text(
        "Game Over",
        (center[0], center[1] - 80),
        font_size=title_size,
        color=wrong_color,
        center=True
    )
    
    screen.draw_text(
        f"Final Score: {game_manager.score}",
        (center[0], center[1]),
        font_size=text_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        f"Level Reached: {game_manager.current_level_num}",
        (center[0], center[1] + 50),
        font_size=small_size,
        color=secondary_color,
        center=True
    )
    
    screen.draw_text(
        "Press SPACE or Click to restart",
        (center[0], center[1] + 120),
        font_size=small_size,
        color=accent_color,
        center=True
    )


def draw_victory(screen: Screen, game_manager: GameManager, config_loader: ConfigLoader) -> None:
    """Draw the victory screen."""
    center = screen.get_center()
    
    # Get colors from config
    victory_color = config_loader.get_color("victory") if config_loader else (255, 215, 0)
    complete_color = config_loader.get_color("level_complete") if config_loader else (100, 255, 100)
    text_color = config_loader.get_color("text_primary") if config_loader else (255, 255, 255)
    accent_color = config_loader.get_color("level_complete") if config_loader else (150, 255, 150)
    
    # Get font sizes from config
    title_size = config_loader.get_font_size("title_size") if config_loader else 64
    text_size = config_loader.get_font_size("text_size") if config_loader else 36
    small_size = config_loader.get_font_size("small_text_size") if config_loader else 28
    
    screen.draw_text(
        "Congratulations!",
        (center[0], center[1] - 80),
        font_size=title_size,
        color=victory_color,
        center=True
    )
    
    screen.draw_text(
        f"You completed all {game_manager.total_levels} levels!",
        (center[0], center[1] - 20),
        font_size=text_size,
        color=complete_color,
        center=True
    )
    
    screen.draw_text(
        f"Final Score: {game_manager.score}",
        (center[0], center[1] + 40),
        font_size=text_size,
        color=text_color,
        center=True
    )
    
    screen.draw_text(
        "Press SPACE or Click to play again",
        (center[0], center[1] + 100),
        font_size=small_size,
        color=accent_color,
        center=True
    )


if __name__ == "__main__":
    main()