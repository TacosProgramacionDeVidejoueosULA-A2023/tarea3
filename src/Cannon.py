from src.states import PlayState
from src.Projectile import Projectile
from gale.factory import Factory
import settings
import random


class Cannon:
    def __init__(self, x: int, y: int, play_state: PlayState) -> None:
        self.x = x
        self.y = y
        self.projectile_factory = Factory(Projectile)
        self.texture = settings.TEXTURES["cannon"]
        frame = settings.FRAMES["cannons"][0]
        self.height = frame.height
        self.width = frame.width
        self.play_state = play_state

    def shoot(self):
        projectile = self.projectile_factory.create(self.x, self.y)
        projectile.vx = random.randint(-80, 80)
        projectile.vy = random.randint(-170, -100)
        self.play_state.projectiles.append(projectile)
        

    def render(self, surface):
        surface.blit(
            self.texture, (self.x, self.y), settings.FRAMES["cannons"][0]
        )
