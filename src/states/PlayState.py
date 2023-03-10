"""
ISPPJ1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""
import random

import pygame

from gale.factory import AbstractFactory
from gale.state_machine import BaseState
from gale.input_handler import InputHandler, InputData, InputData
from gale.text import render_text

import settings
import src.powerups
from src.Ball import Ball
from src.Cannon import Cannon
import time


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.speed = params["speed"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS *
            (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])
        self.reserve_balls_timer = 0
        self.speed_up_timer = 0
        self.cannon_timer = 0
        self.projectiles = []
        self.cannons = []

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

        InputHandler.register_listener(self)

    def exit(self) -> None:
        InputHandler.unregister_listener(self)

    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        for ball in self.balls:
            if ball.following_paddle:
                ball.x = self.paddle.x + self.paddle.width // 2 - 4
                ball.y = self.paddle.y - 8
            else:
                ball.update(dt)

            ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle):
                settings.SOUNDS["paddle_hit"].stop()
                settings.SOUNDS["paddle_hit"].play()
                ball.rebound(self.paddle)
                ball.push(self.paddle)
                ball.following_paddle = self.reserve_balls_timer > 0

            if self.reserve_balls_timer > 0 and \
                    time.time() - self.reserve_balls_timer >= 2.5 and \
                    ball.following_paddle:
                ball.following_paddle = False
                ball.vx = random.randint(-80, 80)
                ball.vy = random.randint(-170, -100)
                self.reserve_balls_timer = 0

            # Check collision with brickset
            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(
                ball.get_collision_rect())

            if brick is None:
                continue

            brick.hit()
            self.score += brick.score()
            ball.rebound(brick)

            # Check earn life
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            # Check growing up of the paddle
            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS *
                    (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            # Chance to generate two more balls
            if random.random() < 0.1:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("TwoMoreBall").create(
                        r.centerx - 8, r.centery - 8
                    ))
            elif random.random() < 0.3:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("SpeedUp").create(
                        r.centerx - 8, r.centery - 8
                    ))
            elif random.random() < 0.3:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("SimpleDoubleCannons").create(
                        r.centerx - 8, r.centery - 8
                    ))
            elif random.random() < 0.3:
                r = brick.get_collision_rect()
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory("ReServeBall").create(
                        r.centerx - 8, r.centery - 8
                    ))

        for projectile in self.projectiles:
            projectile.update(dt)

            if projectile.collides(self.brickset):
                projectile.solve_world_boundaries()

                brick = self.brickset.get_colliding_brick(
                    projectile.get_collision_rect())

                if brick is None:
                    continue

                brick.hit()
                self.score += brick.score()
                projectile.in_play = False

        if self.speed_up_timer != 0:
            if time.time() - self.speed_up_timer >= 5:
                self.speed = 1
                self.speed_up_timer = 0

        if len(self.cannons) > 0 and time.time() - self.cannon_timer >= 2.5:
            self.cannons = []

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.in_play]
        self.projectiles = [
            projectile for projectile in self.projectiles if projectile.in_play]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self)

        # Remove powerups that are not in play
        self.powerups = [p for p in self.powerups if p.in_play]

        # Check victory
        if self.brickset.size == 1 and next(
            (True for _, b in self.brickset.bricks.items() if b.broken), False
        ):
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
            )

        if len(self.cannons) > 0:
            self.cannons[0].x = self.paddle.x-self.cannons[0].width
            self.cannons[0].y = self.paddle.y - self.cannons[0].height

            self.cannons[1].x = self.paddle.x+self.paddle.width
            self.cannons[1].y = self.paddle.y - self.cannons[1].height

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x,
                                              5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x,
                                              5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)

        self.paddle.render(surface)

        for ball in self.balls:
            ball.render(surface)

        for cannon in self.cannons:
            cannon.render(surface)

        for projectile in self.projectiles:
            projectile.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED * self.speed
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED * self.speed
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
        elif input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause",
                level=self.level,
                score=self.score,
                lives=self.lives,
                paddle=self.paddle,
                balls=self.balls,
                brickset=self.brickset,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                powerups=self.powerups,
            )
        elif input_id == "enter" and input_data.pressed:
            for ball in self.balls:
                if ball.following_paddle:
                    ball.following_paddle = False
                    ball.vx = random.randint(-80, 80)
                    ball.vy = random.randint(-170, -100)

            self.reserve_balls_timers = {}
        elif input_id == "fire" and input_data.pressed:
            for cannon in self.cannons:
                cannon.shoot()

    def enable_speed_up(self):
        self.speed_up_timer = time.time()
        self.speed = 2

    def enable_cannons(self):
        if len(self.cannons) == 0:
            self.cannons.append(
                Cannon(self.paddle.x, self.paddle.y+self.paddle.height, self))
            self.cannons.append(
                Cannon(self.paddle.x-self.paddle.width, self.paddle.y+self.paddle.height, self))

            self.cannon_timer = time.time()
