"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the specialization of PowerUp to add two more ball to the game.
"""
import random
from typing import TypeVar

from gale.factory import Factory

import settings
from src.Ball import Ball
from src.powerups.PowerUp import PowerUp
from threading import Timer


class SimpleDoubleCannons(PowerUp):
    """
    Power-up to add two more ball to the game.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 8)
        self.play_state = None

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.play_state = play_state
        self.play_state.enable_cannons()

        self.in_play = False