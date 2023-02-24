"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the specialization of PowerUp to add two more ball to the game.
"""
import random
from typing import TypeVar

import settings
from src.powerups.PowerUp import PowerUp
import time

class SpeedUp(PowerUp):
    """
    Power-up to speed up the paddle
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 8)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.play_state = play_state
        settings.SOUNDS["paddle_hit"].stop()
        settings.SOUNDS["paddle_hit"].play()
        play_state.speed = 2
        self.in_play = False
        self.speed_up_timmer = time.time()