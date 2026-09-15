import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        pygame.mixer.music.load('assets/sounds/GeneralGameMusic.mp3')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        self.yippee = pygame.mixer.Sound('assets/sounds/yippee.mp3')
        self.yippee.set_volume(0.6)

        self.blow = pygame.mixer.Sound('assets/sounds/blow.mp3')
        self.blow.set_volume(0.6)

        self.game_objective = pygame.mixer.Sound('assets/sounds/GameObjective.mp3')
        self.game_objective.set_volume(0.6)

        self.sound_channel = pygame.mixer.Channel(1)

    def play_yippee(self):
        return self.sound_channel.play(self.yippee)

    def play_blow(self):
        return self.sound_channel.play(self.blow)

    def play_game_objective(self):
        return self.sound_channel.play(self.game_objective)

    def is_busy(self):
        return self.sound_channel.get_busy()
    