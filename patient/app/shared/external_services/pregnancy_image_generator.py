import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Ellipse, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Dict, Tuple
import os
import requests
from io import BytesIO

class BabySizeImageGenerator:
    def __init__(self):
        self.week_data = self._initialize_week_data()
        self.colors = {
            'background': '#f8f9fa',
            'baby': '#ffb3ba',
            'text': '#333333',
            'accent': '#ff6b6b'
        }
    
    def _initialize_week_data(self) -> Dict:
        """Initialize baby size data for each week with fruit/vegetable emojis and colors"""
        return {
            1: {"size": "Poppy seed", "diameter": 0.1, "color": "#8B4513", "emoji": "🌱", "shape": "circle"},
            2: {"size": "Poppy seed", "diameter": 0.1, "color": "#8B4513", "emoji": "🌱", "shape": "circle"},
            3: {"size": "Poppy seed", "diameter": 0.1, "color": "#8B4513", "emoji": "🌱", "shape": "circle"},
            4: {"size": "Poppy seed", "diameter": 0.1, "color": "#8B4513", "emoji": "🌱", "shape": "circle"},
            5: {"size": "Sesame seed", "diameter": 0.2, "color": "#D2691E", "emoji": "🌰", "shape": "circle"},
            6: {"size": "Lentil", "diameter": 0.3, "color": "#8B4513", "emoji": "🫘", "shape": "circle"},
            7: {"size": "Blueberry", "diameter": 0.4, "color": "#4169E1", "emoji": "🫐", "shape": "circle"},
            8: {"size": "Raspberry", "diameter": 0.5, "color": "#DC143C", "emoji": "🫐", "shape": "circle"},
            9: {"size": "Grape", "diameter": 0.6, "color": "#9370DB", "emoji": "🍇", "shape": "oval"},
            10: {"size": "Coconut", "diameter": 0.7, "color": "#8B4513", "emoji": "🥥", "shape": "circle"},
            11: {"size": "Lime", "diameter": 0.8, "color": "#32CD32", "emoji": "🍋", "shape": "oval"},
            12: {"size": "Plum", "diameter": 0.9, "color": "#8B008B", "emoji": "🍇", "shape": "oval"},
            13: {"size": "Peach", "diameter": 1.0, "color": "#FFB6C1", "emoji": "🍑", "shape": "oval"},
            14: {"size": "Lemon", "diameter": 1.1, "color": "#FFD700", "emoji": "🍋", "shape": "oval"},
            15: {"size": "Apple", "diameter": 1.2, "color": "#FF0000", "emoji": "🍎", "shape": "oval"},
            16: {"size": "Avocado", "diameter": 1.3, "color": "#228B22", "emoji": "🥑", "shape": "oval"},
            17: {"size": "Onion", "diameter": 1.4, "color": "#F0E68C", "emoji": "🧅", "shape": "circle"},
            18: {"size": "Sweet potato", "diameter": 1.5, "color": "#FF8C00", "emoji": "🍠", "shape": "oval"},
            19: {"size": "Mango", "diameter": 1.6, "color": "#FFA500", "emoji": "🥭", "shape": "oval"},
            20: {"size": "Banana", "diameter": 1.7, "color": "#FFFF00", "emoji": "🍌", "shape": "banana"},
            21: {"size": "Carrot", "diameter": 1.8, "color": "#FF8C00", "emoji": "🥕", "shape": "carrot"},
            22: {"size": "Corn cob", "diameter": 1.9, "color": "#FFD700", "emoji": "🌽", "shape": "oval"},
            23: {"size": "Grapefruit", "diameter": 2.0, "color": "#FF6347", "emoji": "🍊", "shape": "circle"},
            24: {"size": "Cantaloupe", "diameter": 2.1, "color": "#FFA500", "emoji": "🍈", "shape": "oval"},
            25: {"size": "Cauliflower", "diameter": 2.2, "color": "#F5F5DC", "emoji": "🥬", "shape": "oval"},
            26: {"size": "Butternut squash", "diameter": 2.3, "color": "#D2691E", "emoji": "🎃", "shape": "oval"},
            27: {"size": "Head of lettuce", "diameter": 2.4, "color": "#90EE90", "emoji": "🥬", "shape": "oval"},
            28: {"size": "Eggplant", "diameter": 2.5, "color": "#8B008B", "emoji": "🍆", "shape": "oval"},
            29: {"size": "Butternut squash", "diameter": 2.6, "color": "#D2691E", "emoji": "🎃", "shape": "oval"},
            30: {"size": "Cabbage", "diameter": 2.7, "color": "#90EE90", "emoji": "🥬", "shape": "oval"},
            31: {"size": "Coconut", "diameter": 2.8, "color": "#8B4513", "emoji": "🥥", "shape": "circle"},
            32: {"size": "Jicama", "diameter": 2.9, "color": "#F5F5DC", "emoji": "🥔", "shape": "oval"},
            33: {"size": "Pineapple", "diameter": 3.0, "color": "#FFD700", "emoji": "🍍", "shape": "oval"},
            34: {"size": "Cantaloupe", "diameter": 3.1, "color": "#FFA500", "emoji": "🍈", "shape": "oval"},
            35: {"size": "Honeydew melon", "diameter": 3.2, "color": "#98FB98", "emoji": "🍈", "shape": "oval"},
            36: {"size": "Romaine lettuce", "diameter": 3.3, "color": "#90EE90", "emoji": "🥬", "shape": "oval"},
            37: {"size": "Swiss chard", "diameter": 3.4, "color": "#90EE90", "emoji": "🥬", "shape": "oval"},
            38: {"size": "Leek", "diameter": 3.5, "color": "#90EE90", "emoji": "🧄", "shape": "oval"},
            39: {"size": "Mini watermelon", "diameter": 3.6, "color": "#32CD32", "emoji": "🍉", "shape": "oval"},
            40: {"size": "Small pumpkin", "diameter": 3.7, "color": "#FF8C00", "emoji": "🎃", "shape": "oval"}
        }
    
    def generate_baby_size_image(self, week: int, size: Tuple[int, int] = (400, 300)) -> str:
        """
        Generate a fruit/vegetable-shaped baby size visualization image
        
        Args:
            week: Pregnancy week (1-40)
            size: Image size (width, height)
            
        Returns:
            Base64 encoded image string
        """
        if week not in self.week_data:
            week = 10  # Default to week 10
        
        data = self.week_data[week]
        
        # Create figure and axis
        fig, ax = plt.subplots(1, 1, figsize=(size[0]/100, size[1]/100))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7.5)
        ax.set_aspect('equal')
        
        # Remove axes
        ax.axis('off')
        
        # Set background color
        fig.patch.set_facecolor(self.colors['background'])
        
        # Calculate baby size (scaled for visualization)
        baby_diameter = max(0.5, min(4.0, data['diameter'] * 2))  # Scale for visibility
        
        # Draw fruit/vegetable shape based on week
        self._draw_fruit_shape(ax, data, baby_diameter, 5, 4)
        
        # Add fruit emoji
        ax.text(5, 4, data['emoji'], 
                ha='center', va='center', 
                fontsize=int(baby_diameter * 8), 
                alpha=0.8)
        
        # Add week text
        ax.text(5, 6.5, f"Week {week}", 
                ha='center', va='center', 
                fontsize=20, fontweight='bold', 
                color=self.colors['text'])
        
        # Add size comparison text
        ax.text(5, 6, f"Size: {data['size']}", 
                ha='center', va='center', 
                fontsize=14, 
                color=self.colors['text'])
        
        # Add diameter text
        ax.text(5, 5.5, f"~{data['diameter']}cm", 
                ha='center', va='center', 
                fontsize=12, 
                color=self.colors['accent'])
        
        # Add hands cradling the baby (for larger weeks)
        if week >= 20:
            # Left hand
            left_hand = Ellipse((3, 3.5), 1.5, 0.8, 
                              angle=30, facecolor='#ffdbac', 
                              edgecolor='#ff6b6b', linewidth=1, alpha=0.7)
            ax.add_patch(left_hand)
            
            # Right hand
            right_hand = Ellipse((7, 3.5), 1.5, 0.8, 
                               angle=-30, facecolor='#ffdbac', 
                               edgecolor='#ff6b6b', linewidth=1, alpha=0.7)
            ax.add_patch(right_hand)
        
        # Add decorative elements
        if week >= 15:
            # Add some stars around the baby
            for i in range(3):
                x = 2 + i * 3
                y = 2 + (i % 2) * 2
                ax.plot(x, y, '*', color='#ffd700', markersize=8, alpha=0.6)
        
        # Add trimester indicator
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        ax.text(5, 1, f"Trimester {trimester}", 
                ha='center', va='center', 
                fontsize=10, 
                color=self.colors['accent'],
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def _draw_fruit_shape(self, ax, data, diameter, x, y):
        """Draw different fruit/vegetable shapes based on the data"""
        shape = data['shape']
        color = data['color']
        
        if shape == "circle":
            circle = Circle((x, y), diameter/2, 
                          facecolor=color, 
                          edgecolor='#333333', 
                          linewidth=2, alpha=0.8)
            ax.add_patch(circle)
            
        elif shape == "oval":
            ellipse = Ellipse((x, y), diameter, diameter*0.8, 
                            facecolor=color, 
                            edgecolor='#333333', 
                            linewidth=2, alpha=0.8)
            ax.add_patch(ellipse)
            
        elif shape == "banana":
            # Draw banana shape
            banana = Ellipse((x, y), diameter, diameter*0.4, 
                           angle=30, facecolor=color, 
                           edgecolor='#333333', linewidth=2, alpha=0.8)
            ax.add_patch(banana)
            
        elif shape == "carrot":
            # Draw carrot shape (triangle-like)
            carrot_points = np.array([
                [x, y + diameter/2],
                [x - diameter/3, y - diameter/2],
                [x + diameter/3, y - diameter/2]
            ])
            carrot = patches.Polygon(carrot_points, 
                                   facecolor=color, 
                                   edgecolor='#333333', 
                                   linewidth=2, alpha=0.8)
            ax.add_patch(carrot)
            
        else:
            # Default to circle
            circle = Circle((x, y), diameter/2, 
                          facecolor=color, 
                          edgecolor='#333333', 
                          linewidth=2, alpha=0.8)
            ax.add_patch(circle)
    
    def generate_simple_baby_image(self, week: int) -> str:
        """
        Generate a very simple fruit/vegetable baby size image using PIL
        
        Args:
            week: Pregnancy week (1-40)
            
        Returns:
            Base64 encoded image string
        """
        if week not in self.week_data:
            week = 10
        
        data = self.week_data[week]
        
        # Create image
        width, height = 300, 200
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Calculate baby size
        baby_diameter = max(20, min(120, int(data['diameter'] * 30)))
        
        # Draw fruit/vegetable shape
        baby_x = width // 2
        baby_y = height // 2
        
        self._draw_simple_fruit_shape(draw, data, baby_diameter, baby_x, baby_y)
        
        # Add fruit emoji
        try:
            # Try to use a larger font for emoji
            emoji_font = ImageFont.truetype("arial.ttf", size=baby_diameter//2)
        except:
            emoji_font = ImageFont.load_default()
        
        # Draw emoji
        draw.text((baby_x, baby_y), data['emoji'], 
                 fill='#333333', font=emoji_font, anchor='mm')
        
        # Add text
        try:
            # Try to use a default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        # Week text
        draw.text((width//2, 20), f"Week {week}", 
                 fill='#333333', font=font_large, anchor='mm')
        
        # Size text
        draw.text((width//2, 40), f"Size: {data['size']}", 
                 fill='#333333', font=font_small, anchor='mm')
        
        # Diameter text
        draw.text((width//2, 55), f"~{data['diameter']}cm", 
                 fill='#ff6b6b', font=font_small, anchor='mm')
        
        # Trimester
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        draw.text((width//2, height - 20), f"Trimester {trimester}", 
                 fill='#ff6b6b', font=font_small, anchor='mm')
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
    
    def _draw_simple_fruit_shape(self, draw, data, diameter, x, y):
        """Draw simple fruit/vegetable shapes using PIL"""
        shape = data['shape']
        color = data['color']
        
        left = x - diameter // 2
        top = y - diameter // 2
        right = x + diameter // 2
        bottom = y + diameter // 2
        
        if shape == "circle":
            draw.ellipse([left, top, right, bottom], 
                        fill=color, outline='#333333', width=2)
                        
        elif shape == "oval":
            # Draw oval by scaling the ellipse
            oval_height = int(diameter * 0.8)
            oval_top = y - oval_height // 2
            oval_bottom = y + oval_height // 2
            draw.ellipse([left, oval_top, right, oval_bottom], 
                        fill=color, outline='#333333', width=2)
                        
        elif shape == "banana":
            # Draw banana shape (rotated oval)
            banana_height = int(diameter * 0.4)
            banana_top = y - banana_height // 2
            banana_bottom = y + banana_height // 2
            # Create a rotated banana by drawing multiple ellipses
            for i in range(5):
                offset = i - 2
                draw.ellipse([left + offset, banana_top, right + offset, banana_bottom], 
                           fill=color, outline='#333333', width=1)
                           
        elif shape == "carrot":
            # Draw carrot shape (triangle)
            carrot_points = [
                (x, top),
                (left, bottom),
                (right, bottom)
            ]
            draw.polygon(carrot_points, fill=color, outline='#333333', width=2)
            
        else:
            # Default to circle
            draw.ellipse([left, top, right, bottom], 
                        fill=color, outline='#333333', width=2)
