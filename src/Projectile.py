"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Ball.
"""
import random
from typing import Any, Tuple, Optional

import pygame

import settings


class Projectile:
    def __init__(self, x: int, y: int, following_paddle: bool = False) -> None:
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8

        self.vx = 0
        self.vy = 0

        self.texture = settings.TEXTURES["spritesheet"]
        self.frame = random.randint(0, 6)
        self.in_play = True
        self.following_paddle = following_paddle

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def solve_world_boundaries(self) -> None:
        r = self.get_collision_rect()

        if r.left < 0:
            settings.SOUNDS["wall_hit"].stop()
            settings.SOUNDS["wall_hit"].play()
            self.x = 0
            self.vx *= -1
        elif r.right > settings.VIRTUAL_WIDTH:
            settings.SOUNDS["wall_hit"].stop()
            settings.SOUNDS["wall_hit"].play()
            self.x = settings.VIRTUAL_WIDTH - self.width
            self.vx *= -1
        elif r.top < 0:
            settings.SOUNDS["wall_hit"].stop()
            settings.SOUNDS["wall_hit"].play()
            self.y = 0
            self.vy *= -1
        elif r.top > settings.VIRTUAL_HEIGHT:
            settings.SOUNDS["hurt"].play()
            self.in_play = False

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def render(self, surface):
        surface.blit(
            self.texture, (self.x, self.y), settings.FRAMES["balls"][self.frame]
        )

    @staticmethod
    def get_intersection(r1: pygame.Rect, r2: pygame.Rect) -> Optional[Tuple[int, int]]:
        """
        Compute, if exists, the intersection between two
        rectangles.
        """
        if r1.x > r2.right or r1.right < r2.x or r1.bottom < r2.y or r1.y > r2.bottom:
            # There is no intersection
            return None

        # Compute x shift
        if r1.centerx < r2.centerx:
            x_shift = r2.x - r1.right
        else:
            x_shift = r2.right - r1.x

        # Compute y shift
        if r1.centery < r2.centery:
            y_shift = r2.y - r1.bottom
        else:
            y_shift = r2.bottom - r1.y

        return (x_shift, y_shift)