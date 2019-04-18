'''
Project: games
Created Date: Tuesday, January 29th 2019, 9:23:42 pm
Author: Zhefan Ye <zhefanye@gmail.com>
-----
Copyright (c) 2019 TBD
Do whatever you want
'''

import sys
import random

import pygame
from pygame.constants import K_UP, K_DOWN, K_SPACE
from ple.games.utils.vec2d import vec2d

#import base
from ple.games.base.pygamewrapper import PyGameWrapper


class Bullet(pygame.sprite.Sprite):

    def __init__(self, square_width, speed,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)

        self.square_width = square_width
        self.speed = speed
        self.pos = vec2d(pos_init)
        self.pos_before = vec2d(pos_init)
        self.vel = vec2d((0, 0))

        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        image = pygame.Surface((square_width, square_width))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, square_width, square_width),
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

    def update(self, targets, dt):
        """update bullet movement

        Arguments:
            target {[type]} -- [description]
            dt {float} -- 0.01

        Returns:
            int -- > 0 if hit, 0 out of bound
        """

        # bullet moves 1 pix at a time by default
        self.pos.x += self.speed * dt
        ret_val = -1

        # target hit
        if isinstance(targets, list):
            for idx, target in enumerate(targets):
                if self.pos.x == target.pos.x and self.pos.y == target.pos.y:
                    ret_val = idx + 1
        else:
            if self.pos.x == targets.pos.x and self.pos.y == targets.pos.y:
                ret_val = 1

        # boundry check
        if self.pos.y < 0 or self.pos.y > self.SCREEN_HEIGHT or \
                self.pos.x < 0 or self.pos.x > self.SCREEN_WIDTH:
            ret_val = 0

        self.pos_before.x = self.pos.x
        self.pos_before.y = self.pos.y

        self.rect.center = (self.pos.x, self.pos.y)
        return ret_val


class Player(pygame.sprite.Sprite):

    def __init__(self, speed, rect_width, rect_height,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT, color=(255, 0, 0)):

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
            color,
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

    def updateMovingTarget(self, dt, steps):
        if steps % 5 == 0:  # move every 5 steps
            self.vel.y = self.speed
            self.pos.y += self.vel.y * dt

        if self.pos.y - self.rect_height / 2 < 0:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2 - 1

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT:
            self.pos.y = self.rect_height / 2

        self.rect.center = (self.pos.x, self.pos.y)

    def updateRandomTarget(self, dt, steps):
        if steps % 5 == 0:  # move every 5 steps
            if random.uniform(-1, 1) < 0:
                self.vel.y = -1 * self.speed
            else:
                self.vel.y = self.speed
            self.pos.y += self.vel.y * dt

        if self.pos.y - self.rect_height / 2 <= 0:
            self.pos.y = self.rect_height / 2

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT - 1:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2 - 1

        self.rect.center = (self.pos.x, self.pos.y)


class DotShooter(PyGameWrapper):
    def __init__(self, version=0, width=52, height=50, target_speed_ratio=1,
                 players_speed_ratio=1, bullet_speed_ratio=1, MAX_STEPS=200):

        actions = {
            "up": K_UP,
            "down": K_DOWN,
            "shoot": K_SPACE
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)
        self.version = version
        # the %'s come from original values, wanted to keep same ratio when you
        # increase the resolution.
        self.bullet_width = 1
        self.max_bullets = 1

        self.target_speed_ratio = target_speed_ratio
        # with dt=1, bullet moves one pixel each step
        self.bullet_speed = bullet_speed_ratio * 100
        self.players_speed_ratio = players_speed_ratio

        self.player_width = 1
        self.player_height = 1
        self.player_dist_to_wall = 1
        self.MAX_STEPS = MAX_STEPS
        self.n_steps = 0
        self.target_hit = False

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
            if keys[self.actions['shoot']] and len(self.bullet_group) < self.max_bullets:
                bullet = self._create_bullet()
                self.bullet_group.add(bullet)
                self.bullet_list.append(bullet)

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
                    if key == self.actions['shoot'] and len(self.bullet_group) < self.max_bullets:
                        bullet = self._create_bullet()
                        self.bullet_group.add(bullet)
                        self.bullet_list.append(bullet)

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player y position.
            * target y position.

            See code for structure.

        """
        state = {
            "player_y": self.agentPlayer.pos.y - self.player_height / 2,  # offset
            "target_y": self.target.pos.y - self.player_height / 2,  # offset
            "bullet": len(self.bullet_group)  # number of bullets, max 1
        }

        return state

    def getScore(self):
        return self.score_sum

    def game_over(self):
        if self.version == 4:  # shot clock
            # exceed max step and no bullet in flight
            if self.n_steps >= self.MAX_STEPS and len(self.bullet_group) == 0:
                return True
        elif self.version == 5 or self.version == 6:  # shot clock one hit
            if self.n_steps >= self.MAX_STEPS and len(self.bullet_group) == 0:
                return True
            return self.target_hit
        else:
            if self.n_steps == self.MAX_STEPS:
                return True
            if self.version == 3:
                return self.target_hit
        return False

    def init(self):
        self.score_counts = {
            "agent": 0.0
        }

        self.n_steps = 0
        self.score_sum = 0.0

        if self.version == 6:
            self.agentPlayer = Player(
                self.players_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.player_dist_to_wall,
                 random.randrange(self.player_height / 2,
                                  self.height - self.player_height / 2)),
                self.width, self.height)
            self.target = Player(
                self.target_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.width - self.player_dist_to_wall, self.height / 2),
                self.width, self.height)
            self.target_1 = Player(  # distraction
                self.target_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.width - self.player_dist_to_wall, self.height / 4),
                self.width, self.height, color=(0, 255, 0))
            self.target_2 = Player(  # distraction
                self.target_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.width - self.player_dist_to_wall, self.height * 3 / 4),
                self.width, self.height, color=(0, 255, 0))
        else:
            self.agentPlayer = Player(
                self.players_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.player_dist_to_wall, self.height / 2),
                self.width, self.height)
            self.target = Player(
                self.target_speed_ratio * self.height,
                self.player_width,
                self.player_height,
                (self.width - self.player_dist_to_wall,
                 random.randrange(self.player_height / 2,
                                  self.height - self.player_height / 2)),
                self.width, self.height)

        self.players_group = pygame.sprite.Group()
        self.players_group.add(self.agentPlayer)
        self.players_group.add(self.target)
        if self.version == 6:
            self.players_group.add(self.target_1)
            self.players_group.add(self.target_2)

        self.bullet_group = pygame.sprite.Group()
        self.bullet_list = []
        self.target_hit = False

    def _create_bullet(self):
        bullet = Bullet(
            self.bullet_width,
            self.bullet_speed,
            (self.agentPlayer.pos.x, self.agentPlayer.pos.y),
            self.width,
            self.height
        )
        return bullet

    def reset(self):
        # clear existing groups
        self.players_group.empty()
        self.bullet_group.empty()
        del self.bullet_list[:]
        self.init()
        # after game over set random direction of bullet otherwise it will always be the same
        # self._reset_player()

    def _reset_player(self):
        self.agentPlayer.pos.x = self.player_dist_to_wall
        self.agentPlayer.pos.y = self.height / 2
        self.agentPlayer.rect.center = (
            self.agentPlayer.pos.x, self.agentPlayer.pos.y)

    def _reset_target(self):
        if self.version == 3 or self.version == 5 or self.version == 6:
            raise ValueError('Not reset target for v6')
        self.target.pos.x = self.width - self.player_dist_to_wall
        self.target.pos.y = random.randrange(
            self.player_height / 2, self.height - self.player_height / 2)
        self.target.rect.center = (self.target.pos.x, self.target.pos.y)

    def step(self, dt):
        self.n_steps += 1
        dt = 0.01  # disabled for convenience
        self.screen.fill((0, 0, 0))

        # with dt=1, agent moves one pixel each step
        self.agentPlayer.speed = self.players_speed_ratio * 100
        self.target.speed = self.target_speed_ratio * 100

        self._handle_player_events()

        # cost to move
        self.score_sum += self.rewards["tick"]

        self.agentPlayer.update(self.dy, dt)
        if self.version == 1:  # moving target
            self.target.updateMovingTarget(dt, self.n_steps)
        elif self.version == 2:  # random moving target
            self.target.updateRandomTarget(dt, self.n_steps)

        to_del = []
        for idx, bullet in enumerate(self.bullet_list):
            if self.version == 6:
                target_list = [self.target, self.target_1, self.target_2]
                bullet_status = bullet.update(target_list, dt)
            else:
                bullet_status = bullet.update(self.target, dt)

            if bullet_status >= 1:  # target hit
                # self._reset_player()
                to_del.append(idx)
                self.bullet_group.remove(bullet)
                if not (self.version == 3 or self.version == 5 or self.version == 6):
                    self._reset_target()  # reset if not one hit
                if bullet_status == 1:  # hit main target
                    self.score_sum += self.rewards["positive"]
                else:  # hit distractions
                    self.score_sum += 0.5
                self.score_counts['agent'] = self.score_sum
                self.target_hit = True
            elif bullet_status == 0:  # out of bound
                to_del.append(idx)
                self.bullet_group.remove(bullet)
        # delete bullets in the list
        for index in sorted(to_del, reverse=True):
            del self.bullet_list[index]

        self.players_group.draw(self.screen)
        self.bullet_group.draw(self.screen)


if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = DotShooter(version=6)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 16)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(60)
        game.step(dt)
        if game.bullet_list:
            print('player x: {}, player y: {}, target x: {}, target y: {}, bullet x: {}, score {}'.format(
                game.agentPlayer.pos.x, game.agentPlayer.pos.y, game.target.pos.x,
                game.target.pos.y, game.bullet_list[0].pos.x, game.score_sum))
        else:
            print(game.getGameState(), len(game.bullet_list), game.score_sum)
        pygame.display.update()
