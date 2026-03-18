import pygame
import sys
from settings import *


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        # 替换为系统通用无装饰字体（避免自带方框）
        # 优先级：Windows(Arial/SimHei) → Mac/Linux(Helvetica/DejaVu Sans)
        self.title_font = pygame.font.SysFont(
            ['Arial', 'SimHei', 'Helvetica', 'DejaVu Sans'],
            END_FONT_SIZE,  # 使用与结束界面相同的字体大小
            bold=True  # 加粗标题增强视觉
        )
        self.text_font = pygame.font.SysFont(
            ['Arial', 'SimHei', 'Helvetica', 'DejaVu Sans'],
            END_SMALL_FONT_SIZE  # 使用与结束界面相同的字体大小
        )
        self.running = True  # 控制开始页面循环

        # 背景图片
        self.background = pygame.image.load('../graphics/menu/background.jpg').convert_alpha()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        # 创建半透明遮罩层
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((26, 26, 46, 150))  # 与结束界面相同的半透明颜色

        # 标题和选项（文字无隐藏装饰字符）
        self.title = self.title_font.render("ZELDA LIKE", True, END_TEXT_COLOR)
        self.title_rect = self.title.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        # 创建按钮（与结束界面相同的样式）
        self.start_button = Button(
            WIDTH // 2 - 150, HEIGHT // 2, 300, 60,
            "START GAME", self.text_font,
            END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR,
            TEXT_COLOR
        )

        self.quit_button = Button(
            WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60,
            "QUIT GAME", self.text_font,
            END_BUTTON_COLOR, END_BUTTON_HOVER_COLOR,
            TEXT_COLOR
        )

        # 粒子效果（与结束界面相同）
        self.particles = []
        self.particle_timer = 0

        # 闪烁提示文本
        self.instruction_text = self.text_font.render("Press ENTER to start or ESC to quit", True, (200, 200, 200))
        self.instruction_rect = self.instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.instruction_alpha = 255
        self.instruction_direction = -1  # -1表示减少，1表示增加

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    if self.start_button.is_hovered():
                        self.running = False
                    elif self.quit_button.is_hovered():
                        pygame.quit()
                        exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:  # 回车或空格开始游戏
                    self.running = False
                if event.key == pygame.K_ESCAPE:  # ESC退出
                    pygame.quit()
                    exit()

    def update_particles(self):
        """更新粒子效果（与结束界面相同）"""
        self.particle_timer += 1
        # 每3帧添加一个新粒子
        if self.particle_timer % 3 == 0:
            # 添加新的粒子 - 只使用垂直下落
            x = pygame.time.get_ticks() % WIDTH
            self.particles.append({
                'x': x,
                'y': -10,
                'speed': 2 + (pygame.time.get_ticks() % 10) / 10,  # 2.0 - 3.0 之间的速度
                'size': 1 + (pygame.time.get_ticks() % 4),  # 1-4的大小
                'color': (255, 255, 255, 150)  # 白色半透明
            })

        # 更新粒子位置
        for particle in self.particles[:]:
            particle['y'] += particle['speed']
            if particle['y'] > HEIGHT:
                self.particles.remove(particle)

    def draw_particles(self):
        """绘制粒子效果（与结束界面相同）"""
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

    def update_instruction_alpha(self):
        """更新提示文本的闪烁效果"""
        self.instruction_alpha += self.instruction_direction * 5
        if self.instruction_alpha <= 100:
            self.instruction_alpha = 100
            self.instruction_direction = 1
        elif self.instruction_alpha >= 255:
            self.instruction_alpha = 255
            self.instruction_direction = -1

        # 更新文本表面的透明度
        self.instruction_text.set_alpha(self.instruction_alpha)

    def draw(self):
        # 绘制背景图片
        self.screen.blit(self.background, (0, 0))

        # 绘制半透明遮罩层
        self.screen.blit(self.overlay, (0, 0))

        # 绘制粒子效果
        self.draw_particles()

        # 绘制标题
        self.screen.blit(self.title, self.title_rect)

        # 绘制按钮
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.draw(self.screen, mouse_pos)
        self.quit_button.draw(self.screen, mouse_pos)

        # 绘制闪烁的提示文本
        self.screen.blit(self.instruction_text, self.instruction_rect)

        pygame.display.update()

    def run(self):
        # 开始页面主循环
        while self.running:
            self.handle_events()
            self.update_particles()
            self.update_instruction_alpha()
            self.draw()
            pygame.time.delay(16)  # 约60FPS


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

        # 绘制按钮（与结束界面相同的样式）
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 3, border_radius=10)

        # 绘制文本
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)