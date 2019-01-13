'''
Project: games
Created Date: Thursday, December 20th 2018, 1:48:26 am
Author: Zhefan Ye <zhefanye@gmail.com>
-----
Copyright (c) 2018 TBD
Do whatever you want
'''

import sys
import random

import pygame
from pygame.constants import K_UP, K_DOWN, K_SPACE
from ple.games.utils.vec2d import vec2d
from ple.games.utils import percent_round_int

#import base
from ple.games.base.pygamewrapper import PyGameWrapper


class Bullet(pygame.sprite.Sprite):

    def __init__(self, radius, speed, rng,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)

        self.rng = rng
        self.radius = radius
        self.speed = speed
        self.pos = vec2d(pos_init)
        self.pos_before = vec2d(pos_init)
        self.vel = vec2d((0, 0))
        self.is_shoot = False

        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        image = pygame.Surface((radius * 2, radius * 2))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            image,
            (255, 255, 255),
            (radius, radius),
            radius,
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def line_intersection(self, p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):

        s1_x = p1_x - p0_x
        s1_y = p1_y - p0_y
        s2_x = p3_x - p2_x
        s2_y = p3_y - p2_y

        s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / \
            (-s2_x * s1_y + s1_x * s2_y)
        t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / \
            (-s2_x * s1_y + s1_x * s2_y)

        return (s >= 0 and s <= 1 and t >= 0 and t <= 1)

    def update(self, agentPlayer, target, dy, dt):
        # bullet moves 1 pix at a time by default
        self.pos.x += self.vel.x * dt
        if not self.is_shoot:
            self.pos.y = agentPlayer.pos.y

        is_target_hit = False

        if self.pos.x >= target.pos.x - target.rect_width:
            if self.line_intersection(self.pos_before.x, self.pos_before.y, self.pos.x, self.pos.y,
                                      target.pos.x - target.rect_width / 2,
                                      target.pos.y - target.rect_height / 2,
                                      target.pos.x - target.rect_width / 2,
                                      target.pos.y + target.rect_height / 2):
                is_target_hit = True

        if self.pos.y - self.radius <= 0:
            self.pos.y += 1.0
            self.vel.x = 0

        if self.pos.y + self.radius >= self.SCREEN_HEIGHT:
            self.pos.y -= 1.0
            self.vel.x = 0

        self.pos_before.x = self.pos.x
        self.pos_before.y = self.pos.y

        self.rect.center = (self.pos.x, self.pos.y)
        return is_target_hit


class Player(pygame.sprite.Sprite):

    def __init__(self, speed, rect_width, rect_height,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)

        self.speed = speed
        self.pos = vec2d(pos_init)
        self.vel = vec2d((0, 0))

        self.rect_height = rect_height
        self.rect_width = rect_width
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        image = pygame.Surface((rect_width, rect_height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, rect_width, rect_height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dy, dt):
        self.vel.y = dy
        self.pos.y += self.vel.y * dt

        if self.pos.y - self.rect_height / 2 <= 0:
            self.pos.y = self.rect_height / 2
            self.vel.y = 0.0

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT - 1:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2 - 1
            self.vel.y = 0.0

        self.rect.center = (self.pos.x, self.pos.y)

    def updateTarget(self, bullet, dt):
        dy = 0.0
        if bullet.vel.x >= 0 and bullet.pos.x >= self.SCREEN_WIDTH / 2:
            dy = self.speed
            if self.pos.y > bullet.pos.y:
                dy = -1.0 * dy
        else:
            dy = 1.0 * self.speed / 4.0

            if self.pos.y > self.SCREEN_HEIGHT / 2.0:
                dy = -1.0 * self.speed / 4.0

        if self.pos.y - self.rect_height / 2 <= 0:
            self.pos.y = self.rect_height / 2
            self.vel.y = 0.0

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2
            self.vel.y = 0.0

        self.pos.y += dy * dt
        self.rect.center = (self.pos.x, self.pos.y)


class SimpleShooter(PyGameWrapper):
    def __init__(self, width=118, height=110, target_speed_ratio=1,
                 players_speed_ratio=1, bullet_speed_ratio=1, MAX_STEPS=10000):

        actions = {
            "up": K_UP,
            "down": K_DOWN,
            "shoot": K_SPACE
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        # the %'s come from original values, wanted to keep same ratio when you
        # increase the resolution.
        self.bullet_radius = percent_round_int(width, 0.025)

        self.target_speed_ratio = target_speed_ratio
        self.bullet_speed_ratio = bullet_speed_ratio
        self.players_speed_ratio = players_speed_ratio

        self.player_width = percent_round_int(width, 0.1)
        self.player_height = percent_round_int(height, 0.1)
        self.player_dist_to_wall = percent_round_int(width, 0.05)
        self.MAX_STEPS = MAX_STEPS
        self.n_steps = 0

        self.dy = 0.0
        self.score_sum = 0.0  # need to deal with 11 on either side winning
        self.score_counts = {
            "agent": 0.0
        }

    def _handle_player_events(self):
        self.dy = 0

        if __name__ == "__main__":
            # for debugging mode
            pygame.event.get()
            keys = pygame.key.get_pressed()
            if keys[self.actions['up']]:
                self.dy = -self.agentPlayer.speed
            if keys[self.actions['down']]:
                self.dy = self.agentPlayer.speed
            if keys[self.actions['shoot']]:
                self.bullet.is_shoot = True
                self.bullet.vel.x = self.bullet.speed

            if keys[pygame.QUIT]:
                pygame.quit()
                sys.exit()
            pygame.event.pump()
        else:
            # consume events from act
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == self.actions['up']:
                        self.dy = -self.agentPlayer.speed
                    if key == self.actions['down']:
                        self.dy = self.agentPlayer.speed
                    if key == self.actions['shoot']:
                        self.bullet.is_shoot = True
                        self.bullet.vel.x = self.bullet.speed

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player y position.
            * players velocity.
            * target y position.
            * bullet x position.
            * bullet y position.
            * bullet x velocity.
            * bullet y velocity.

            See code for structure.

        """
        state = {
            "player_y": self.agentPlayer.pos.y - self.player_height / 2,  # offset
            "player_velocity": self.agentPlayer.vel.y,
            "target_y": self.target.pos.y - self.player_height / 2,  # offset
            "bullet_x": self.bullet.pos.x - self.player_dist_to_wall,  # offset
            "bullet_y": self.bullet.pos.y - self.player_height / 2,  # offset
            "bullet_velocity_x": self.bullet.vel.x,
            "bullet_velocity_y": self.bullet.vel.y
        }

        return state

    def getScore(self):
        return self.score_sum

    def game_over(self):
        return (self.n_steps == self.MAX_STEPS)

    def init(self):
        self.score_counts = {
            "agent": 0.0
        }

        self.n_steps = 0
        self.score_sum = 0.0

        self.agentPlayer = Player(
            self.players_speed_ratio * self.height,
            self.player_width,
            self.player_height,
            (self.player_dist_to_wall, self.height / 2),
            self.width,
            self.height)

        self.target = Player(
            self.target_speed_ratio * self.height,
            self.player_width,
            self.player_height,
            (self.width - self.player_dist_to_wall,
             random.randrange(self.player_height / 2,
                              self.height - self.player_height / 2)),
            self.width,
            self.height)

        self.bullet = Bullet(
            self.bullet_radius,
            self.bullet_speed_ratio * self.height,
            self.rng,
            (self.agentPlayer.pos.x, self.agentPlayer.pos.y),
            self.width,
            self.height
        )

        self.players_group = pygame.sprite.Group()
        self.players_group.add(self.agentPlayer)
        self.players_group.add(self.target)

        self.bullet_group = pygame.sprite.Group()
        self.bullet_group.add(self.bullet)

    def reset(self):
        self.init()
        # after game over set random direction of bullet otherwise it will always be the same
        # self._reset_player()
        self._reset_bullet()

    def _reset_player(self):
        self.agentPlayer.pos.x = self.player_dist_to_wall
        self.agentPlayer.pos.y = self.height / 2
        self.agentPlayer.rect.center = (
            self.agentPlayer.pos.x, self.agentPlayer.pos.y)

    def _reset_target(self):
        self.target.pos.x = self.width - self.player_dist_to_wall
        self.target.pos.y = random.randrange(
            self.player_height / 2, self.height - self.player_height / 2)
        self.target.rect.center = (self.target.pos.x, self.target.pos.y)

    def _reset_bullet(self):
        self.bullet.pos.x = self.agentPlayer.pos.x
        self.bullet.pos.y = self.agentPlayer.pos.y
        self.bullet.is_shoot = False

        # we go in the same direction that they lost in but at starting vel.
        self.bullet.vel.x = 0
        self.bullet.vel.y = 0

    def step(self, dt):
        self.n_steps += 1
        dt = 0.01  # disabled for convenience
        self.screen.fill((0, 0, 0))

        # with dt=1, agent moves one pixel each step
        self.agentPlayer.speed = self.players_speed_ratio * 100
        self.target.speed = self.target_speed_ratio * self.height
        # with dt=1, bullet moves one pixel each step
        self.bullet.speed = self.bullet_speed_ratio * 100

        self._handle_player_events()

        # cost to move
        self.score_sum += self.rewards["tick"]

        self.agentPlayer.update(self.dy, dt)
        # self.target.updateCpu(self.bullet, dt)

        is_target_hit = self.bullet.update(
            self.agentPlayer, self.target, self.dy, dt)

        # logic
        if self.bullet.pos.x <= 0:
            self._reset_bullet()

        if self.bullet.pos.x >= self.width:
            self._reset_bullet()

        if is_target_hit:
            # self._reset_player()
            self._reset_bullet()
            self._reset_target()
            self.score_sum += self.rewards["positive"]
            self.score_counts['agent'] = self.score_sum

        self.players_group.draw(self.screen)
        self.bullet_group.draw(self.screen)


if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = SimpleShooter()
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 16)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(60)
        game.step(dt)
        print(game.getGameState())
        pygame.display.update()
