import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
	def __init__(self,monster_name,pos,groups,obstacle_sprites,damage_player,trigger_death_particles,add_exp,floor_depth=1,level_ref=None):

		# 总体配置
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# 图像配置
		self.import_graphics(monster_name)
		self.status = 'idle'
		self.image = self.animations[self.status][self.frame_index]

		# 移动
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-10)
		self.obstacle_sprites = obstacle_sprites

		# 属�?
		self.monster_name = monster_name
		monster_info = monster_data[self.monster_name]
  
		# Depth coefficient
		depth_multiplier = 1.0 + (FLOOR_ENEMY_MULTIPLIER * (floor_depth - 1))
  
		self.health = monster_info['health'] * depth_multiplier
		self.exp = monster_info['exp'] * (1.0 + (FLOOR_EXP_BONUS * (floor_depth - 1)))
		self.speed = monster_info['speed'] * (1.0 + 0.05 * (floor_depth - 1))
		self.attack_damage = monster_info['damage'] * depth_multiplier
		self.resistance = monster_info['resistance']
		self.attack_radius = monster_info['attack_radius']
		self.notice_radius = monster_info['notice_radius']
		self.attack_type = monster_info['attack_type']

		# 玩�?�互�?
		self.can_attack = True
		self.attack_time = None
		self.attack_cooldown = 400
		self.damage_player = damage_player
		self.trigger_death_particles = trigger_death_particles
		self.add_exp = add_exp
  
		# Pathfinding system
		self.path = []
		self.current_path_index = 0
		self.path_update_cooldown = 0
		self.path_update_interval = 500
		self.last_player_pos = None
		self.path_direction = pygame.math.Vector2()
  
		# Sight detection cache
		self.line_of_sight_cooldown = 0
		self.line_of_sight_cache = True
		self.line_of_sight_interval = 200

		# 无敌时间
		self.vulnerable = True
		self.hit_time = None
		self.invincibility_duration = 300

		# 声音
		self.death_sound = pygame.mixer.Sound('../audio/death.wav')
		self.hit_sound = pygame.mixer.Sound('../audio/hit.wav')
		self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
		self.death_sound.set_volume(0.6)
		self.hit_sound.set_volume(0.6)
		self.attack_sound.set_volume(0.6)

		# Add a Level reference
		self.level_ref = level_ref

	def import_graphics(self,name):
		self.animations = {'idle':[],'move':[],'attack':[]}
		main_path = f'../graphics/monsters/{name}/'
		for animation in self.animations.keys():
			self.animations[animation] = import_folder(main_path + animation)

	def get_player_distance_direction(self, player):
		"""Use A* pathfinding instead of calculating the direction of a straight line"""
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()
        
        # Check if the path needs to be updated
		current_time = pygame.time.get_ticks()
        
        # Update gaze detection
		if current_time - self.line_of_sight_cooldown > self.line_of_sight_interval:
			self.line_of_sight_cache = self.has_line_of_sight(player)
			self.line_of_sight_cooldown = current_time
        
        # If the player is within sight and the distance is relatively close, use the straight line direction
		if self.line_of_sight_cache and distance < self.notice_radius * 0.5:
			if distance > 0:
				direction = (player_vec - enemy_vec).normalize()
			else:
				direction = pygame.math.Vector2()
			return (distance, direction)
        
        # Use A* for finding your way
		if current_time - self.path_update_cooldown > self.path_update_interval:
            # Check if the player's position has moved far enough and recalculate the path
			if (not self.last_player_pos or 
                (player_vec - self.last_player_pos).length() > TILESIZE * 2):
                
				if hasattr(player, 'level') and player.level.pathfinder:
					self.path = player.level.get_path_to_player(self.rect.center)
					self.current_path_index = 0
					self.last_player_pos = player_vec.copy()
					self.path_update_cooldown = current_time
        
        # If there is a path, move along it
		if self.path and self.current_path_index < len(self.path):
			target_pos = pygame.math.Vector2(self.path[self.current_path_index])
			direction = (target_pos - enemy_vec)
            
            # If approaching the current path point, move on to the next one
			if direction.length() < TILESIZE // 2:
				self.current_path_index += 1
				if self.current_path_index < len(self.path):
					target_pos = pygame.math.Vector2(self.path[self.current_path_index])
					direction = (target_pos - enemy_vec)
            
			if direction.length() > 0:
				direction = direction.normalize()
            
			self.path_direction = direction
			return (distance, direction)
        
        # Retreat to the straight line direction
		if distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()
        
		return (distance, direction)

	def has_line_of_sight(self, player):
		"""Check if there is a direct line of sight between the enemy and the player (without any obstacles)"""
		enemy_pos = pygame.math.Vector2(self.rect.center)
		player_pos = pygame.math.Vector2(player.rect.center)
		direction = (player_pos - enemy_pos)
        
		if direction.length() == 0:
			return True
        
		direction = direction.normalize()
		distance = (player_pos - enemy_pos).length()
        
        # Radiographic testing
		step = TILESIZE // 4
		current_pos = enemy_pos.copy()
		steps = int(distance / step) + 1
        
		for _ in range(steps):
			current_pos += direction * step
            
            # Check if there are any obstacles at the current position
			for sprite in self.obstacle_sprites:
				if hasattr(sprite, 'hitbox'):
					if sprite.hitbox.collidepoint(current_pos.x, current_pos.y):
						return False
        
		return True

	def get_status(self, player):
		distance = self.get_player_distance_direction(player)[0]

		if distance <= self.attack_radius and self.can_attack:
			if self.status != 'attack':
				self.frame_index = 0
			self.status = 'attack'
		elif distance <= self.notice_radius:
			self.status = 'move'
		else:
			self.status = 'idle'

	def actions(self, player):
		if self.status == 'attack':
			self.attack_time = pygame.time.get_ticks()
			self.damage_player(self.attack_damage, self.attack_type)
			self.attack_sound.play()
		elif self.status == 'move':
            # Use the wayfinding direction
			distance, direction = self.get_player_distance_direction(player)
            
            # If there is a direct line of sight, use the direct direction first
			if self.line_of_sight_cache:
				self.direction = direction
			else:
                # Use the pathfinding direction, but make a smooth transition
				if self.path_direction.length() > 0:
                    # Smooth steering and avoid sudden turns
					self.direction = self.direction.lerp(self.path_direction, 0.2)
				else:
					self.direction = direction
		else:
			self.direction = pygame.math.Vector2()

	def animate(self):
		animation = self.animations[self.status]
		
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			if self.status == 'attack':
				self.can_attack = False
			self.frame_index = 0

		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if not self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

		if not self.vulnerable:
			if current_time - self.hit_time >= self.invincibility_duration:
				self.vulnerable = True

	def get_damage(self,player,attack_type):
		if self.vulnerable:
			self.hit_sound.play()
			self.direction = self.get_player_distance_direction(player)[1]
			if attack_type == 'weapon':
				self.health -= player.get_full_weapon_damage()
			else:
				self.health -= player.get_full_magic_damage()
			self.hit_time = pygame.time.get_ticks()
			self.vulnerable = False

	def check_death(self):
		if self.health <= 0:
			# Generate dropped items
			if self.level_ref:
				self.level_ref.trigger_item_drop(self.monster_name, self.rect.center)
			
			# If it's a raccoon, update the count
			if self.monster_name == 'raccoon' and hasattr(self.level_ref, 'raccoon_count'):
				self.level_ref.raccoon_count -= 1
			
			self.kill()
			self.trigger_death_particles(self.rect.center,self.monster_name)
			self.add_exp(self.exp)
			self.death_sound.play()

	def hit_reaction(self):
		if not self.vulnerable:
			self.direction *= -self.resistance

	def update(self):
		self.hit_reaction()
		self.move(self.speed)
		self.animate()
		self.cooldowns()
		self.check_death()

	def enemy_update(self,player):
		self.get_status(player)
		self.actions(player)