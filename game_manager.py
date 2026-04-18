"""
GameManager class for managing game state and logic.
Handles levels, scoring, lives, timer, and game flow.
"""

import pygame
from typing import List, Optional, Tuple
from enum import Enum
from card import Card, CardState
from config_loader import ConfigLoader, LevelData, QuestionData
from asset_manager import AssetManager


class GameState(Enum):
    """Possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    ANSWER_FEEDBACK = "answer_feedback"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class Level:
    """Represents a single level in the game."""
    
    def __init__(
        self,
        level_data: LevelData,
    ):
        """
        Initialize a level from configuration data.
        
        Args:
            level_data: LevelData object containing level configuration
            config_loader: Configuration loader instance
        """
        self.level_num = level_data.level_number
        self.level_name = level_data.level_name
        self.description = level_data.description
        self.questions = [(q.expression, q.correct_answer, q.wrong_answers) 
                          for q in level_data.questions]
        self.time_limit = level_data.time_limit
        self.points_per_correct = level_data.points_per_correct
        self.current_question_index = 0
        
    def get_current_question(self) -> Optional[Tuple[str, str, List[str]]]:
        """Get the current question data."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def next_question(self) -> bool:
        """
        Advance to the next question.
        
        Returns:
            True if there are more questions, False if level is complete
        """
        self.current_question_index += 1
        return self.current_question_index < len(self.questions)
    
    def is_complete(self) -> bool:
        """Check if all questions have been answered."""
        return self.current_question_index >= len(self.questions)
    
    def reset(self) -> None:
        """Reset the level to its initial state."""
        self.current_question_index = 0


class GameManager:
    """
    Manages the overall game state, including levels, scoring, lives, and timer.
    """
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """
        Initialize the game manager.
        
        Args:
            config_loader: Configuration loader instance
        """
        self.config_loader = config_loader
        self.asset_manager = AssetManager()
        
        # Load settings from config
        if config_loader:
            self.total_levels = config_loader.get_total_levels()
            self.initial_lives = config_loader.get_initial_lives()
            self.max_lives = config_loader.get_max_lives()
            # Get screen center from config
            window_width, window_height = config_loader.get_window_size()
            self.screen_center = (window_width // 2, window_height // 2)
        else:
            self.total_levels = 10
            self.initial_lives = 3
            self.max_lives = 5
            self.screen_center = (400, 300)
        
        # Game state
        self.state = GameState.MENU
        self.current_level_num = 1
        self.current_level: Optional[Level] = None
        self.current_card: Optional[Card] = None
        
        # Player stats
        self.lives = self.initial_lives
        self.score = 0
        
        # Timer
        self.time_remaining = 0
        self.timer_running = False
        
        # Answer feedback
        self.last_answer_correct = False
        self.feedback_timer = 0
        
        # Levels data (loaded from config)
        self.levels: List[Level] = []
        self._initialize_levels()
            
    def _initialize_levels(self) -> None:
        """Initialize all game levels from configuration."""
        if self.config_loader:
            levels_data = self.config_loader.get_all_levels()
            for level_data in levels_data:
                self.levels.append(Level(level_data))
        else:
            # Fallback to default levels if no config
            self._initialize_default_levels()
            
    def _initialize_default_levels(self) -> None:
        """Initialize default levels without configuration file."""
        # Level 1: Simple addition/subtraction operators
        level1_questions = [
            ("5 ? 3 = 8", "+", ["-", "×", "÷"]),
            ("10 ? 4 = 6", "-", ["+", "×", "÷"]),
            ("7 ? 2 = 9", "+", ["-", "×", "÷"]),
            ("8 ? 3 = 5", "-", ["+", "×", "÷"]),
        ]
        
        # Level 2: Multiplication and division
        level2_questions = [
            ("4 ? 3 = 12", "×", ["+", "-", "÷"]),
            ("15 ? 3 = 5", "÷", ["+", "-", "×"]),
            ("6 ? 7 = 42", "×", ["+", "-", "÷"]),
            ("20 ? 4 = 5", "÷", ["+", "-", "×"]),
        ]
        
        # Create level objects with increasing difficulty
        level_configs = [
            (level1_questions, 60, 100),
            (level2_questions, 55, 120),
        ]
        
        for i, (questions, time_limit, points) in enumerate(level_configs, 1):
            # Create a simple LevelData-like structure
            self.levels.append(self._create_level_from_questions(i, questions, time_limit, points))
            
    def _create_level_from_questions(
        self, 
        level_num: int, 
        questions: List[Tuple[str, str, List[str]]], 
        time_limit: int, 
        points: int
    ) -> Level:
        """Create a Level object from question tuples."""
        class SimpleLevel:
            def __init__(self, num, qs, time, pts):
                self.level_number = num
                self.level_name = f"Level {num}"
                self.description = ""
                self.questions = qs
                self.time_limit = time
                self.points_per_correct = pts
                self.current_question_index = 0
                
            def get_current_question(self):
                if self.current_question_index < len(self.questions):
                    return self.questions[self.current_question_index]
                return None
                
            def next_question(self):
                self.current_question_index += 1
                return self.current_question_index < len(self.questions)
                
            def is_complete(self):
                return self.current_question_index >= len(self.questions)
                
            def reset(self):
                self.current_question_index = 0
                
        return SimpleLevel(level_num, questions, time_limit, points)
            
    def start_game(self) -> None:
        """Start a new game from level 1."""
        self.current_level_num = 1
        self.lives = self.initial_lives
        self.score = 0
        self.state = GameState.PLAYING
        self._load_level(self.current_level_num)
        
    def _load_level(self, level_num: int) -> None:
        """Load a specific level."""
        if 1 <= level_num <= len(self.levels):
            self.current_level = self.levels[level_num - 1]
            self.current_level.reset()
            self.time_remaining = self.current_level.time_limit
            self.timer_running = True
            self._load_current_question()
            
    def _load_current_question(self) -> None:
        """Load the current question as a Card."""
        if self.current_level:
            question_data = self.current_level.get_current_question()
            if question_data:
                expression, correct, wrong = question_data
                self.current_card = Card(
                    expression=expression,
                    correct_answer=correct,
                    wrong_answers=wrong,
                    position=self.screen_center,
                    config_loader=self.config_loader,
                    asset_manager=self.asset_manager
                )
            else:
                self.current_card = None
                
    def update_timer(self, delta_time: float) -> None:
        """
        Update the game timer.
        
        Args:
            delta_time: Time elapsed in milliseconds
        """
        if self.timer_running and self.state == GameState.PLAYING:
            self.time_remaining -= delta_time / 1000.0
            
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self._handle_timeout()
                
    def _handle_timeout(self) -> None:
        """Handle when time runs out."""
        self.lives -= 1
        self.timer_running = False
        
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            # Move to next question or level
            self._advance_game()
            
    def handle_answer(self, answer: str) -> bool:
        """
        Handle a player's answer.
        
        Args:
            answer: The selected answer
            
        Returns:
            True if the answer was correct, False otherwise
        """
        if not self.current_card:
            return False
        
        print(f"[DEBUG] handle_answer called with: '{answer}'")
        print(f"[DEBUG] Current question: {self.current_card.expression}")
        print(f"[DEBUG] Correct answer should be: '{self.current_card.correct_answer}'")
            
        is_correct = self.current_card.is_answer_correct(answer)
        
        if is_correct:
            self.current_card.set_state(CardState.CORRECT)
            self.score += self.current_level.points_per_correct
        else:
            self.current_card.set_state(CardState.WRONG)
            self.lives -= 1
            
        self.timer_running = False
        self.last_answer_correct = is_correct
        self.state = GameState.ANSWER_FEEDBACK
        self.feedback_timer = 1.5  # Show feedback for 1.5 seconds
        
        return is_correct
    
    def update_feedback(self, delta_time: float) -> None:
        """
        Update the answer feedback timer.
        
        Args:
            delta_time: Time elapsed in milliseconds
        """
        if self.state == GameState.ANSWER_FEEDBACK:
            self.feedback_timer -= delta_time / 1000.0
            if self.feedback_timer <= 0:
                # Check for game over
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    # Move to next question/level
                    self._advance_game()
                    if self.state == GameState.ANSWER_FEEDBACK:
                        self.state = GameState.PLAYING
                        
    def _advance_game(self) -> None:
        """Advance to the next question or level."""
        if not self.current_level:
            return
            
        if self.current_level.next_question():
            # More questions in current level
            self._load_current_question()
            self.time_remaining = self.current_level.time_limit
            self.timer_running = True
        else:
            # Level complete
            if self.current_level_num >= self.total_levels:
                self.state = GameState.VICTORY
            else:
                self.state = GameState.LEVEL_COMPLETE
                
    def next_level(self) -> None:
        """Advance to the next level."""
        self.current_level_num += 1
        self._load_level(self.current_level_num)
        self.state = GameState.PLAYING
        
    def restart_level(self) -> None:
        """Restart the current level."""
        self._load_level(self.current_level_num)
        self.state = GameState.PLAYING
        
    def get_level_progress(self) -> Tuple[int, int]:
        """Get the current question number and total questions in level."""
        if self.current_level:
            return (self.current_level.current_question_index + 1, len(self.current_level.questions))
        return (0, 0)
    
    def get_level_name(self) -> str:
        """Get the current level name."""
        if self.current_level:
            return self.current_level.level_name
        return ""
    
    def get_level_description(self) -> str:
        """Get the current level description."""
        if self.current_level:
            return self.current_level.description
        return ""
    
    def reset_game(self) -> None:
        """Reset the entire game."""
        self.current_level_num = 1
        self.lives = self.initial_lives
        self.score = 0
        self.state = GameState.MENU
        self.current_level = None
        self.current_card = None
        self.timer_running = False
        
    def reload_config(self) -> bool:
        """
        Reload configuration and reinitialize levels.
        
        Returns:
            True if successful, False otherwise
        """
        if self.config_loader and self.config_loader.reload():
            self.levels.clear()
            self._initialize_levels()
            return True
        return False