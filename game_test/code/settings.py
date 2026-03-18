import json
import os

# 游戏设置
WIDTH    = 1280	
HEIGHT   = 720
FPS      = 60
TILESIZE = 64
HITBOX_OFFSET = {
	'player': -26,
	'object': -40,
	'grass': -10,
	'invisible': 0}

# ui 
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = '../graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

# 通用颜色
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui 颜色
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# 升级菜单
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

# Open 'weapons.json'
weapon_json_path = os.path.join(parent_dir, 'data', 'weapons.json')
with open(weapon_json_path, 'r', encoding='utf-8') as f:
    weapon_data = json.load(f)

# Open 'magic.json'
magic_json_path = os.path.join(parent_dir, 'data', 'magic.json')
with open(magic_json_path, 'r', encoding='utf-8') as f:
    magic_data = json.load(f)

# Open 'monsters.json'
monster_json_path = os.path.join(parent_dir, 'data', 'monsters.json')
with open(monster_json_path, 'r', encoding='utf-8') as f:
    monster_data = json.load(f)
    
# Open 'items.json'
item_json_path = os.path.join(parent_dir, 'data', 'items.json')
with open(item_json_path, 'r', encoding='gbk') as f:
    item_data = json.load(f)
    
# Access item data
ITEMS_DATA = item_data.get('items', {})
MONSTER_DROP_TABLES = item_data.get('monster_drop_tables', {})
RARITY_COLORS = item_data.get('rarity_colors', {})

FLOOR_ENEMY_MULTIPLIER = 1.1
FLOOR_EXP_BONUS = 1.2

# 结束界面
END_BG_COLOR = '#1a1a2e'
END_TEXT_COLOR = '#ff6b6b'
END_BUTTON_COLOR = '#4ecdc4'
END_BUTTON_HOVER_COLOR = '#45b7af'
END_FONT_SIZE = 64
END_SMALL_FONT_SIZE = 32