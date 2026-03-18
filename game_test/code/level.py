# -*- coding: utf-8 -*-
import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from astar import AStarPathfinder
from item import Item
from inventory import Inventory

class Level:
	def __init__(self):

		self.display_surface = pygame.display.get_surface()
		self.game_paused = False

		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()

		self.current_attack = None
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# Add depth system
		self.floor_depth = 1
		self.player_spawn_pos = None
		self.enemy_count = 0
  
		# Add raccoon tracking
		self.raccoon_count = 0
		self.initial_raccoon_count = 0
  
		# Add pathfinder
		self.pathfinder = None
		self.boundary_layout = None  # Save the boundary layout

		self.create_map()
  
		# Initialize the search network grid
		self.initialize_pathfinding()

		self.ui = UI()
		self.upgrade = Upgrade(self.player)

		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)
  
		# Add backpack system
		self.inventory = Inventory(self.player)
  
	def initialize_pathfinding(self):
		"""Initialize the pathfinding system"""
		if self.boundary_layout:
			self.pathfinder = AStarPathfinder(self.boundary_layout, self.obstacle_sprites)
			self.pathfinder.setup_grid()

	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('../map/map_Grass.csv'),
			'object': import_csv_layout('../map/map_Objects.csv'),
			'entities': import_csv_layout('../map/map_Entities.csv')
		}
		graphics = {
			'grass': import_folder('../graphics/Grass'),
			'objects': import_folder('../graphics/objects')
		}
		
		self.boundary_layout = layouts['boundary']
		self.enemy_count = 0
		self.raccoon_count = 0
		self.initial_raccoon_count = 0
		
		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'grass':
							random_grass_image = choice(graphics['grass'])
							Tile(
								(x,y),
								[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],
								'grass',
								random_grass_image)
						
						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)
						
						if style == 'entities':
							if col == '394':
								self.player_spawn_pos = (x, y)
								if not hasattr(self, 'player'):
									self.player = Player(
										(x,y),
										[self.visible_sprites],
										self.obstacle_sprites,
										self.create_attack,
										self.destroy_attack,
										self.create_magic)
								else:
									self.player.hitbox.topleft = (x,y)
									self.player.rect.center = self.player.hitbox.center
							else:
								if col == '390': monster_name = 'bamboo'
								elif col == '391': monster_name = 'spirit'
								elif col == '392': monster_name ='raccoon'
								else: monster_name = 'squid'
								
								# If it's a raccoon, increase the count
								if monster_name == 'raccoon':
									self.raccoon_count += 1
									self.initial_raccoon_count += 1
								
								Enemy(
									monster_name,
									(x,y),
									[self.visible_sprites,self.attackable_sprites],
									self.obstacle_sprites,
									self.damage_player,
									self.trigger_death_particles,
									self.add_exp,
									self.floor_depth,
									self)
								self.enemy_count += 1

	def create_attack(self):
		
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

		if style == 'flame':
			self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'grass':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

	def trigger_death_particles(self,pos,particle_type):
		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

	def add_exp(self,amount):
		# Snow: Add exp based on depth
		base_exp = amount
		depth_bonus = base_exp * (FLOOR_EXP_BONUS * (self.floor_depth - 1))
		total_exp = base_exp + depth_bonus

		self.player.exp += int(total_exp)

	def toggle_menu(self):
		self.game_paused = not self.game_paused
  
	# depth system method
	def check_enemies_cleared(self):
		# Recalculate the current number of surviving raccoons
		current_raccoons = 0
		for sprite in self.attackable_sprites:
			if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy':
				if hasattr(sprite, 'monster_name') and sprite.monster_name == 'raccoon':
					current_raccoons += 1
		
		# Only when all the initial raccoons have been cleared will you proceed to the next level
		if current_raccoons == 0 and self.initial_raccoon_count > 0:
			self.advance_floor()
			return True
		return False

	def advance_floor(self):
		self.floor_depth += 1
		
		for sprite in list(self.attackable_sprites):
			if hasattr(sprite, 'sprite_type'):
				sprite.kill()
		
		# Reset the raccoon count
		self.raccoon_count = 0
		self.initial_raccoon_count = 0
		
		# Generate new enemies
		self.enemy_count = 0
		self.create_map()
		
		# bonus
		self.player.health = min(self.player.stats['health'],
						self.player.health + 20)
  
	def display_floor_info(self, surface):
		font = pygame.font.Font(UI_FONT, UI_FONT_SIZE + 10)
		text_surf = font.render(f"Depth: {self.floor_depth}", True, (255, 215, 0))  # golden
		text_rect = text_surf.get_rect(topright=(WIDTH - 20, 20))
    
		# Snow: Add background box
		bg_rect = text_rect.inflate(20, 10)
		pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=5)
		pygame.draw.rect(surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3, border_radius=5)
	
		surface.blit(text_surf, text_rect)

	def run(self, events=None):
		if events is None:
			events = []
    
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)
	
		# Snow: Display depth
		self.display_floor_info(self.display_surface)

		# Snow: Handle backpack events
		self.inventory.handle_events(events)
		# Snow: Draw the backpack if open
		self.inventory.draw()
  
		if self.game_paused:
			self.upgrade.display()
		else:
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			self.player_attack_logic()

			# Check for collisions between players and items
			self.check_item_pickup()
   
			# Check whether all the enemies are dead.
			self.check_enemies_cleared()
   
	def get_path_to_player(self, enemy_pos):
		"""Obtain the path from the enemy's position to the player"""
		if self.pathfinder and hasattr(self, 'player'):
			return self.pathfinder.find_path(enemy_pos, self.player.rect.center)
		return []

	def get_direction_to_player(self, enemy_pos):
		"""Obtain the direction from the enemy's position to the player"""
		if self.pathfinder and hasattr(self, 'player'):
			path = self.get_path_to_player(enemy_pos)
			if path and len(path) > 0:
                # Return to the direction of the first path point
				enemy_vec = pygame.math.Vector2(enemy_pos)
				first_waypoint = pygame.math.Vector2(path[0])
				direction = (first_waypoint - enemy_vec)
				if direction.length() > 0:
					return direction.normalize()
		return pygame.math.Vector2(0, 0)

	def trigger_item_drop(self, monster_name, pos):
		"""Generate monster drop items at the designated location"""
		from settings import MONSTER_DROP_TABLES
		import random
    
		drop_table = MONSTER_DROP_TABLES.get(monster_name, {})
		drop_list = drop_table.get('drops', [])
    
		for drop in drop_list:
			if random.random() <= drop['chance']:
				quantity = random.randint(drop['min_quantity'], drop['max_quantity'])
				for _ in range(quantity):
    	            # Add a slight random offset to avoid complete overlap of items
					offset_x = random.randint(-10, 10)
					offset_y = random.randint(-10, 10)
					drop_pos = (pos[0] + offset_x, pos[1] + offset_y)
					Item(drop['item_id'], drop_pos, [self.visible_sprites])
     
	def toggle_inventory(self):
		"""Switch the on/off state of the backpack"""
		self.inventory.toggle()

	def check_item_pickup(self):
		"""Check if the player has collided with an item and picked it up"""
		if not hasattr(self, 'player') or not hasattr(self, 'visible_sprites'):
			return
    
		# Get all item sprites
		items = [sprite for sprite in self.visible_sprites.sprites() 
             if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'item']
    
		for item in items:
        	# Check for collisions between players and items
			if self.player.hitbox.colliderect(item.rect):
				# Try adding it to your backpack
				if self.inventory.add_item(item.item_id):
					# If added successfully, remove the item Sprite
					item.kill()
                
					# Snow: We can add the pickup sound effect here
					# pickup_sound.play()
		

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)