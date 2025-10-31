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
import json
import asyncio

class BabySizeImageGenerator:
    def __init__(self, openai_service=None):
        self.week_data = self._initialize_week_data()
        self.colors = {
            'background': '#f8f9fa',
            'baby': '#ffb3ba',
            'text': '#333333',
            'accent': '#ff6b6b'
        }
        self.fruit_images_cache = {}
        self.fruit_image_urls = self._get_fruit_image_urls()
        self.openai_service = openai_service
    
    def _get_fruit_image_urls(self) -> Dict:
        """Get URLs for real fruit/vegetable images - high quality photos"""
        return {
            "Poppy seed": "https://images.pexels.com/photos/6832055/pexels-photo-6832055.jpeg?w=400&h=400&fit=crop",
            "Sesame seed": "https://images.pexels.com/photos/6832055/pexels-photo-6832055.jpeg?w=400&h=400&fit=crop",
            "Blueberry": "https://images.pexels.com/photos/2170473/pexels-photo-2170473.jpeg?w=400&h=400&fit=crop",
            "Raspberry": "https://images.pexels.com/photos/1649318/pexels-photo-1649318.jpeg?w=400&h=400&fit=crop", 
            "Grape": "https://images.pexels.com/photos/23042/pexels-photo.jpg?w=400&h=400&fit=crop",
            "Lime": "https://images.pexels.com/photos/1536869/pexels-photo-1536869.jpeg?w=400&h=400&fit=crop",
            "Plum": "https://images.pexels.com/photos/5945857/pexels-photo-5945857.jpeg?w=400&h=400&fit=crop",
            "Peach": "https://images.pexels.com/photos/4022092/pexels-photo-4022092.jpeg?w=400&h=400&fit=crop",
            "Lemon": "https://images.pexels.com/photos/1414110/pexels-photo-1414110.jpeg?w=400&h=400&fit=crop",
            "Apple": "https://images.pexels.com/photos/102104/pexels-photo-102104.jpeg?w=400&h=400&fit=crop",
            "Avocado": "https://images.pexels.com/photos/557659/pexels-photo-557659.jpeg?w=400&h=400&fit=crop",
            "Onion": "https://images.pexels.com/photos/1323646/pexels-photo-1323646.jpeg?w=400&h=400&fit=crop",
            "Sweet potato": "https://images.pexels.com/photos/2286776/pexels-photo-2286776.jpeg?w=400&h=400&fit=crop",
            "Mango": "https://images.pexels.com/photos/2294471/pexels-photo-2294471.jpeg?w=400&h=400&fit=crop",
            "Banana": "https://images.pexels.com/photos/2872755/pexels-photo-2872755.jpeg?w=400&h=400&fit=crop",
            "Carrot": "https://images.pexels.com/photos/3650647/pexels-photo-3650647.jpeg?w=400&h=400&fit=crop",
            "Corn": "https://images.pexels.com/photos/547263/pexels-photo-547263.jpeg?w=400&h=400&fit=crop",
            "Corn cob": "https://images.pexels.com/photos/547263/pexels-photo-547263.jpeg?w=400&h=400&fit=crop",
            "Grapefruit": "https://images.pexels.com/photos/1435735/pexels-photo-1435735.jpeg?w=400&h=400&fit=crop",
            "Cantaloupe": "https://images.pexels.com/photos/4022089/pexels-photo-4022089.jpeg?w=400&h=400&fit=crop",
            "Cauliflower": "https://images.pexels.com/photos/461428/pexels-photo-461428.jpeg?w=400&h=400&fit=crop",
            "Eggplant": "https://images.pexels.com/photos/321551/pexels-photo-321551.jpeg?w=400&h=400&fit=crop",
            "Zucchini": "https://images.pexels.com/photos/4116519/pexels-photo-4116519.jpeg?w=400&h=400&fit=crop",
            "Cabbage": "https://images.pexels.com/photos/2255935/pexels-photo-2255935.jpeg?w=400&h=400&fit=crop",
            "Pineapple": "https://images.pexels.com/photos/947879/pexels-photo-947879.jpeg?w=400&h=400&fit=crop",
            "Papaya": "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=200&h=200&fit=crop&crop=center",
            "Honeydew": "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=200&h=200&fit=crop&crop=center",
            "Rutabaga": "https://images.unsplash.com/photo-1518977956812-cd3dbadaaf31?w=200&h=200&fit=crop&crop=center",
            "Butternut squash": "https://images.unsplash.com/photo-1518977956812-cd3dbadaaf31?w=200&h=200&fit=crop&crop=center",
            "Watermelon": "https://images.unsplash.com/photo-1571575173700-afb9492e6a50?w=200&h=200&fit=crop&crop=center",
            "Pumpkin": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=200&fit=crop&crop=center"
        }
    
    def _fetch_fruit_image(self, fruit_name: str) -> str:
        """Fetch real fruit image from URL and convert to base64"""
        if fruit_name in self.fruit_images_cache:
            return self.fruit_images_cache[fruit_name]
        
        try:
            # Use Unsplash for high-quality fruit images
            if fruit_name in self.fruit_image_urls:
                url = self.fruit_image_urls[fruit_name]
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    # Convert to base64
                    img_base64 = base64.b64encode(response.content).decode()
                    self.fruit_images_cache[fruit_name] = f"data:image/jpeg;base64,{img_base64}"
                    return self.fruit_images_cache[fruit_name]
        except Exception as e:
            print(f"Error fetching fruit image for {fruit_name}: {e}")
        
        # Fallback to emoji if image fetch fails
        return None
    
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
    
    def generate_baby_size_image_with_real_fruit(self, week: int) -> str:
        """Generate baby size comparison with real fruit/vegetable images"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        baby_diameter = data['diameter'] * 2  # Scale for visualization
        
        # Create figure with larger size for better image quality
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Set background
        ax.set_facecolor(self.colors['background'])
        
        # Try to get real fruit image
        fruit_image_data = self._fetch_fruit_image(data['size'])
        
        # Draw baby representation
        self._draw_baby_representation(ax, data, baby_diameter, 5, 4)
        
        # Add real fruit image if available, otherwise fallback to emoji
        if fruit_image_data:
            try:
                # Create a separate figure for the fruit image
                fruit_fig, fruit_ax = plt.subplots(figsize=(2, 2))
                fruit_ax.axis('off')
                
                # Load the fruit image
                import base64
                img_data = base64.b64decode(fruit_image_data.split(',')[1])
                fruit_img = Image.open(BytesIO(img_data))
                fruit_img = fruit_img.resize((100, 100), Image.Resampling.LANCZOS)
                
                # Add fruit image to main plot
                ax.imshow(fruit_img, extent=[3.5, 6.5, 2.5, 3.5], aspect='auto', alpha=0.9)
                fruit_fig.clf()
                plt.close(fruit_fig)
                
                # Add "Real" label
                ax.text(5, 2.2, "Real Fruit Image", 
                        ha='center', va='center', 
                        fontsize=10, fontweight='bold',
                        color=self.colors['accent'],
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                        
            except Exception as e:
                print(f"Error displaying real fruit image: {e}")
                # Fallback to emoji
                ax.text(5, 3, data['emoji'], 
                        ha='center', va='center', 
                        fontsize=int(baby_diameter * 8), 
                        alpha=0.8)
        else:
            # Fallback to emoji
            ax.text(5, 3, data['emoji'], 
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
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_real_fruit_only_image(self, week: int) -> str:
        """Generate image showing a REAL PHOTO of fruit/vegetable with baby size information"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        fruit_name = data['size']
        
        # Create figure with clean layout
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_facecolor('white')
        
        # Title - "How big is your baby?"
        ax.text(4, 9.2, "How big is your baby?", 
                ha='center', va='center', 
                fontsize=24, fontweight='bold', 
                color='#4a2c5a', family='sans-serif')
        
        # Try to load real fruit image
        fruit_img = self._fetch_fruit_image(fruit_name)
        
        if fruit_img:
            # Display real fruit photo
            fruit_display_center_x = 4
            fruit_display_center_y = 6.2
            
            # Resize fruit image to fit nicely
            img_size = 3.0  # Size in plot units
            extent = [fruit_display_center_x - img_size/2, fruit_display_center_x + img_size/2,
                     fruit_display_center_y - img_size/2, fruit_display_center_y + img_size/2]
            
            ax.imshow(fruit_img, extent=extent, aspect='auto', zorder=2)
            
            # Add subtle circular frame
            frame_circle = plt.Circle((fruit_display_center_x, fruit_display_center_y), img_size/2 + 0.1, 
                                     fill=False, edgecolor='#e0e0e0', linewidth=3, zorder=3)
            ax.add_patch(frame_circle)
        else:
            # Fallback to emoji if photo unavailable
            fruit_display_center_x = 4
            fruit_display_center_y = 6.2
            
            background_circle = plt.Circle((fruit_display_center_x, fruit_display_center_y), 1.8, 
                                         facecolor='#f5f5f5', edgecolor='#d0d0d0', linewidth=1)
            ax.add_patch(background_circle)
            
            ax.text(fruit_display_center_x, fruit_display_center_y, data['emoji'], 
                    ha='center', va='center', fontsize=100, color='#2c3e50')
        
        # Pink ribbon banner with week number
        ribbon_y = 4.3
        ribbon_width = 2.8
        ribbon_height = 0.65
        
        ribbon = plt.Rectangle((4 - ribbon_width/2, ribbon_y - ribbon_height/2), 
                             ribbon_width, ribbon_height,
                             facecolor='#e91e63', edgecolor='#e91e63', 
                             alpha=1.0, linewidth=0, zorder=4)
        ax.add_patch(ribbon)
        
        ax.text(4, ribbon_y, f"Week {week}", 
                ha='center', va='center', 
                fontsize=18, fontweight='bold',
                color='white', family='sans-serif', zorder=5)
        
        # Fruit/vegetable name (baby size comparison)
        ax.text(4, 3.5, f"{fruit_name}", 
                ha='center', va='center', 
                fontsize=20, fontweight='bold',
                color='#4a2c5a', family='sans-serif')
        
        # Subtitle text
        ax.text(4, 3.1, "Baby Size Comparison", 
                ha='center', va='center', 
                fontsize=12,
                color='#6c757d', family='sans-serif', style='italic')
        
        # Length/Weight information
        length_weight = self._get_length_weight_for_week(week)
        ax.text(4, 2.6, length_weight, 
                ha='center', va='center', 
                fontsize=12, 
                color='#6c757d', family='sans-serif')
        
        # Trimester badge
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        trimester_color = '#e74c3c' if trimester == 1 else '#f39c12' if trimester == 2 else '#27ae60'
        
        ax.text(4, 1.9, f"Trimester {trimester}", 
                ha='center', va='center', 
                fontsize=13, fontweight='bold',
                color='white', family='sans-serif',
                bbox=dict(boxstyle="round,pad=0.5", facecolor=trimester_color, alpha=1.0, edgecolor=trimester_color))
        
        # Progress indicator
        ax.text(4, 1.3, f"Week {week} of 40", 
                ha='center', va='center', 
                fontsize=11, 
                color='#6c757d', family='sans-serif')
        
        # Progress bar
        progress_width = 5
        progress_x_start = 4 - progress_width/2
        progress_y = 0.8
        
        # Background bar
        bg_bar = plt.Rectangle((progress_x_start, progress_y - 0.1), progress_width, 0.2,
                              facecolor='#e0e0e0', edgecolor='none')
        ax.add_patch(bg_bar)
        
        # Progress bar
        progress_fill = (week / 40) * progress_width
        fill_bar = plt.Rectangle((progress_x_start, progress_y - 0.1), progress_fill, 0.2,
                                facecolor=trimester_color, edgecolor='none')
        ax.add_patch(fill_bar)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_infographic_style_image(self, week: int) -> str:
        """Generate infographic-style baby size comparison similar to the reference image"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        
        # Create figure with larger size for better quality
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Set clean white background
        ax.set_facecolor('white')
        
        # Title
        ax.text(6, 7.5, "Baby Size During Pregnancy", 
                ha='center', va='center', 
                fontsize=24, fontweight='bold', 
                color='#2c3e50')
        
        # Current week highlight box
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        trimester_color = '#e74c3c' if trimester == 1 else '#f39c12' if trimester == 2 else '#27ae60'
        
        # Create highlighted box for current week
        highlight_box = plt.Rectangle((4, 4.5), 4, 2.5, 
                                     facecolor=trimester_color, 
                                     alpha=0.1, 
                                     edgecolor=trimester_color, 
                                     linewidth=3)
        ax.add_patch(highlight_box)
        
        # Current week info
        ax.text(6, 6.2, f"Week {week}", 
                ha='center', va='center', 
                fontsize=20, fontweight='bold', 
                color=trimester_color)
        
        ax.text(6, 5.8, f"Size: {data['size']}", 
                ha='center', va='center', 
                fontsize=16, 
                color='#2c3e50')
        
        ax.text(6, 5.4, f"Trimester {trimester}", 
                ha='center', va='center', 
                fontsize=14, 
                color=trimester_color)
        
        # Try to get real fruit image for the comparison
        fruit_image_data = self._fetch_fruit_image(data['size'])
        
        if fruit_image_data:
            try:
                # Load and display the real fruit image
                img_data = base64.b64decode(fruit_image_data.split(',')[1])
                fruit_img = Image.open(BytesIO(img_data))
                
                # Resize fruit image
                fruit_img = fruit_img.resize((120, 120), Image.Resampling.LANCZOS)
                
                # Add fruit image to the center
                ax.imshow(fruit_img, extent=[5.4, 6.6, 4.7, 5.3], aspect='auto', alpha=0.9)
                
            except Exception as e:
                print(f"Error displaying real fruit image in infographic: {e}")
                # Fallback to emoji or text
                ax.text(6, 5, data['size'], 
                        ha='center', va='center', 
                        fontsize=48, 
                        color='#e74c3c')
        else:
            # Fallback to emoji representation
            ax.text(6, 5, data['size'], 
                    ha='center', va='center', 
                    fontsize=48, 
                    color='#e74c3c')
        
        # Add comparison text
        ax.text(6, 4.3, f"~{data['diameter']}cm", 
                ha='center', va='center', 
                fontsize=12, 
                color='#7f8c8d')
        
        # Add trimester indicator at bottom
        trimester_text = f"Trimester {trimester}: Weeks {'1-13' if trimester == 1 else '14-26' if trimester == 2 else '27-40'}"
        ax.text(6, 0.5, trimester_text, 
                ha='center', va='center', 
                fontsize=12, 
                color='#7f8c8d',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))
        
        # Add some decorative elements
        # Small fetus icons in corners
        ax.text(1, 7.5, "👶", ha='center', va='center', fontsize=20)
        ax.text(11, 7.5, "👶", ha='center', va='center', fontsize=20)
        
        # Add week progression indicator
        progress_y = 1.5
        for w in range(1, 41, 5):  # Show every 5th week
            if w <= week:
                color = trimester_color
                alpha = 1.0
            else:
                color = '#bdc3c7'
                alpha = 0.3
            
            circle = plt.Circle((w/4, progress_y), 0.15, 
                              facecolor=color, alpha=alpha, 
                              edgecolor=color, linewidth=1)
            ax.add_patch(circle)
            
            if w % 10 == 0:  # Label every 10th week
                ax.text(w/4, progress_y - 0.4, str(w), 
                        ha='center', va='center', 
                        fontsize=8, color=color)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_exact_reference_style_image(self, week: int) -> str:
        """Generate exact replica of reference image style - grid layout with circular icons and pink ribbons"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        
        # Create figure with proper size for grid layout
        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 16)
        ax.axis('off')
        
        # Set clean white background
        ax.set_facecolor('white')
        
        # Title - "How big is your baby?"
        ax.text(10, 15, "How big is your baby?", 
                ha='center', va='center', 
                fontsize=32, fontweight='bold', 
                color='#4a2c5a', family='sans-serif')
        
        # Color scheme from reference
        circle_bg_color = '#e8f4fd'  # Light blue background for circles
        ribbon_color = '#e91e63'     # Pink/magenta for ribbons
        text_color = '#4a2c5a'       # Dark purple for text
        
        # Grid layout: 4 rows, 5 columns (20 weeks total)
        # Show weeks 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40
        weeks_to_show = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
        
        # Grid positions (4 rows x 5 columns)
        grid_positions = []
        for row in range(4):
            for col in range(5):
                x_pos = 2 + col * 3.5
                y_pos = 11 - row * 2.5
                grid_positions.append((x_pos, y_pos))
        
        # Draw each week item
        for i, (week_num, (x_pos, y_pos)) in enumerate(zip(weeks_to_show, grid_positions)):
            if i >= len(weeks_to_show):
                break
                
            # Circle background
            circle = plt.Circle((x_pos, y_pos), 0.8, 
                              facecolor=circle_bg_color, 
                              edgecolor=ribbon_color, 
                              linewidth=3, alpha=1.0)
            ax.add_patch(circle)
            
            # Fruit/vegetable emoji or representation in center of circle
            fruit_emoji = self._get_fruit_emoji_for_week(week_num)
            ax.text(x_pos, y_pos, fruit_emoji, 
                    ha='center', va='center', 
                    fontsize=24, 
                    color=text_color)
            
            # Pink ribbon banner below circle
            ribbon_width = 1.4
            ribbon_height = 0.4
            ribbon = plt.Rectangle((x_pos - ribbon_width/2, y_pos - 1.2), 
                                 ribbon_width, ribbon_height,
                                 facecolor=ribbon_color, 
                                 edgecolor=ribbon_color, 
                                 alpha=1.0, linewidth=0)
            ax.add_patch(ribbon)
            
            # Week text on ribbon (white text)
            ax.text(x_pos, y_pos - 1.0, f"{week_num} week", 
                    ha='center', va='center', 
                    fontsize=12, fontweight='bold',
                    color='white', family='sans-serif')
            
            # Length/Weight text below ribbon
            length_weight = self._get_length_weight_for_week(week_num)
            ax.text(x_pos, y_pos - 1.6, length_weight, 
                    ha='center', va='center', 
                    fontsize=10, 
                    color=text_color, family='sans-serif')
            
            # Highlight current week
            if week_num == week:
                # Add a special border around current week
                highlight_circle = plt.Circle((x_pos, y_pos), 0.9, 
                                            facecolor='none', 
                                            edgecolor='#ff6b35', 
                                            linewidth=4, alpha=1.0)
                ax.add_patch(highlight_circle)
                
                # Add "CURRENT WEEK" text above
                ax.text(x_pos, y_pos + 1.3, "CURRENT WEEK", 
                        ha='center', va='center', 
                        fontsize=8, fontweight='bold',
                        color='#ff6b35', family='sans-serif')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def _get_fruit_emoji_for_week(self, week: int) -> str:
        """Get appropriate fruit/vegetable emoji for specific week"""
        fruit_map = {
            4: "🌱",    # Seeds
            6: "🫐",    # Blueberries  
            8: "🫛",    # Peas
            10: "🍇",   # Grapes
            12: "🍋",   # Limes
            14: "🍎",   # Apple
            16: "🥑",   # Avocado
            18: "🫑",   # Bell pepper
            20: "🍌",   # Banana
            22: "🥒",   # Cucumber
            24: "🌽",   # Corn
            26: "🥒",   # Zucchini (using cucumber)
            28: "🥦",   # Broccoli
            30: "🥬",   # Cabbage
            32: "🍍",   # Pineapple
            34: "🍈",   # Cantaloupe
            36: "🧅",   # Spring onion
            38: "🍉",   # Watermelon
            40: "🎃",   # Pumpkin
        }
        return fruit_map.get(week, "🍎")
    
    def _get_length_weight_for_week(self, week: int) -> str:
        """Get length/weight information for specific week"""
        length_weight_map = {
            4: "2mm/2mg",
            6: "6.5mm/40mg", 
            8: "15mm/1g",
            10: "30mm/10g",
            12: "50mm/20g",
            14: "80mm/25g",
            16: "110mm/120g",
            18: "140mm/210g", 
            20: "165mm/300g",
            22: "280mm/500g",
            24: "305mm/620g",
            26: "355mm/800g",
            28: "380mm/980g",
            30: "400mm/1450g",
            32: "425mm/1860g",
            34: "450mm/2350g",
            36: "460mm/2600g",
            38: "500mm/3200g",
            40: "590mm/3800g"
        }
        return length_weight_map.get(week, "N/A")
    
    def generate_single_fruit_style_image(self, week: int) -> str:
        """Generate single fruit image style - clean, prominent fruit display like reference image"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        
        # Create figure with clean layout
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Set clean white background
        ax.set_facecolor('white')
        
        # Title - "How big is your baby?"
        ax.text(5, 11, "How big is your baby?", 
                ha='center', va='center', 
                fontsize=28, fontweight='bold', 
                color='#4a2c5a', family='sans-serif')
        
        # Get the appropriate fruit for this week
        fruit_emoji = self._get_fruit_emoji_for_week(week)
        length_weight = self._get_length_weight_for_week(week)
        
        # Large fruit display area
        fruit_display_center_x = 5
        fruit_display_center_y = 7
        
        # Create a subtle background circle for the fruit
        background_circle = plt.Circle((fruit_display_center_x, fruit_display_center_y), 2.5, 
                                     facecolor='#f8f9fa', 
                                     edgecolor='#e9ecef', 
                                     linewidth=2, alpha=0.8)
        ax.add_patch(background_circle)
        
        # Display the fruit emoji prominently
        ax.text(fruit_display_center_x, fruit_display_center_y, fruit_emoji, 
                ha='center', va='center', 
                fontsize=120, 
                color='#2c3e50')
        
        # Week information with pink ribbon style
        ribbon_y = 4.5
        ribbon_width = 4
        ribbon_height = 0.8
        
        # Pink ribbon background
        ribbon = plt.Rectangle((fruit_display_center_x - ribbon_width/2, ribbon_y - ribbon_height/2), 
                             ribbon_width, ribbon_height,
                             facecolor='#e91e63', 
                             edgecolor='#e91e63', 
                             alpha=1.0, linewidth=0)
        ax.add_patch(ribbon)
        
        # Week text on ribbon (white text)
        ax.text(fruit_display_center_x, ribbon_y, f"Week {week}", 
                ha='center', va='center', 
                fontsize=18, fontweight='bold',
                color='white', family='sans-serif')
        
        # Size comparison text
        ax.text(fruit_display_center_x, 3.5, f"Size: {data['size']}", 
                ha='center', va='center', 
                fontsize=16, fontweight='bold',
                color='#4a2c5a', family='sans-serif')
        
        # Length/Weight information
        ax.text(fruit_display_center_x, 3.0, length_weight, 
                ha='center', va='center', 
                fontsize=14, 
                color='#6c757d', family='sans-serif')
        
        # Trimester information
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        trimester_color = '#e74c3c' if trimester == 1 else '#f39c12' if trimester == 2 else '#27ae60'
        
        trimester_text = f"Trimester {trimester}"
        ax.text(fruit_display_center_x, 2.3, trimester_text, 
                ha='center', va='center', 
                fontsize=14, fontweight='bold',
                color=trimester_color, family='sans-serif',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor=trimester_color))
        
        # Add some decorative elements
        # Small fruit icons in corners
        ax.text(1, 10.5, "👶", ha='center', va='center', fontsize=16)
        ax.text(9, 10.5, "👶", ha='center', va='center', fontsize=16)
        
        # Progress indicator
        progress_y = 1.2
        for w in range(1, 41, 5):  # Show every 5th week
            if w <= week:
                color = trimester_color
                alpha = 1.0
            else:
                color = '#bdc3c7'
                alpha = 0.3
            
            circle = plt.Circle((w/4 + 1, progress_y), 0.08, 
                              facecolor=color, alpha=alpha, 
                              edgecolor=color, linewidth=1)
            ax.add_patch(circle)
        
        # Add "Current Week" indicator
        ax.text(fruit_display_center_x, 1.6, "Current Week", 
                ha='center', va='center', 
                fontsize=10, fontweight='bold',
                color=trimester_color, family='sans-serif')
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_clean_banana_image(self, week: int) -> str:
        """Generate clean single banana image - just the banana in center like reference image"""
        if week not in self.week_data:
            return self.generate_simple_baby_image(week)
        
        data = self.week_data[week]
        
        # Create figure with clean layout
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Set clean white background
        ax.set_facecolor('white')
        
        # Title - "How big is your baby?"
        ax.text(4, 9, "How big is your baby?", 
                ha='center', va='center', 
                fontsize=24, fontweight='bold', 
                color='#4a2c5a', family='sans-serif')
        
        # Get the appropriate fruit for this week
        fruit_emoji = self._get_fruit_emoji_for_week(week)
        length_weight = self._get_length_weight_for_week(week)
        
        # Large fruit display area - centered
        fruit_display_center_x = 4
        fruit_display_center_y = 6
        
        # Create a light gray circle background (matching reference)
        background_circle = plt.Circle((fruit_display_center_x, fruit_display_center_y), 1.8, 
                                     facecolor='#f5f5f5', 
                                     edgecolor='#d0d0d0', 
                                     linewidth=1, alpha=1.0)
        ax.add_patch(background_circle)
        
        # Display the fruit emoji prominently (large size)
        ax.text(fruit_display_center_x, fruit_display_center_y, fruit_emoji, 
                ha='center', va='center', 
                fontsize=80, 
                color='#2c3e50')
        
        # Pink ribbon banner below circle (matching reference)
        ribbon_y = 4.2
        ribbon_width = 2.5
        ribbon_height = 0.6
        
        # Pink ribbon background
        ribbon = plt.Rectangle((fruit_display_center_x - ribbon_width/2, ribbon_y - ribbon_height/2), 
                             ribbon_width, ribbon_height,
                             facecolor='#e91e63', 
                             edgecolor='#e91e63', 
                             alpha=1.0, linewidth=0)
        ax.add_patch(ribbon)
        
        # Week text on ribbon (white text)
        ax.text(fruit_display_center_x, ribbon_y, f"Week {week}", 
                ha='center', va='center', 
                fontsize=16, fontweight='bold',
                color='white', family='sans-serif')
        
        # Size comparison text
        ax.text(fruit_display_center_x, 3.3, f"Size: {data['size']}", 
                ha='center', va='center', 
                fontsize=14, fontweight='bold',
                color='#4a2c5a', family='sans-serif')
        
        # Length/Weight information
        ax.text(fruit_display_center_x, 2.8, length_weight, 
                ha='center', va='center', 
                fontsize=12, 
                color='#6c757d', family='sans-serif')
        
        # Trimester information (small rounded button)
        trimester = 1 if week <= 13 else 2 if week <= 26 else 3
        trimester_color = '#e74c3c' if trimester == 1 else '#f39c12' if trimester == 2 else '#27ae60'
        
        trimester_text = f"Trimester {trimester}"
        ax.text(fruit_display_center_x, 2.0, trimester_text, 
                ha='center', va='center', 
                fontsize=12, fontweight='bold',
                color=trimester_color, family='sans-serif',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#fffacd', alpha=0.9, edgecolor=trimester_color, linewidth=2))
        
        # "Current Week" text
        ax.text(fruit_display_center_x, 1.5, "Current Week", 
                ha='center', va='center', 
                fontsize=10, 
                color='#6c757d', family='sans-serif')
        
        # Progress dots at bottom
        progress_y = 0.8
        for i, w in enumerate(range(1, 41, 5)):  # Show every 5th week
            x_pos = 1.5 + i * 0.3
            if w <= week:
                color = trimester_color
                alpha = 1.0
            else:
                color = '#d0d0d0'
                alpha = 0.5
            
            circle = plt.Circle((x_pos, progress_y), 0.06, 
                              facecolor=color, alpha=alpha, 
                              edgecolor=color, linewidth=1)
            ax.add_patch(circle)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode as base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    def _draw_baby_representation(self, ax, data, diameter, x, y):
        """Draw baby representation with more realistic styling"""
        # Baby body (slightly more realistic)
        baby_body = Ellipse((x, y), diameter*0.8, diameter*1.2, 
                           facecolor=self.colors['baby'], 
                           edgecolor='#ff9999', linewidth=2, alpha=0.9)
        ax.add_patch(baby_body)
        
        # Baby head
        head_radius = diameter * 0.3
        head = Circle((x, y + diameter*0.3), head_radius, 
                     facecolor=self.colors['baby'], 
                     edgecolor='#ff9999', linewidth=2, alpha=0.9)
        ax.add_patch(head)
        
        # Simple face features
        # Eyes
        ax.plot(x - head_radius*0.3, y + diameter*0.4, 'ko', markersize=3)
        ax.plot(x + head_radius*0.3, y + diameter*0.4, 'ko', markersize=3)
        
        # Smile
        smile = patches.Arc((x, y + diameter*0.25), head_radius*0.8, head_radius*0.4, 
                           angle=0, theta1=0, theta2=180, color='black', linewidth=2)
        ax.add_patch(smile)
    
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
    
    async def get_or_generate_openai_image(self, week: int, regenerate: bool = False) -> str:
        """
        Get cached image or generate new one using OpenAI DALL-E
        Falls back to real fruit photos if OpenAI unavailable
        
        Args:
            week: Pregnancy week (1-40)
            regenerate: Force regeneration even if cached
            
        Returns:
            Base64 encoded image data
        """
        if week not in self.week_data:
            return self.generate_real_fruit_only_image(week)
        
        cache_path = f"image_cache/week_{week}.png"
        
        # Return cached image if exists and not regenerating
        if os.path.exists(cache_path) and not regenerate:
            try:
                with open(cache_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"Error reading cached image for week {week}: {e}")
        
        # Generate new image using OpenAI
        if not self.openai_service:
            print("OpenAI service not available, using real fruit image fallback")
            return self.generate_real_fruit_only_image(week)
        
        try:
            data = self.week_data[week]
            fruit_name = data['size']
            
            # Get size in cm for the prompt
            size_cm = self._get_size_in_cm(week)
            
            # Generate image via OpenAI
            image_base64 = await self.openai_service.generate_baby_fruit_image(
                week, fruit_name, size_cm
            )
            
            if image_base64:
                # Cache the image
                try:
                    os.makedirs("image_cache", exist_ok=True)
                    with open(cache_path, 'wb') as f:
                        f.write(base64.b64decode(image_base64))
                    print(f"✅ Cached OpenAI image for week {week}")
                except Exception as e:
                    print(f"Error caching image for week {week}: {e}")
                
                return image_base64
            else:
                print(f"OpenAI image generation failed for week {week}, using real fruit image fallback")
                return self.generate_real_fruit_only_image(week)
                
        except Exception as e:
            print(f"Error in OpenAI image generation for week {week}: {e}")
            print(f"Using real fruit image fallback for week {week}")
            return self.generate_real_fruit_only_image(week)
    
    def _get_size_in_cm(self, week: int) -> float:
        """Get approximate size in centimeters for the week"""
        # Approximate size progression from 0.1cm to 50cm over 40 weeks
        if week <= 4:
            return 0.1
        elif week <= 8:
            return 0.1 + (week - 4) * 0.05
        elif week <= 12:
            return 0.3 + (week - 8) * 0.1
        elif week <= 16:
            return 0.7 + (week - 12) * 0.15
        elif week <= 20:
            return 1.3 + (week - 16) * 0.2
        elif week <= 24:
            return 2.1 + (week - 20) * 0.25
        elif week <= 28:
            return 3.1 + (week - 24) * 0.3
        elif week <= 32:
            return 4.3 + (week - 28) * 0.35
        elif week <= 36:
            return 5.7 + (week - 32) * 0.4
        else:
            return 7.3 + (week - 36) * 0.45
