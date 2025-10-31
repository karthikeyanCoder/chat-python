"""
Image Generator for Trimester Module

This service handles image generation for baby size comparisons,
including real fruit images, AI-generated images, and traditional visualizations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Ellipse, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Dict, Tuple, Optional
import os
import requests
from io import BytesIO
import json
import asyncio

from .config import settings


class BabySizeImageGenerator:
    """Service for generating baby size comparison images"""
    
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
            "Poppy seed": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Sesame seed": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Blueberry": "https://images.unsplash.com/photo-1498551172505-8ee7ad69f235?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Raspberry": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Grape": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Lime": "https://images.unsplash.com/photo-1536869/pexels-photo-1536869.jpeg?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Plum": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Peach": "https://images.unsplash.com/photo-1566479179817-c0d9ed07d9e7?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Lemon": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Apple": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Avocado": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Onion": "https://images.unsplash.com/photo-1518977956812-cd3dbadaaf31?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Sweet potato": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Mango": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Banana": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Carrot": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Corn": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Corn cob": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Grapefruit": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Cantaloupe": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Kumquat": "https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Orange": "https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Cabbage": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Cauliflower": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80",
            "Watermelon": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80"
        }
    
    def _initialize_week_data(self) -> Dict:
        """Initialize basic week data for image generation"""
        return {
            1: {"size": "Poppy seed", "weight": "0.1g", "length": "0.1cm"},
            10: {"size": "Kumquat", "weight": "4g", "length": "3.1cm"},
            20: {"size": "Banana", "weight": "300g", "length": "16.4cm"},
            30: {"size": "Cabbage", "weight": "1.3kg", "length": "39.9cm"},
            40: {"size": "Watermelon", "weight": "3.4kg", "length": "51.2cm"}
        }
    
    def _get_fruit_name_for_week(self, week: int) -> str:
        """Get fruit name for a specific week from full pregnancy data"""
        try:
            # Try to get from full pregnancy data
            from app.shared.pregnancy_rag.pregnancy_data_full import get_all_40_weeks_data
            all_weeks = get_all_40_weeks_data()
            
            if week in all_weeks:
                week_data = all_weeks[week]
                # Access baby_size.size
                if hasattr(week_data, 'baby_size'):
                    if hasattr(week_data.baby_size, 'size'):
                        return week_data.baby_size.size
                    elif isinstance(week_data.baby_size, dict):
                        return week_data.baby_size.get('size', 'Unknown')
            
            # Fallback to basic week data
            week_info = self.week_data.get(week)
            if week_info:
                return week_info['size']
            
            # Last resort: use closest week
            closest_week = min([1, 10, 20, 30, 40], key=lambda x: abs(x - week))
            return self.week_data[closest_week]['size']
            
        except Exception as e:
            print(f"Error getting fruit name for week {week}: {e}")
            # Fallback
            week_info = self.week_data.get(week, self.week_data[40])
            return week_info['size']
    
    def generate_baby_size_image(self, week: int) -> str:
        """Generate a traditional matplotlib baby size visualization"""
        try:
            # Get week data
            week_info = self.week_data.get(week, self.week_data[40])
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_facecolor(self.colors['background'])
            
            # Draw baby representation
            baby_size = week_info['size']
            baby_color = self.colors['baby']
            
            # Create appropriate shape based on week
            if week <= 12:
                # Early weeks - small circle
                baby_shape = Circle((0.5, 0.5), 0.1, color=baby_color, alpha=0.8)
            elif week <= 24:
                # Mid pregnancy - ellipse
                baby_shape = Ellipse((0.5, 0.5), 0.3, 0.2, color=baby_color, alpha=0.8)
            else:
                # Late pregnancy - larger ellipse
                baby_shape = Ellipse((0.5, 0.5), 0.4, 0.3, color=baby_color, alpha=0.8)
            
            ax.add_patch(baby_shape)
            
            # Add text
            ax.text(0.5, 0.2, f"Week {week}", ha='center', va='center', 
                   fontsize=16, fontweight='bold', color=self.colors['text'])
            ax.text(0.5, 0.1, f"Size: {baby_size}", ha='center', va='center', 
                   fontsize=12, color=self.colors['text'])
            ax.text(0.5, 0.05, f"Weight: {week_info['weight']}", ha='center', va='center', 
                   fontsize=10, color=self.colors['text'])
            
            # Remove axes
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error generating baby size image: {e}")
            return self._get_fallback_image(week)
    
    def generate_real_fruit_only_image(self, week: int) -> str:
        """Generate real fruit image for baby size comparison"""
        try:
            # Get fruit name from full pregnancy data
            fruit_name = self._get_fruit_name_for_week(week)
            
            # Check cache first
            cache_key = f"{week}_{fruit_name}"
            if cache_key in self.fruit_images_cache:
                return self.fruit_images_cache[cache_key]
            
            # Get fruit image URL
            fruit_url = self.fruit_image_urls.get(fruit_name)
            if not fruit_url:
                # Fallback to generic fruit image
                fruit_url = "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&h=600&fit=crop&crop=focalpoint&fp-x=0.5&fp-y=0.5&q=80"
            
            # Download and process image
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(fruit_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Convert to base64
            image_base64 = base64.b64encode(response.content).decode()
            image_data = f"data:image/jpeg;base64,{image_base64}"
            
            # Cache the result
            self.fruit_images_cache[cache_key] = image_data
            
            return image_data
            
        except Exception as e:
            print(f"Error generating real fruit image: {e}")
            return self._get_fallback_image(week)
    
    async def get_or_generate_openai_image(self, week: int, regenerate: bool = False) -> str:
        """Get or generate OpenAI image for baby size comparison"""
        try:
            if not self.openai_service:
                raise ValueError("OpenAI service not available")
            
            # Check cache first (unless regenerating)
            cache_key = f"openai_{week}"
            if not regenerate and cache_key in self.fruit_images_cache:
                return self.fruit_images_cache[cache_key]
            
            # Get fruit name from pregnancy data service (full 40 weeks)
            fruit_name = self._get_fruit_name_for_week(week)
            
            # Generate image using OpenAI
            image_data = await self._generate_openai_image(week, fruit_name)
            
            # Cache the result
            self.fruit_images_cache[cache_key] = image_data
            
            return image_data
            
        except Exception as e:
            print(f"Error getting OpenAI image: {e}")
            return self._get_fallback_image(week)
    
    async def _generate_openai_image(self, week: int, fruit_name: str) -> str:
        """Generate image using OpenAI DALL-E"""
        try:
            # Create prompt for single fruit image
            prompt = f"A single {fruit_name.lower()} on a clean white background, professional photography style, high quality, isolated object, perfect for baby size comparison during pregnancy week {week}"
            
            # Generate image using OpenAI
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_response.content).decode()
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error generating OpenAI image: {e}")
            raise
    
    def _get_fallback_image(self, week: int) -> str:
        """Get fallback image when other methods fail"""
        try:
            # Create a simple fallback image
            fig, ax = plt.subplots(1, 1, figsize=(6, 4))
            fig.patch.set_facecolor('#f0f0f0')
            ax.set_facecolor('#f0f0f0')
            
            # Add simple text
            ax.text(0.5, 0.5, f"Week {week}\nBaby Size Info", 
                   ha='center', va='center', fontsize=14, 
                   color='#666666', fontweight='bold')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error creating fallback image: {e}")
            # Return a simple base64 placeholder
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    def get_image_info(self, week: int) -> Dict[str, str]:
        """Get information about available images for a week"""
        week_info = self.week_data.get(week, self.week_data[40])
        return {
            "week": str(week),
            "fruit_name": week_info['size'],
            "weight": week_info['weight'],
            "length": week_info['length'],
            "available_images": {
                "traditional": "matplotlib",
                "real_fruit": "unsplash",
                "openai": "dall-e-3" if self.openai_service else "unavailable"
            }
        }
    
    def clear_cache(self):
        """Clear the image cache"""
        self.fruit_images_cache.clear()
        print("Image cache cleared")
