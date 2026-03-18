import pygame
import random
import math
from settings import TILESIZE, ITEMS_DATA

class Item(pygame.sprite.Sprite):
    def __init__(self, item_id, pos, groups):
        super().__init__(groups)
        
        self.sprite_type = 'item'
        self.item_id = item_id
        self.picked_up = False  # Has the mark been picked up
        
        # Obtain information from item data
        item_info = ITEMS_DATA.get(item_id, {})
        self.name = item_info.get('name', 'Unknown Item')
        self.item_type = item_info.get('type', 'material')
        self.rarity = item_info.get('rarity', 'common')
        self.value = item_info.get('value', 0)
        self.description = item_info.get('description', '')
        
        # Load the picture
        image_path = item_info.get('image_path', '')
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            # Adjust the size to half of TILESIZE
            self.image = pygame.transform.scale(self.image, (TILESIZE//2, TILESIZE//2))
        except:
            # If the image fails to load, create a placeholder
            self.image = pygame.Surface((TILESIZE//2, TILESIZE//2))
            color_map = {
                'common': (255, 255, 255),
                'uncommon': (0, 255, 0),
                'rare': (0, 112, 255),
                'epic': (163, 53, 238),
                'legendary': (255, 128, 0),
                'immortal': (255, 0, 0)
            }
            self.image.fill(color_map.get(self.rarity, (255, 255, 255)))
        
        # Set the location
        self.rect = self.image.get_rect(center=pos)
        
        # Life cycle (automatically disappears after 30 seconds)
        self.lifetime = 30000  # 30 sec
        self.creation_time = pygame.time.get_ticks()
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Check if it has expired
        if current_time - self.creation_time > self.lifetime:
            self.kill()
            return