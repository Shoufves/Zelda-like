# -*- coding: utf-8 -*-
import pygame
from settings import *

class Inventory:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.small_font = pygame.font.Font(UI_FONT, UI_FONT_SIZE - 4)
        
        # Backpack Settings
        self.slots_count = 20  # Total of 20 slots
        self.slots_per_row = 5  # 5 cells per row
        self.slot_size = 64
        self.slot_margin = 10
        self.slot_padding = 5
        
        # Backpack status
        self.items = [None] * self.slots_count
        self.is_open = False
        
        # Calculate UI position
        self.inventory_width = (self.slots_per_row * (self.slot_size + self.slot_margin)) - self.slot_margin
        self.inventory_height = 4 * (self.slot_size + self.slot_margin)  # 4 rows
        
        # Backpack position (center of screen)
        screen_width, screen_height = self.display_surface.get_size()
        self.inventory_x = (screen_width - self.inventory_width) // 2
        self.inventory_y = (screen_height - self.inventory_height) // 2
        
        # Mouse interaction
        self.hovered_slot = None
        self.last_mouse_pos = (0, 0)
        
        # Item information display
        self.info_font = pygame.font.Font(UI_FONT, 14)
        
    def add_item(self, item_id):
        """Add item to first empty slot"""
        for i in range(self.slots_count):
            if self.items[i] is None:
                self.items[i] = item_id
                return True
        return False
    
    def remove_item(self, slot_index):
        """Remove item from specified slot"""
        if 0 <= slot_index < self.slots_count and self.items[slot_index] is not None:
            item_id = self.items[slot_index]
            self.items[slot_index] = None
            return item_id
        return None
    
    def get_slot_at_pos(self, pos):
        """Get slot index at mouse position"""
        x, y = pos
        
        if not self.is_open or not self.is_point_in_inventory(pos):
            return None
        
        rel_x = x - self.inventory_x
        rel_y = y - self.inventory_y
        
        col = rel_x // (self.slot_size + self.slot_margin)
        row = rel_y // (self.slot_size + self.slot_margin)
        
        if 0 <= col < self.slots_per_row and 0 <= row < (self.slots_count // self.slots_per_row):
            slot_index = row * self.slots_per_row + col
            if slot_index < self.slots_count:
                slot_x = col * (self.slot_size + self.slot_margin)
                slot_y = row * (self.slot_size + self.slot_margin)
                
                if (slot_x <= rel_x <= slot_x + self.slot_size and 
                    slot_y <= rel_y <= slot_y + self.slot_size):
                    return slot_index
        
        return None
    
    def is_point_in_inventory(self, pos):
        """Check if point is in inventory UI area"""
        x, y = pos
        return (self.inventory_x <= x <= self.inventory_x + self.inventory_width and
                self.inventory_y <= y <= self.inventory_y + self.inventory_height)
    
    def toggle(self):
        """Toggle inventory open/close state"""
        self.is_open = not self.is_open
    
    def handle_events(self, events):
        """Handle inventory-related events"""
        if not self.is_open:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_slot = self.get_slot_at_pos(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(mouse_pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(mouse_pos)
    
    def handle_left_click(self, mouse_pos):
        """Handle left click (use consumables)"""
        slot_index = self.get_slot_at_pos(mouse_pos)
        if slot_index is not None and self.items[slot_index] is not None:
            item_id = self.items[slot_index]
            from settings import ITEMS_DATA
            item_data = ITEMS_DATA.get(item_id, {})
            
            if item_data.get('type') == 'consumable':
                print(f"Use consumable: {item_data.get('name')}")
                self.use_consumable(item_id, slot_index)
    
    def handle_right_click(self, mouse_pos):
        """Handle right click (discard items)"""
        slot_index = self.get_slot_at_pos(mouse_pos)
        if slot_index is not None and self.items[slot_index] is not None:
            item_id = self.items[slot_index]
            from settings import ITEMS_DATA
            item_data = ITEMS_DATA.get(item_id, {})
            
            self.remove_item(slot_index)
    
    def use_consumable(self, item_id, slot_index):
        """Use consumables to achieve specific effects"""
        from settings import ITEMS_DATA
    
        item_data = ITEMS_DATA.get(item_id, {})
        item_name = item_data.get('name', 'Unknown item')
    
        # Perform different effects based on the item ID
        if item_id == 'consumable_1':  # Raccoon Healing Herb
            self.apply_healing_herb()
        elif item_id == 'consumable_2':  # Raccoon Energy Root
            self.apply_energy_root()
        elif item_id == 'special_1':  # Raccoon Lucky Charm
            self.apply_lucky_charm()
        elif item_id == 'special_2':  # Ancient Raccoon Talisman
            self.apply_ancient_talisman()
        else:
            return
    
        # Remove the items after use
        self.remove_item(slot_index)
        
    def apply_healing_herb(self):
        """Raccoon Healing Herb: Restore health to the maximum"""
        if hasattr(self.player, 'health') and hasattr(self.player, 'stats'):
            self.player.health = self.player.stats['health']
        
    def apply_energy_root(self):
        """Raccoon Energy Root: Restore the energy value to the maximum"""
        if hasattr(self.player, 'energy') and hasattr(self.player, 'stats'):
            self.player.energy = self.player.stats['energy']

    def apply_lucky_charm(self):
        """Raccoon Lucky Charm: Permanently enhance attributes by 20%"""
        if hasattr(self.player, 'stats') and hasattr(self.player, 'max_stats'):
            # Enhance attack power
            if 'attack' in self.player.stats and 'attack' in self.player.max_stats:
                new_attack = min(self.player.stats['attack'] * 1.2, self.player.max_stats['attack'])
                self.player.stats['attack'] = new_attack
                print(f"The attack power is permanently increased by 20%: {new_attack}")
            
            # Boost energy
            if 'energy' in self.player.stats and 'energy' in self.player.max_stats:
                new_energy = min(self.player.stats['energy'] * 1.2, self.player.max_stats['energy'])
                self.player.stats['energy'] = new_energy
                # Restore the current energy value simultaneously
                self.player.energy = new_energy
            
            # Increase health points
            if 'health' in self.player.stats and 'health' in self.player.max_stats:
                new_health = min(self.player.stats['health'] * 1.2, self.player.max_stats['health'])
                self.player.stats['health'] = new_health
                # Restore the current health points simultaneously
                self.player.health = new_health

    def apply_ancient_talisman(self):
        """Ancient Raccoon Talisman: Gain the number of revivals"""
        if not hasattr(self.player, 'revive_count'):
            self.player.revive_count = 0
        
        self.player.revive_count += 1
    
    def draw(self):
        """Draw inventory UI"""
        if not self.is_open:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.display_surface.blit(overlay, (0, 0))
        
        # Inventory background
        bg_rect = pygame.Rect(
            self.inventory_x - 20,
            self.inventory_y - 20,
            self.inventory_width + 40,
            self.inventory_height + 40
        )
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 4, border_radius=10)
        
        # Title
        title = self.font.render("Backpack", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(self.inventory_x + self.inventory_width // 2, 
                                            self.inventory_y - 40))
        self.display_surface.blit(title, title_rect)
        
        # Draw all slots
        for i in range(self.slots_count):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = self.inventory_x + col * (self.slot_size + self.slot_margin)
            slot_y = self.inventory_y + row * (self.slot_size + self.slot_margin)
            
            # Slot background
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            slot_color = UI_BORDER_COLOR_ACTIVE if i == self.hovered_slot else UI_BORDER_COLOR
            pygame.draw.rect(self.display_surface, UI_BG_COLOR, slot_rect)
            pygame.draw.rect(self.display_surface, slot_color, slot_rect, 2)
            
            # Slot number (for debugging)
            slot_text = self.small_font.render(str(i), True, TEXT_COLOR)
            self.display_surface.blit(slot_text, (slot_x + 5, slot_y + 5))
            
            # Draw item
            if self.items[i] is not None:
                self.draw_item_in_slot(i, slot_x, slot_y)
        
        # Draw hovered item info
        if self.hovered_slot is not None and self.items[self.hovered_slot] is not None:
            self.draw_item_info(self.hovered_slot)
    
    def draw_item_in_slot(self, slot_index, x, y):
        """Draw item in slot"""
        item_id = self.items[slot_index]
        from settings import ITEMS_DATA, RARITY_COLORS
        
        item_data = ITEMS_DATA.get(item_id, {})
        rarity = item_data.get('rarity', 'common')
        
        # Try loading item image
        image_path = item_data.get('image_path', '')
        try:
            item_image = pygame.image.load(image_path).convert_alpha()
            item_image = pygame.transform.scale(item_image, (self.slot_size - 10, self.slot_size - 10))
            self.display_surface.blit(item_image, (x + 5, y + 5))
        except:
            # Fallback colored square
            color_hex = RARITY_COLORS.get(rarity, '#FFFFFF')
            color_hex = color_hex.lstrip('#')
            color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            
            item_surf = pygame.Surface((self.slot_size - 10, self.slot_size - 10))
            item_surf.fill(color)
            self.display_surface.blit(item_surf, (x + 5, y + 5))
    
    def draw_item_info(self, slot_index):
        """Draw detailed item info"""
        item_id = self.items[slot_index]
        from settings import ITEMS_DATA, RARITY_COLORS
        
        item_data = ITEMS_DATA.get(item_id, {})
        if not item_data:
            return
        
        name = item_data.get('name', 'Unknown item')
        item_type = item_data.get('type', 'material')
        rarity = item_data.get('rarity', 'common')
        description = item_data.get('description', '')
        
        # Get rarity color
        rarity_color_hex = RARITY_COLORS.get(rarity, '#FFFFFF')
        rarity_color_hex = rarity_color_hex.lstrip('#')
        rarity_color = tuple(int(rarity_color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Type text mapping
        type_map = {
            'material': 'Material',
            'consumable': 'Consumable',
            'special': 'Special'
        }
        type_text = type_map.get(item_type, item_type)
        
        # Rarity text mapping
        rarity_map = {
            'common': 'Common',
            'uncommon': 'Uncommon',
            'rare': 'Rare',
            'epic': 'Epic',
            'legendary': 'Legendary',
            'immortal': 'Immortal'
        }
        rarity_text = rarity_map.get(rarity, rarity)
        
        # Create info text
        lines = [
            f"Name: {name}",
            f"Type: {type_text}",
            f"Rarity: {rarity_text}",
            f"Desc: {description}"
        ]
        
        # Calculate info box size
        max_width = 0
        line_heights = []
        for line in lines:
            line_surf = self.info_font.render(line, True, TEXT_COLOR)
            max_width = max(max_width, line_surf.get_width())
            line_heights.append(line_surf.get_height())
        
        total_height = sum(line_heights) + 20
        info_width = max_width + 20
        
        # Position (top right corner)
        screen_width = self.display_surface.get_size()[0]
        info_x = screen_width - info_width - 20
        info_y = 20
        
        # Draw info box background
        info_rect = pygame.Rect(info_x, info_y, info_width, total_height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, info_rect, border_radius=5)
        pygame.draw.rect(self.display_surface, rarity_color, info_rect, 2, border_radius=5)
        
        # Draw text
        current_y = info_y + 10
        for i, line in enumerate(lines):
            line_color = rarity_color if i == 2 else TEXT_COLOR
            line_surf = self.info_font.render(line, True, line_color)
            self.display_surface.blit(line_surf, (info_x + 10, current_y))
            current_y += line_heights[i]