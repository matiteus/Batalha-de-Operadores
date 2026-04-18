"""
Screen class for managing the game display window.
Handles window creation, rendering, and display utilities.
"""

import pygame
from typing import Tuple, Optional
from config_loader import ConfigLoader


class Screen:
    """Manages the game window and display surface."""
    
    def __init__(self, config_loader: Optional[ConfigLoader] = None, 
                 width: int = 800, height: int = 600, title: str = "Math Logic Game"):
        """
        Initialize the game screen.
        
        Args:
            config_loader: Configuration loader instance (optional)
            width: Window width in pixels (used if no config)
            height: Window height in pixels (used if no config)
            title: Window title (used if no config)
        """
        pygame.init()
        
        # Load from config if available
        if config_loader:
            width, height = config_loader.get_window_size()
            title = config_loader.get_window_title()
            self.background_color = config_loader.get_background_color()
        else:
            self.background_color = (30, 30, 50)
        
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = config_loader.get_fps() if config_loader else 60
        
    def clear(self) -> None:
        """Clear the screen with the background color."""
        self.screen.fill(self.background_color)
        
    def update(self) -> None:
        """Update the display."""
        pygame.display.flip()
        
    def tick(self) -> float:
        """
        Control the frame rate and return delta time.
        
        Returns:
            Delta time in milliseconds
        """
        return self.clock.tick(self.fps)
    
    def get_center(self) -> Tuple[int, int]:
        """Get the center coordinates of the screen."""
        return (self.width // 2, self.height // 2)
    
    def draw_text(
        self, 
        text: str, 
        position: Tuple[int, int], 
        font_size: int = 32, 
        color: Tuple[int, int, int] = (255, 255, 255),
        center: bool = False
    ) -> pygame.Rect:
        """
        Draw text on the screen.
        
        Args:
            text: Text to display
            position: (x, y) position
            font_size: Font size in pixels
            color: RGB color tuple
            center: Whether to center the text at position
            
        Returns:
            The rectangle containing the text
        """
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
            
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def draw_rect(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        color: Tuple[int, int, int],
        border_radius: int = 0,
        center: bool = False
    ) -> pygame.Rect:
        """
        Draw a rectangle on the screen.
        
        Args:
            position: (x, y) position
            size: (width, height) size
            color: RGB color tuple
            border_radius: Corner radius for rounded rectangles
            center: Whether to center the rectangle at position
            
        Returns:
            The rectangle object
        """
        rect = pygame.Rect(0, 0, size[0], size[1])
        
        if center:
            rect.center = position
        else:
            rect.topleft = position
            
        pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)
        return rect
    
    def get_surface(self) -> pygame.Surface:
        """Get the screen surface for direct drawing operations."""
        return self.screen