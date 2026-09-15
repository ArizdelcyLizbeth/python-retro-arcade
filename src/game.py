import pygame
from src.gameObject import GameObject
from src.player import Player
from src.enemy import Enemy
from src.SoundManager import SoundManager

class Game:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.white_colour = (255, 255, 255)

        self.game_window = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # We initialize the sound manager
        self.sound_manager = SoundManager()
        self.is_waiting_for_sound = False
        self.sound_type = None
        self.game_won = False

        self.background = GameObject(0, 0, self.width, self.height, 'assets/images/background.png')
        self.treasure = GameObject(375, 50, 50, 50, 'assets/images/treasure.png')
        
        coin_img = pygame.image.load('assets/images/coins.png')
        self.coin_icon = pygame.transform.scale(coin_img, (35, 35))

        try:
            game_over_img = pygame.image.load('assets/images/logo-game-over.png')
            self.game_over_image = pygame.transform.scale(game_over_img, (400, 200))
        except (pygame.error, FileNotFoundError, OSError):
            font = pygame.font.SysFont(None, 50)
            self.game_over_image = font.render("¡VICTORIA!", True, (255, 0, 0))

        try:
            repeat_img = pygame.image.load('assets/images/repeat.png')
            self.repeat_image = pygame.transform.scale(repeat_img, (100, 100))
        except (pygame.error, FileNotFoundError, OSError):
            font = pygame.font.SysFont(None, 30)
            self.repeat_image = font.render("[ REPETIR ]", True, (0, 0, 255))
            
        # We define the repeat button's rectangle to detect clicks
        self.repeat_rect = self.repeat_image.get_rect(center=(self.width // 2, 500))

        self.victories = 0
        self.reset_map()

    def reset_map(self):
        self.player = Player(375, 700, 50, 50, 'assets/images/player.png', 10)
        
        # The difficulty of the monsters increases every two victories
        num_enemies = 1 + (self.victories // 2)
        speed = 5 + (self.victories * 1.5)

        if num_enemies >= 3:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/images/enemy.png', speed),
                Enemy(750, 400, 50, 50, 'assets/images/enemy.png', speed),
                Enemy(0, 200, 50, 50, 'assets/images/enemy.png', speed),
            ]
        elif num_enemies == 2:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/images/enemy.png', speed),
                Enemy(750, 400, 50, 50, 'assets/images/enemy.png', speed),
            ]
        else:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/images/enemy.png', speed),
            ]

    def restart_game(self):
        self.sound_manager.sound_channel.stop()
        
        self.victories = 0
        self.game_won = False
        self.is_waiting_for_sound = False
        self.sound_type = None
        self.reset_map()

    def draw_objects(self):
        self.game_window.fill(self.white_colour)

        # Draw background
        self.game_window.blit(self.background.image, (self.background.x, self.background.y))
        
        if not self.game_won:
            self.game_window.blit(self.treasure.image, (self.treasure.x, self.treasure.y))
            self.game_window.blit(self.player.image, (self.player.x, self.player.y))

            for enemy in self.enemies:
                self.game_window.blit(enemy.image, (enemy.x, enemy.y))

            coins_to_show = self.victories // 2
            for i in range(coins_to_show):
                self.game_window.blit(self.coin_icon, (20 + (i * 45), 20))
        else:
            logo_x = (self.width - self.game_over_image.get_width()) // 2
            self.game_window.blit(self.game_over_image, (logo_x, 250))
            
            self.repeat_rect = self.repeat_image.get_rect(center=(self.width // 2, 500))
            self.game_window.blit(self.repeat_image, self.repeat_rect.topleft)

        pygame.display.update()

    def move_objects(self, player_direction):
        if self.game_won:
            return
        self.player.move(player_direction, self.height)
        for enemy in self.enemies:
            enemy.move(self.width)

    def detect_collision(self, object_1, object_2):
        if object_1.y < (object_2.y + object_2.height) and (object_1.y + object_1.height) > object_2.y and object_1.x < (object_2.x + object_2.width) and (object_1.x + object_1.width) > object_2.x:
            return True
        return False

    def run_game_loop(self):
        player_direction = 0

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                
                if self.game_won:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.repeat_rect.collidepoint(event.pos):
                            self.restart_game()
                            player_direction = 0
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.restart_game()
                            player_direction = 0
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player_direction = -1
                    elif event.key == pygame.K_DOWN:
                        player_direction = 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        player_direction = 0

            if self.is_waiting_for_sound:
                if not self.sound_manager.is_busy():
                    if self.sound_type == 'blow':
                        self.victories = 0  
                        self.reset_map()
                        player_direction = 0
                    elif self.sound_type == 'win_game':
                        pass
                    elif self.sound_type == 'yippee':
                        self.reset_map()
                        player_direction = 0
                    
                    if self.sound_type != 'win_game':
                        self.is_waiting_for_sound = False
            elif not self.game_won:
                self.move_objects(player_direction)

                hit_enemy = False
                for enemy in self.enemies:
                    if self.detect_collision(self.player, enemy):
                        hit_enemy = True
                        break

                if hit_enemy:
                    self.sound_manager.play_blow()
                    self.sound_type = 'blow'
                    self.is_waiting_for_sound = True
                
                elif self.detect_collision(self.player, self.treasure):
                    self.victories += 1
                    
                    # Upon reaching 6 victories, the victory screen is displayed
                    if self.victories >= 6:
                        self.game_won = True
                        self.sound_manager.play_game_objective()
                        self.sound_type = 'win_game'
                        self.is_waiting_for_sound = True
                    else:
                        self.sound_manager.play_yippee()
                        self.sound_type = 'yippee'
                        self.is_waiting_for_sound = True

            self.draw_objects()
            self.clock.tick(60)
            