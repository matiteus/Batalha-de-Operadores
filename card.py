"""
Card class for displaying math logic questions.
Represents a single question card with expression and answer options.
"""

import pygame
from typing import List, Tuple, Optional, Callable
from enum import Enum
from config_loader import ConfigLoader
from asset_manager import AssetManager


class CardState(Enum):
    """Possible states for a card."""
    IDLE = "idle"
    HOVER = "hover"
    CORRECT = "correct"
    WRONG = "wrong"


class Card:
    """
    Represents a question card in the game.
    Displays a math expression and multiple answer options.
    """
    
    def __init__(
        self,
        expression: str,
        correct_answer: str,
        wrong_answers: List[str],
        position: Tuple[int, int] = (0, 0),
        config_loader: Optional[ConfigLoader] = None,
        asset_manager: Optional[AssetManager] = None
    ):
        """
        Initialize a question card.
        
        Args:
            expression: The math expression (e.g., "5 ? 3 = 8")
            correct_answer: The correct answer/option
            wrong_answers: List of incorrect answer options
            position: Center position of the card
            config_loader: Configuration loader for settings
            asset_manager: Asset manager for loading/generating assets
        """
        self.expression = expression
        self.correct_answer = correct_answer
        self.all_answers = [correct_answer] + wrong_answers
        self.position = position
        self.state = CardState.IDLE
        self.asset_manager = asset_manager
        
        # Load settings from config
        if config_loader:
            self.card_size = config_loader.get_card_size()
            self.option_size = config_loader.get_option_size()
            self.option_spacing = config_loader.get_option_spacing()
            self.border_radius = config_loader.get_border_radius()
            
            # Colors from config
            self.bg_color = config_loader.get_color("card_idle")
            self.hover_color = config_loader.get_color("card_hover")
            self.correct_color = config_loader.get_color("card_correct")
            self.wrong_color = config_loader.get_color("card_wrong")
            self.text_color = config_loader.get_color("text_primary")
            self.border_color = config_loader.get_color("border")
            self.button_idle_color = config_loader.get_color("button_idle")
            self.button_hover_color = config_loader.get_color("button_hover")
            
            # Font sizes
            self.expression_font_size = config_loader.get_font_size("heading_size")
            self.option_font_size = config_loader.get_font_size("option_size")
        else:
            # Default values
            self.card_size = (400, 200)
            self.option_size = (80, 50)
            self.option_spacing = 20
            self.border_radius = 15
            
            self.bg_color = (50, 50, 80)
            self.hover_color = (70, 70, 100)
            self.correct_color = (50, 150, 50)
            self.wrong_color = (150, 50, 50)
            self.text_color = (255, 255, 255)
            self.border_color = (100, 100, 150)
            self.button_idle_color = (60, 60, 90)
            self.button_hover_color = (100, 100, 140)
            
            self.expression_font_size = 48
            self.option_font_size = 36
        
        # Option buttons
        self.option_buttons: List[pygame.Rect] = []
        self.hovered_option: Optional[int] = None
        self._calculate_option_positions()
        
    def _calculate_option_positions(self) -> None:
        """Calculate positions for answer option buttons."""
        self.option_buttons.clear()
        num_options = len(self.all_answers)
        
        option_width, option_height = self.option_size
        
        total_width = num_options * option_width + (num_options - 1) * self.option_spacing
        start_x = self.position[0] - total_width // 2
        start_y = self.position[1] + 50
        
        for i in range(num_options):
            rect = pygame.Rect(
                start_x + i * (option_width + self.option_spacing),
                start_y,
                option_width,
                option_height
            )
            self.option_buttons.append(rect)
            
    def set_position(self, position: Tuple[int, int]) -> None:
        """Update the card position and recalculate option positions."""
        self.position = position
        self._calculate_option_positions()
        
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update card state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        self.hovered_option = None
        
        for i, rect in enumerate(self.option_buttons):
            if rect.collidepoint(mouse_pos):
                self.hovered_option = i
                break
                
    def check_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        Check if an option was clicked.
        
        Args:
            mouse_pos: Mouse click position
            
        Returns:
            The clicked answer string, or None if no option was clicked
        """
        for i, rect in enumerate(self.option_buttons):
            if rect.collidepoint(mouse_pos):
                return self.all_answers[i]
        return None
    
    def is_answer_correct(self, answer: str) -> bool:
        """Check if the given answer is correct."""
        return answer == self.correct_answer
    
    def set_state(self, state: CardState) -> None:
        """Set the card state."""
        self.state = state
        
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the card on the screen.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Determine card background color based on state
        if self.state == CardState.CORRECT:
            bg_color = self.correct_color
        elif self.state == CardState.WRONG:
            bg_color = self.wrong_color
        elif self.state == CardState.HOVER:
            bg_color = self.hover_color
        else:
            bg_color = self.bg_color
            
        # Draw card background (use asset manager if available)
        card_rect = pygame.Rect(
            self.position[0] - self.card_size[0] // 2,
            self.position[1] - self.card_size[1] // 2,
            self.card_size[0],
            self.card_size[1]
        )
        
        if self.asset_manager:
            # Use asset manager to get card background
            if self.state == CardState.CORRECT:
                card_bg = self.asset_manager.get_card_correct(self.card_size[0], self.card_size[1])
            elif self.state == CardState.WRONG:
                card_bg = self.asset_manager.get_card_wrong(self.card_size[0], self.card_size[1])
            else:
                card_bg = self.asset_manager.get_card_background(
                    self.card_size[0], self.card_size[1], bg_color, self.border_radius
                )
            screen.blit(card_bg, card_rect)
        else:
            # Draw without asset manager
            pygame.draw.rect(screen, bg_color, card_rect, border_radius=self.border_radius)
            pygame.draw.rect(screen, self.border_color, card_rect, width=3, border_radius=self.border_radius)
        
        # Draw expression text
        font = pygame.font.Font(None, self.expression_font_size)
        text_surface = font.render(self.expression, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.position[0], self.position[1] - 30))
        screen.blit(text_surface, text_rect)
        
        # Draw option buttons
        option_font = pygame.font.Font(None, self.option_font_size)
        for i, rect in enumerate(self.option_buttons):
            if self.asset_manager:
                # Use asset manager for button
                btn_surface = self.asset_manager.get_button(
                    self.option_size[0], self.option_size[1],
                    self.button_idle_color, self.button_hover_color,
                    10, self.hovered_option == i
                )
                screen.blit(btn_surface, rect)
            else:
                # Determine button color
                if self.hovered_option == i:
                    btn_color = self.button_hover_color
                else:
                    btn_color = self.button_idle_color
                    
                pygame.draw.rect(screen, btn_color, rect, border_radius=10)
                pygame.draw.rect(screen, self.border_color, rect, width=2, border_radius=10)
            
            # Draw option text
            text_surface = option_font.render(self.all_answers[i], True, self.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
            
    def reset(self) -> None:
        """Reset the card to its initial state."""
        self.state = CardState.IDLE
        self.hovered_option = None