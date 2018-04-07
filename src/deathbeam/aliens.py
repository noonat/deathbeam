from __future__ import absolute_import
import math

from . import defs
from .actors import Actor, register_actor
from .particles import TurretBullet
from .sounds import AmbientSound, Sound


@register_actor
class Mothership(Actor):

    BEAM_COLORS = [
        (0, 1, 1, 0.5),
        (1, 0.5, 0.5, 0.5),
        (1, 1, 0, 0.5),
    ]
    BEAM_COUNT = 6
    BEAM_ROTATE_TIME = 0.1
    BEAM_WIDTH = 2
    BEAM_Z = defs.Z_BEAM
    CELL_TYPE = defs.CELL_ALIEN_MOTHERSHIP
    COLLIDE_WITH_ACTORS = False
    COLLIDE_WITH_WORLD = False
    SPEED = 20
    WIDTH = 32
    HEIGHT = 16
    Z = defs.Z_ACTOR_FOREGROUND

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beam_rotate = 0
        self.beam_rotate_time = 0
        self.beam_sounds = [
            AmbientSound(self, 'deathbeam_sweep.wav', auto_update=False,
                         pitch=1.5, volume=0.5),
            AmbientSound(self, 'deathbeam_whine.wav', auto_update=False)]

    def draw(self):
        # ship
        self.game.draw.quad(self.x - self.WIDTH / 2, self.y, self.WIDTH,
                            self.HEIGHT, self.Z, (0, 0, 0, 1))

        # beam
        while self.game.time >= self.beam_rotate_time:
            self.beam_rotate = (self.beam_rotate + 1) % self.BEAM_COUNT
            self.beam_rotate_time += self.BEAM_ROTATE_TIME
        bw = self.BEAM_WIDTH * self.BEAM_COUNT
        bx = self.x - bw / 2
        for i in range(self.BEAM_COUNT):
            color = (self.BEAM_COLORS[(self.beam_rotate + i) %
                     len(self.BEAM_COLORS)])
            self.game.draw.quad(bx, 0, self.BEAM_WIDTH, self.y, self.BEAM_Z,
                                color)
            bx += self.BEAM_WIDTH

    def update(self, dt):
        self.x += self.SPEED * dt
        for s in self.beam_sounds:
            s.update((self.x, self.game.player.y, 0))


@register_actor
class Turret(Actor):

    CELL_TYPE = defs.CELL_ALIEN_TURRET
    COLOR = (0.4, 0.4, 0.4, 1)
    VOLLEY_DELAY = 2.0
    VOLLEY_RANGE = 256
    VOLLEY_ROUNDS = 3
    VOLLEY_ROUNDS_DELAY = 0.5
    VOLLEY_ROUNDS_SPEED = 200
    WIDTH = 10
    HEIGHT = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fire_sound = Sound(self, 'turret_fire.wav')
        self.volley_rounds = 0
        self.volley_time = self.game.time + self.VOLLEY_DELAY

    def fire(self, normal_x, normal_y, spawn_time):
        self.fire_sound.play()
        bullet = self.game.spawn(TurretBullet, self.x, self.y, spawn_time)
        bullet.vel_x = normal_x * self.VOLLEY_ROUNDS_SPEED
        bullet.vel_y = normal_y * self.VOLLEY_ROUNDS_SPEED

    def update(self, dt):
        super().update(dt)
        if self.volley_time <= self.game.time:
            if self.volley_rounds >= self.VOLLEY_ROUNDS:
                self.volley_time = self.game.time + self.VOLLEY_DELAY
                self.volley_rounds = 0
            else:
                self.volley_time = self.game.time + self.VOLLEY_ROUNDS_DELAY
                self.volley_rounds += 1
                dx = self.game.player.x - self.x
                dy = self.game.player.y - self.y
                length = math.sqrt(dx*dx + dy*dy)
                if length and length <= self.VOLLEY_RANGE:
                    dx /= length
                    dy /= length
                    self.fire(dx, dy, self.game.time)
