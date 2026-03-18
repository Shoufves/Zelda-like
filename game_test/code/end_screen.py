# file name: end_screen.py
import pygame
import sys
from settings import *


class EndScreen:
    def __init__(self, screen, final_score=0, floor_depth=1):
        self.screen = screen
        self.final_score = final_score
        self.floor_depth = floor_depth
        self.running = True

        # 加载�?定义字体，�?�果失败则使用系统字�?
        try:
            self.title_font = pygame.font.Font('../graphics/font/joystix.ttf', END_FONT_SIZE)
            self.text_font = pygame.font.Font('../graphics/font/joystix.ttf', END_SMALL_FONT_SIZE)
        except:
            self.title_font = pygame.font.SysFont(['Arial', 'SimHei', 'Helvetica'], END_FONT_SIZE)
            self.text_font = pygame.font.SysFont(['Arial', 'SimHei', 'Helvetica'], END_SMALL_FONT_SIZE)

        # ========== 添加背景图片 ==========
        # 尝试加载背景图片，�?�果失败则使用纯色背�?
        try:
            # 使用与开始界面相同的背景图片�?�?
            self.background_image = pygame.image.load('../graphics/menu/background.jpg').convert_alpha()
            # 缩放背景图片以适应屏幕尺�??
            self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
            self.use_image_background = True
        except Exception as e:
            print(f"无法加载结束界面背景图片: {e}")
            self.background_image = None
            self.use_image_background = False

        # 创建半透明�?罩层（�?�文字在背景图片上更清晰�?
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((26, 26, 46, 180))  # 半透明深蓝色，调整透明度为180
        # ========== 背景图片部分结束 ==========

        # 创建文本表面
        self.title = self.title_font.render("GAME OVER", True, END_TEXT_COLOR)
        self.title_rect = self.title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        self.score_text = self.text_font.render(f"Final Exp: {int(self.final_score)}", True, TEXT_COLOR)
        self.score_rect = self.score_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 60))

        self.floor_text = self.text_font.render(f"Floor Reached: {self.floor_depth}", True, TEXT_COLOR)
        self.floor_rect = self.floor_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 110))

        # 创建按钮
        self.restart_button = Button(
            WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60,
            "RESTART", self.text_font,
            END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR,
            TEXT_COLOR
        )

        self.quit_button = Button(
            WIDTH // 2 - 150, HEIGHT // 2 + 130, 300, 60,
            "QUIT", self.text_font,
            END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR,
            TEXT_COLOR
        )

        # �?色背�?（�?�用，当图片加载失败时使�?�?
        self.solid_background = pygame.Surface((WIDTH, HEIGHT))
        self.solid_background.fill(END_BG_COLOR)
        self.solid_background.set_alpha(220)  # 半透明效果

        # 简化的粒子效果 - �?使用垂直下落
        self.particles = []
        self.particle_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    if self.restart_button.is_hovered():
                        return "restart"
                    elif self.quit_button.is_hovered():
                        pygame.quit()
                        sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R�?重新开�?
                    return "restart"
                elif event.key == pygame.K_ESCAPE:  # ESC�?退�?
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:  # Enter�?重新开�?
                    return "restart"

        return None

    def update_particles(self):
        self.particle_timer += 1
        # �?3帧添加一�?新粒�?
        if self.particle_timer % 3 == 0:
            # 添加新的粒子 - �?使用垂直下落
            x = pygame.time.get_ticks() % WIDTH
            self.particles.append({
                'x': x,
                'y': -10,
                'speed': 2 + (pygame.time.get_ticks() % 10) / 10,  # 2.0 - 3.0 之间的速度
                'size': 1 + (pygame.time.get_ticks() % 4),  # 1-4的大�?
                'color': (255, 255, 255, 150)  # 白色半透明
            })

        # 更新粒子位置
        for particle in self.particles[:]:
            particle['y'] += particle['speed']
            if particle['y'] > HEIGHT:
                self.particles.remove(particle)

    def draw_particles(self):
        for particle in self.particles:
            # 创建临时表面绘制圆形
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                particle['color'],
                (particle['size'], particle['size']),
                particle['size']
            )
            self.screen.blit(particle_surface,
                             (particle['x'] - particle['size'], particle['y'] - particle['size']))

    def draw(self):
        # ========== 绘制背景 ==========
        if self.use_image_background:
            # 绘制背景图片
            self.screen.blit(self.background_image, (0, 0))
            # 绘制半透明�?罩层
            self.screen.blit(self.overlay, (0, 0))
        else:
            # 如果图片加载失败，使用纯色背�?
            self.screen.blit(self.solid_background, (0, 0))
        # ========== 背景绘制结束 ==========

        # 绘制粒子
        self.draw_particles()

        # 绘制文本
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.score_text, self.score_rect)
        self.screen.blit(self.floor_text, self.floor_rect)

        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.draw(self.screen, mouse_pos)
        self.quit_button.draw(self.screen, mouse_pos)

        # 绘制提示文本
        hint = self.text_font.render("Press R/ENTER to restart or ESC to quit", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(hint, hint_rect)

        pygame.display.update()

    def run(self):
        while self.running:
            result = self.handle_events()
            if result == "restart":
                return True  # 重新开始游�?

            self.update_particles()
            self.draw()
            pygame.time.delay(16)  # �?60FPS


class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface, mouse_pos):
        # 更新颜色
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

        # 绘制按钮
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 3, border_radius=10)

        # 绘制文本
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)