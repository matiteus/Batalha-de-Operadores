"""
Configuration loader for loading game settings from JSON files.
Allows game designers to modify game parameters without touching code.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class QuestionData:
    """Data class for a single question."""
    id: str
    expression: str
    correct_answer: str
    wrong_answers: List[str]


@dataclass
class LevelData:
    """Data class for a single level."""
    level_number: int
    level_name: str
    description: str
    questions: List[QuestionData]
    time_limit: int
    points_per_correct: int


class ConfigLoader:
    """
    Loads and manages game configuration from JSON files.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self.game_settings: Dict[str, Any] = {}
        self.levels_data: List[LevelData] = []
        
    def load_all(self) -> bool:
        """
        Load all configuration files.
        
        Returns:
            True if all files loaded successfully, False otherwise
        """
        try:
            self.load_game_settings()
            self.load_levels()
            return True
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False
            
    def load_game_settings(self) -> Dict[str, Any]:
        """
        Load game settings from JSON file.
        
        Returns:
            Dictionary containing game settings
        """
        filepath = os.path.join(self.config_dir, "game_settings.json")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.game_settings = data
        return self.game_settings
    
    def load_levels(self) -> List[LevelData]:
        """
        Load level data from JSON file.
        
        Returns:
            List of LevelData objects
        """
        filepath = os.path.join(self.config_dir, "levels.json")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.levels_data = []
        
        # Get time limits and points from game settings
        time_limits = self.game_settings.get("difficulty_settings", {}).get("level_time_limits", {})
        level_points = self.game_settings.get("difficulty_settings", {}).get("level_points", {})
        
        for level_json in data.get("levels", []):
            level_num = str(level_json["level_number"])
            
            questions = [
                QuestionData(
                    id=q["id"],
                    expression=q["expression"],
                    correct_answer=q["correct_answer"],
                    wrong_answers=q["wrong_answers"]
                )
                for q in level_json["questions"]
            ]
            
            level_data = LevelData(
                level_number=level_json["level_number"],
                level_name=level_json["level_name"],
                description=level_json["description"],
                questions=questions,
                time_limit=time_limits.get(level_num, 60),
                points_per_correct=level_points.get(level_num, 100)
            )
            
            self.levels_data.append(level_data)
            
        return self.levels_data
    
    # Game Settings Getters
    def get_total_levels(self) -> int:
        """Get the total number of levels."""
        return self.game_settings.get("game_settings", {}).get("total_levels", 10)
    
    def get_initial_lives(self) -> int:
        """Get the initial number of lives."""
        return self.game_settings.get("game_settings", {}).get("initial_lives", 3)
    
    def get_max_lives(self) -> int:
        """Get the maximum number of lives."""
        return self.game_settings.get("game_settings", {}).get("max_lives", 5)
    
    def get_window_size(self) -> tuple:
        """Get the window dimensions."""
        display = self.game_settings.get("display_settings", {})
        return (
            display.get("window_width", 800),
            display.get("window_height", 600)
        )
    
    def get_window_title(self) -> str:
        """Get the window title."""
        return self.game_settings.get("display_settings", {}).get("window_title", "Math Logic Game")
    
    def get_fps(self) -> int:
        """Get the target FPS."""
        return self.game_settings.get("display_settings", {}).get("fps", 60)
    
    def get_background_color(self) -> tuple:
        """Get the background color."""
        color = self.game_settings.get("display_settings", {}).get("background_color", [30, 30, 50])
        return tuple(color)
    
    # Card Settings Getters
    def get_card_size(self) -> tuple:
        """Get the card dimensions."""
        card = self.game_settings.get("card_settings", {})
        return (
            card.get("card_width", 400),
            card.get("card_height", 200)
        )
    
    def get_option_size(self) -> tuple:
        """Get the option button dimensions."""
        card = self.game_settings.get("card_settings", {})
        return (
            card.get("option_width", 80),
            card.get("option_height", 50)
        )
    
    def get_option_spacing(self) -> int:
        """Get the spacing between option buttons."""
        return self.game_settings.get("card_settings", {}).get("option_spacing", 20)
    
    def get_border_radius(self) -> int:
        """Get the border radius for UI elements."""
        return self.game_settings.get("card_settings", {}).get("border_radius", 15)
    
    # Color Getters
    def get_color(self, color_name: str) -> tuple:
        """
        Get a color by name.
        
        Args:
            color_name: Name of the color in the config
            
        Returns:
            RGB tuple
        """
        colors = self.game_settings.get("colors", {})
        color = colors.get(color_name, [255, 255, 255])
        return tuple(color)
    
    # Font Settings Getters
    def get_font_size(self, size_name: str) -> int:
        """
        Get a font size by name.
        
        Args:
            size_name: Name of the font size setting
            
        Returns:
            Font size in pixels
        """
        fonts = self.game_settings.get("font_settings", {})
        return fonts.get(size_name, 32)
    
    # Level Data Getters
    def get_level(self, level_number: int) -> Optional[LevelData]:
        """
        Get level data by level number.
        
        Args:
            level_number: The level number (1-indexed)
            
        Returns:
            LevelData object or None if not found
        """
        for level in self.levels_data:
            if level.level_number == level_number:
                return level
        return None
    
    def get_all_levels(self) -> List[LevelData]:
        """Get all level data."""
        return self.levels_data
    
    # Utility Methods
    def reload(self) -> bool:
        """
        Reload all configuration files.
        
        Returns:
            True if successful, False otherwise
        """
        return self.load_all()
    
    def validate_config(self) -> List[str]:
        """
        Validate the configuration for common issues.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check game settings
        if self.get_initial_lives() < 1:
            errors.append("initial_lives must be at least 1")
            
        if self.get_initial_lives() > self.get_max_lives():
            errors.append("initial_lives cannot exceed max_lives")
            
        # Check levels
        for level in self.levels_data:
            if len(level.questions) == 0:
                errors.append(f"Level {level.level_number} has no questions")
                
            for question in level.questions:
                if len(question.wrong_answers) < 1:
                    errors.append(f"Question {question.id} needs at least 1 wrong answer")
                    
        return errors