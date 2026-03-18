# -*- coding: utf-8 -*-
import pygame, sys
from settings import *
from level import Level
from start_screen import StartScreen
from end_screen import EndScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()
        self.game_active = False

        self.start_screen = StartScreen(self.screen)
        self.level = None

        self.main_sound = pygame.mixer.Sound('../audio/main.ogg')
        self.main_sound.set_volume(0.5)
        self.main_sound_playing = False

    def reset_game(self):
        if self.main_sound_playing:
            self.main_sound.stop()
            self.main_sound_playing = False

        self.level = Level()
        self.game_active = True

        self.main_sound.play(loops=-1)
        self.main_sound_playing = True

    def show_end_screen(self):
        if self.main_sound_playing:
            self.main_sound.stop()
            self.main_sound_playing = False

        final_score = self.level.player.exp if self.level and self.level.player else 0
        floor_depth = self.level.floor_depth if self.level else 1

        end_screen = EndScreen(self.screen, final_score, floor_depth)
        should_restart = end_screen.run()

        return should_restart

    def run(self):
        self.start_screen.run()

        self.reset_game()

        while True:
            if self.game_active and self.level and self.level.player and self.level.player.is_dead:
                self.game_active = False
                if not self.show_end_screen():
                    pygame.quit()
                    sys.exit()
                else:
                    self.reset_game()
                continue
            
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN and self.game_active:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
                    # Add 'B' press
                    elif event.key == pygame.K_b:
                        self.level.toggle_inventory()

            if self.game_active and self.level:
                self.screen.fill(WATER_COLOR)
                self.level.run(events)
                pygame.display.update()

            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()