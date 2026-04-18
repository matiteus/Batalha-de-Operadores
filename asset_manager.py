"""
Asset Manager for loading and generating game assets.
Handles PNG images and generates them if they don't exist.
"""

import pygame
import os
from typing import Dict, Optional, Tuple


class AssetManager:
    """
    Manages game assets - loads PNG files or generates them programmatically.
    """
    
    def __init__(self, assets_dir: str = "assets"):
        """
        Initialize the asset manager.
        
        Args:
            assets_dir: Root directory for assets
        """
        self.assets_dir = assets_dir
        self.cache: Dict[str, pygame.Surface] = {}
        
        # Asset subdirectories
        self.cards_dir = os.path.join(assets_dir, "cards")
        self.buttons_dir = os.path.join(assets_dir, "buttons")
        self.backgrounds_dir = os.path.join(assets_dir, "backgrounds")
        self.ui_dir = os.path.join(assets_dir, "ui")
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _ensure_directories(self) -> None:
        """Create asset directories if they don't exist."""
        for directory in [self.cards_dir, self.buttons_dir, self.backgrounds_dir, self.ui_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def load_image(self, path: str) -> Optional[pygame.Surface]:
        """
        Load an image from file.
        
        Args:
            path: Path to the image file
            
        Returns:
            pygame.Surface or None if file doesn't exist
        """
        if path in self.cache:
            return self.cache[path]
            
        if os.path.exists(path):
            try:
                image = pygame.image.load(path).convert_alpha()
                self.cache[path] = image
                return image
            except pygame.error:
                return None
        return None
    
    def save_image(self, surface: pygame.Surface, path: str) -> bool:
        """
        Save a surface to a PNG file.
        
        Args:
            surface: pygame.Surface to save
            path: Path to save the image
            
        Returns:
            True if saved successfully
        """
        try:
            pygame.image.save(surface, path)
            return True
        except pygame.error:
            return False
    
    # ==================== CARD ASSETS ====================
    
    def get_card_background(self, width: int = 400, height: int = 200, 
                            color: Tuple[int, int, int] = (50, 50, 80),
                            border_radius: int = 15) -> pygame.Surface:
        """
        Get or create a card background.
        
        Args:
            width: Card width
            height: Card height
            color: Background color
            border_radius: Corner radius
            
        Returns:
            pygame.Surface with the card background
        """
        cache_key = f"card_bg_{width}_{height}_{color}_{border_radius}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Try to load from file
        filename = f"card_bg_{width}x{height}.png"
        filepath = os.path.join(self.cards_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate the card background
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, surface.get_rect(), border_radius=border_radius)
        
        # Add border
        border_color = (100, 100, 150)
        pygame.draw.rect(surface, border_color, surface.get_rect(), width=3, border_radius=border_radius)
        
        # Save for future use
        self.save_image(surface, filepath)
        
        self.cache[cache_key] = surface
        return surface
    
    def get_card_correct(self, width: int = 400, height: int = 200) -> pygame.Surface:
        """Get or create a correct answer card background."""
        cache_key = f"card_correct_{width}_{height}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        filename = f"card_correct_{width}x{height}.png"
        filepath = os.path.join(self.cards_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (50, 150, 50), surface.get_rect(), border_radius=15)
        pygame.draw.rect(surface, (100, 200, 100), surface.get_rect(), width=3, border_radius=15)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    def get_card_wrong(self, width: int = 400, height: int = 200) -> pygame.Surface:
        """Get or create a wrong answer card background."""
        cache_key = f"card_wrong_{width}_{height}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        filename = f"card_wrong_{width}x{height}.png"
        filepath = os.path.join(self.cards_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (150, 50, 50), surface.get_rect(), border_radius=15)
        pygame.draw.rect(surface, (200, 100, 100), surface.get_rect(), width=3, border_radius=15)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    # ==================== BUTTON ASSETS ====================
    
    def get_button(self, width: int = 80, height: int = 50,
                   color: Tuple[int, int, int] = (60, 60, 90),
                   hover_color: Tuple[int, int, int] = (100, 100, 140),
                   border_radius: int = 10,
                   is_hovered: bool = False) -> pygame.Surface:
        """
        Get or create a button surface.
        
        Args:
            width: Button width
            height: Button height
            color: Normal color
            hover_color: Color when hovered
            border_radius: Corner radius
            is_hovered: Whether button is hovered
            
        Returns:
            pygame.Surface with the button
        """
        cache_key = f"button_{width}_{height}_{color}_{hover_color}_{border_radius}_{is_hovered}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        state = "hover" if is_hovered else "normal"
        filename = f"button_{width}x{height}_{state}.png"
        filepath = os.path.join(self.buttons_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate button
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        btn_color = hover_color if is_hovered else color
        pygame.draw.rect(surface, btn_color, surface.get_rect(), border_radius=border_radius)
        pygame.draw.rect(surface, (100, 100, 150), surface.get_rect(), width=2, border_radius=border_radius)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    # ==================== BACKGROUND ASSETS ====================
    
    def get_background(self, width: int = 800, height: int = 600,
                       color: Tuple[int, int, int] = (30, 30, 50)) -> pygame.Surface:
        """
        Get or create a background surface.
        
        Args:
            width: Background width
            height: Background height
            color: Background color
            
        Returns:
            pygame.Surface with the background
        """
        cache_key = f"bg_{width}_{height}_{color}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        filename = f"background_{width}x{height}.png"
        filepath = os.path.join(self.backgrounds_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate background with gradient effect
        surface = pygame.Surface((width, height))
        surface.fill(color)
        
        # Add subtle gradient
        for y in range(height):
            alpha = int(255 * (1 - y / height * 0.3))
            gradient_color = (color[0] + 10, color[1] + 10, color[2] + 20)
            pygame.draw.line(surface, gradient_color, (0, y), (width, y))
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    # ==================== UI ASSETS ====================
    
    def get_feedback_panel(self, width: int = 400, height: int = 200,
                          is_correct: bool = True) -> pygame.Surface:
        """
        Get or create a feedback panel for answer results.
        
        Args:
            width: Panel width
            height: Panel height
            is_correct: Whether the answer was correct
            
        Returns:
            pygame.Surface with the feedback panel
        """
        cache_key = f"feedback_{width}_{height}_{'correct' if is_correct else 'wrong'}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        state = "correct" if is_correct else "wrong"
        filename = f"feedback_{state}_{width}x{height}.png"
        filepath = os.path.join(self.ui_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate feedback panel
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if is_correct:
            color = (50, 150, 50)
            border_color = (100, 200, 100)
        else:
            color = (150, 50, 50)
            border_color = (200, 100, 100)
            
        pygame.draw.rect(surface, color, surface.get_rect(), border_radius=20)
        pygame.draw.rect(surface, border_color, surface.get_rect(), width=4, border_radius=20)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    def get_heart_icon(self, size: int = 32, filled: bool = True) -> pygame.Surface:
        """
        Get or create a heart icon for lives display.
        
        Args:
            size: Icon size
            filled: Whether the heart is filled
            
        Returns:
            pygame.Surface with the heart icon
        """
        cache_key = f"heart_{size}_{'filled' if filled else 'empty'}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        filename = f"heart_{'filled' if filled else 'empty'}_{size}.png"
        filepath = os.path.join(self.ui_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate heart icon
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        color = (255, 100, 100) if filled else (100, 100, 100)
        
        # Draw heart shape using circles
        center_x, center_y = size // 2, size // 2
        radius = size // 4
        
        # Two circles for top of heart
        pygame.draw.circle(surface, color, (center_x - radius // 2, center_y - radius // 2), radius)
        pygame.draw.circle(surface, color, (center_x + radius // 2, center_y - radius // 2), radius)
        
        # Triangle for bottom of heart
        points = [
            (center_x - radius - 2, center_y - 2),
            (center_x + radius + 2, center_y - 2),
            (center_x, center_y + radius + 2)
        ]
        pygame.draw.polygon(surface, color, points)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    def get_timer_icon(self, size: int = 32) -> pygame.Surface:
        """
        Get or create a timer/clock icon.
        
        Args:
            size: Icon size
            
        Returns:
            pygame.Surface with the timer icon
        """
        cache_key = f"timer_{size}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        filename = f"timer_{size}.png"
        filepath = os.path.join(self.ui_dir, filename)
        
        image = self.load_image(filepath)
        if image:
            self.cache[cache_key] = image
            return image
            
        # Generate timer icon
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (255, 255, 255)
        
        center = size // 2
        radius = size // 2 - 2
        
        # Circle outline
        pygame.draw.circle(surface, color, (center, center), radius, 2)
        
        # Clock hands
        pygame.draw.line(surface, color, (center, center), (center, center - radius + 4), 2)
        pygame.draw.line(surface, color, (center, center), (center + radius - 4, center), 2)
        
        self.save_image(surface, filepath)
        self.cache[cache_key] = surface
        return surface
    
    def clear_cache(self) -> None:
        """Clear the asset cache."""
        self.cache.clear()