import math
import random

from pyglet import gl

import defs
import helpers
from actors import Actor
from game import Draw, Game


class Particle(Actor):

    COLLIDE_WITH_ACTORS = False
    COLLIDE_WITH_WORLD = False
    COLOR = (0.0, 0.0, 0.0, 1.0)
    LIFE_FADE = True
    LIFE_TIME = 1.0
    RANDOM_X = 0.0
    RANDOM_Y = 0.0
    RANDOM_VEL_X = 0.0
    RANDOM_VEL_Y = 0.0
    WIDTH = 1
    HEIGHT = 1
    Z = defs.Z_PARTICLE_BACKGROUND

    def __init__(self, x=0.0, y=0.0, spawn_time=None, **kwargs):
        super(Particle, self).__init__(x, y)
        self.spawn_time = spawn_time or Game.time
        self.life_time = self.LIFE_TIME
        if self.life_time is not None:
            self.death_time = self.spawn_time + self.LIFE_TIME
        else:
            self.death_time = None
        self.color = self.COLOR
        self.width = self.WIDTH
        self.height = self.HEIGHT
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
        self.x += random.uniform(-self.RANDOM_X, self.RANDOM_X)
        self.y += random.uniform(-self.RANDOM_Y, self.RANDOM_Y)
        self.vel_x += random.uniform(-self.RANDOM_VEL_X, self.RANDOM_VEL_X)
        self.vel_y += random.uniform(-self.RANDOM_VEL_Y, self.RANDOM_VEL_Y)

    def lerp_life(self):
        if self.life_time is None:
            return 1.0
        life = (self.death_time - Game.time) / self.life_time
        life = helpers.clamp(life, 0.0, 1.0)
        return life

    def draw(self):
        if Game.time < self.spawn_time:
            return
        life = self.lerp_life()
        alpha = self.COLOR[3]
        if self.LIFE_FADE:
            alpha *= life
        Draw.quad(self.x, self.y, self.WIDTH, self.HEIGHT, self.Z,
                  (self.COLOR[0], self.COLOR[1], self.COLOR[2], alpha))

    def update(self, dt):
        if Game.time < self.spawn_time:
            return
        if self.death_time is not None and Game.time > self.death_time:
            Game.remove(self)
            return
        return Actor.update(self, dt)


class Arrow(Particle):

    BOUNCE_AMOUNT = 10
    BOUNCE_SPEED = 2
    COLOR = (1, 1, 1, 0.5)
    LIFE_TIME = None
    LINE_WIDTH = 1.5
    PHYSICS = defs.PHYSICS_NONE
    WIDTH = 16
    HEIGHT = 16
    Z = defs.Z_PARTICLE_BACKGROUND

    def draw(self):
        if Game.time < self.spawn_time:
            return
        Draw.callback(self.draw_callback, z=self.Z)

    def draw_callback(self, z):
        x, y = self.x, self.y
        w, h = self.WIDTH, self.HEIGHT
        hh = h * 0.5
        f = (math.sin(Game.time * self.BOUNCE_SPEED) + 1) * 0.5
        f = f * f * f
        x += f * self.BOUNCE_AMOUNT
        gl.glLineWidth(self.LINE_WIDTH)
        gl.glBegin(gl.GL_LINE_STRIP)
        gl.glColor4f(*self.COLOR)
        gl.glVertex3f(x - w, y - hh, z)
        gl.glVertex3f(x - w, y + hh, z)
        gl.glVertex3f(x, y + hh, z)
        gl.glVertex3f(x, y + h, z)
        gl.glVertex3f(x + w, y, z)
        gl.glVertex3f(x, y - h, z)
        gl.glVertex3f(x, y - hh, z)
        gl.glVertex3f(x - w, y - hh, z)
        gl.glEnd()


class JetpackFlame(Particle):

    COLOR = (1.0, 1.0, 0.0, 1.0)
    GRAVITY = 0.1
    LIFE_TIME = 0.2
    RANDOM_X = RANDOM_Y = 1.0
    WIDTH = 2
    HEIGHT = 2
    Z = defs.Z_PARTICLE_BACKGROUND + defs.Z_LAYER_RANGE


class JetpackSmoke(Particle):

    COLOR = (0.0, 0.0, 0.0, 0.3)
    GRAVITY = 0.2
    RANDOM_X = RANDOM_Y = 2
    WIDTH = 2
    HEIGHT = 2


class JetpackIgniteSmoke(JetpackSmoke):

    COLLIDE_WITH_WORLD = False
    RANDOM_X = RANDOM_Y = 3
    WIDTH = 2
    HEIGHT = 2


class RocketFlame(Particle):

    COLOR = (1.0, 1.0, 0.0, 1.0)
    GRAVITY = 0.1
    LIFE_TIME = 0.2
    RANDOM_X = RANDOM_Y = 8
    WIDTH = HEIGHT = 4
    Z = defs.Z_PARTICLE_BACKGROUND + defs.Z_LAYER_RANGE


class RocketFlameOrange(RocketFlame):

    COLOR = (1.0, 0.6, 0.0, 1.0)
    RANDOM_X = 12
    WIDTH = HEIGHT = 6


class RocketFlameRed(RocketFlame):

    COLOR = (1.0, 0.0, 0.0, 1.0)
    RANDOM_X = 16
    WIDTH = HEIGHT = 8


class RocketSmoke(Particle):

    COLOR = (0.0, 0.0, 0.0, 0.3)
    LIFE_TIME = 2
    GRAVITY = 0.2
    RANDOM_X = RANDOM_Y = 10
    RANDOM_VEL_X = 128
    WIDTH = 16
    HEIGHT = 16


class RocketIgniteSmoke(JetpackSmoke):

    COLLIDE_WITH_WORLD = True
    RANDOM_X = 64
    RANDOM_Y = 8
    WIDTH = 16
    HEIGHT = 16


class Text(Particle):

    GRAVITY = 0
    LIFE_TIME = 2.0

    def __init__(self, text, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.label = Draw.create_label(6)
        self.label.text = text

    def draw(self):
        if Game.time < self.spawn_time:
            return
        life = self.lerp_life()
        life *= life / 1.0
        self.label.color = [255, 255, 255, int(255.0 * life)]
        x = self.x
        if self.anchor:
            x += self.anchor.WIDTH + 5
        Draw.label(self.label, x, self.y)


class TurretBullet(Particle):

    COLLIDE_WITH_ACTORS = [defs.CELL_HUMAN_PLAYER, defs.CELL_HUMAN_CIVILIAN]
    COLLIDE_WITH_WORLD = True
    COLOR = (1, 0, 1, 1)
    BOLT_LENGTH = 6
    BOLT_WIDTH = 3
    DAMAGE_ON_COLLIDE = True
    DRAG = 1
    GRAVITY = 0
    LIFE_FADE = False
    LIFE_TIME = 10.0
    REMOVE_ON_COLLIDE = True
    WIDTH = 5
    HEIGHT = 5

    def draw(self):
        if Game.time < self.spawn_time:
            return
        nx = self.vel_x
        ny = self.vel_y
        length = math.sqrt(nx*nx + ny*ny)
        if length:
            nx /= length
            ny /= length
            Draw.callback(self.draw_callback, nx, ny, z=self.Z)

    def draw_callback(self, nx, ny, z):
        gl.glLineWidth(self.BOLT_WIDTH)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4f(self.COLOR[0], self.COLOR[1], self.COLOR[2], 1)
        gl.glVertex3f(self.x, self.y, z)
        gl.glColor4f(self.COLOR[0] * 0.7, self.COLOR[1] * 0.7,
                     self.COLOR[2] * 0.7, 0)
        gl.glVertex3f(self.x + nx * self.BOLT_LENGTH,
                      self.y + ny * self.BOLT_LENGTH, z)
        gl.glColor3f(1, 1, 1)
        gl.glEnd()

    def on_remove(self):
        for i in range(20):
            Game.spawn(JetpackIgniteSmoke(self.x, self.y))
