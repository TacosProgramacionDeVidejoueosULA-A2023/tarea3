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
import time

class ReServeBall(PowerUp):
    """
    Power-up to add two more ball to the game.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 8)
        self.ball_factory = Factory(Ball)
        self.play_state = None

    def take(self, play_state: TypeVar("PlayState")) -> None:
        self.play_state = play_state
        paddle = play_state.paddle
        ball = self.ball_factory.create(paddle.x + paddle.width // 2 - 4, paddle.y - 8, {
            "following_paddle": True
        })
        settings.SOUNDS["paddle_hit"].stop()
        settings.SOUNDS["paddle_hit"].play()

        self.play_state.balls.append(ball)
        self.in_play = False
        self.play_state.reserve_balls_timers[time.time()] = ball