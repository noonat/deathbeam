from __future__ import absolute_import
import math
import random

import pyglet
from pyglet.window.key import LEFT, RIGHT, SPACE

from . import defs
from .actors import Actor, register_actor
from .aliens import Mothership
from .particles import (
    JetpackFlame, JetpackIgniteSmoke, JetpackSmoke, RocketFlame,
    RocketFlameOrange, RocketFlameRed, RocketSmoke, Text)
from .sounds import Sound


@register_actor
class Civilian(Actor):

    CELL_TYPE = defs.CELL_HUMAN_CIVILIAN
    COLLIDE_WITH_ACTORS = [defs.CELL_HUMAN_PLAYER]
    COLOR = (0, 1, 1, 1)
    COLOR_RESCUED = (1, 1, 0.5, 1)
    DEATH_TEXT = defs.TEXT_CIVILIAN_DEATHS
    NAME = 'Civilian'
    OFFSET_X = 2
    OFFSET_Y = 2
    POINTS = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead = False
        self.offset = None
        self.platform = None
        self.player = None

    def attach(self, anchor):
        super().attach(anchor)
        self.COLLIDE_WITH_ACTORS = True
        if isinstance(anchor, Player):
            self.player = anchor
            self.game.score.add('points', self.POINTS / 10,
                                why=self.NAME.upper())

    def detach(self):
        super().detach()
        if self.player:
            self.player.on_detached(self)
            self.player = None
        self.COLLIDE_WITH_ACTORS = Civilian.COLLIDE_WITH_ACTORS
        self.GRAVITY = Civilian.GRAVITY

    def on_cell(self, cell):
        if cell.type == defs.CELL_HUMAN_RESCUE:
            self.detach()
            self.COLOR = self.COLOR_RESCUED
            self.COLLIDE_WITH_ACTORS = False
            cell['platform'].rescue(self)

    def on_collide(self, actor, collision):
        if not self.anchor and isinstance(actor, Player):
            self.attach(actor)
        else:
            return super().on_collide(actor, collision)

    def on_damage(self, actor):
        if self.player or isinstance(actor, Mothership):
            Sound(self, 'civilian_death.wav', volume=0.5).play()
            self.detach()
            self.COLLIDE_WITH_ACTORS = False
            self.COLOR = (0, 0, 0, 1)
            self.dead = True
            self.game.score.add(self.game.score.HUMANS_LOST, 1)
            text = self.game.spawn(Text, random.choice(self.DEATH_TEXT))
            text.attach(self)

    def update(self, dt):
        if self.x < self.game.mothership.x and not self.dead:
            self.on_damage(self.game.mothership)
        super().update(dt)
        if self.platform:
            # FIXME: need to clamp to right side as well ... keep them on it
            if self.x < self.platform.x:
                self.x = self.platform.x
            if self.y < self.platform.y:
                self.y = self.platform.y


@register_actor
class CivilianCommander(Civilian):

    CELL_TYPE = defs.CELL_HUMAN_COMMANDER
    COLOR = (0, 0, 1, 1)
    NAME = 'Mr. President'
    POINTS = 1000


@register_actor
class CivilianScientist(Civilian):

    CELL_TYPE = defs.CELL_HUMAN_SCIENTIST
    COLOR = (0, 1, 0.2, 1)
    NAME = 'Scientist'
    POINTS = 250


@register_actor
class Player(Actor):

    CELL_TYPE = defs.CELL_HUMAN_PLAYER
    JETPACK_IGNITE_DELAY = 0.1
    JETPACK_IGNITE_PARTICLES = 35
    PUSH_JETPACK = 20
    PUSH_JUMP = 600
    PUSH_ROCKET = 60
    PUSH_WALK = 32
    PUSH_WALK_AIR = 64
    Z = defs.Z_PLAYER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.civilians = []
        self.jetpack_ignite_time = None
        self.jetpack_ignited = False
        self.space_pressed = False
        self.has_jetpack = True
        self.has_rocket = False
        if defs.SOUND:
            pyglet.media.listener.position = (self.x, self.y, 0)
            pyglet.media.listener.forward_orientation = (0, 0, 1)
            pyglet.media.listener.up_orientation = (0, 1, 0)

    def draw(self):
        if self.has_rocket:
            old_y = self.y
            self.y += Rocket.HEIGHT
        super().draw()
        if self.has_rocket:
            self.y = old_y

    def on_attached(self, actor):
        if isinstance(actor, Civilian):
            if len(self.civilians) > 0:
                actor.anchor = self.civilians[-1]
            self.civilians.append(actor)
            self.update_gravity()
        elif isinstance(actor, Rocket):
            self.has_rocket = True

    def on_detached(self, actor):
        if isinstance(actor, Civilian):
            try:
                i = self.civilians.index(actor)
            except ValueError:
                return
            del self.civilians[i]
            self.update_gravity()
            if len(self.civilians) > i:
                if i == 0:
                    self.civilians[0].anchor = self
                else:
                    self.civilians[i].anchor = self.civilians[i - 1]

    def on_jetpack_ignited(self):
        if self.has_rocket:
            flame_cls = RocketFlame
            smoke_cls = RocketSmoke
        else:
            flame_cls = JetpackFlame
            smoke_cls = JetpackIgniteSmoke
        self.game.spawn(flame_cls, self.x, self.y, self.game.time)
        for i in range(self.JETPACK_IGNITE_PARTICLES):
            p = self.game.spawn(smoke_cls, self.x, self.y, self.game.time)
            p.vel_x = random.uniform(-20, -60) * math.copysign(1, self.vel_x)
            p.vel_y = random.uniform(-20, -60)

    def update(self, dt):
        if (self.has_jetpack and not self.jetpack_ignited and
                self.jetpack_ignite_time):
            if self.jetpack_ignite_time <= self.game.time:
                self.jetpack_ignited = True
                self.on_jetpack_ignited()
        # figure out how hard to push
        push_x = push_y = 0
        if self.on_ground:
            push_x = self.PUSH_WALK
            if self.has_jetpack:
                push_y = self.PUSH_JETPACK
            elif not self.space_pressed:
                push_y = self.PUSH_JUMP
        else:
            push_x = self.PUSH_WALK_AIR
            if self.has_jetpack:
                if self.jetpack_ignited:
                    push_y = self.PUSH_JETPACK
        if self.has_rocket:
            push_y = self.PUSH_ROCKET
        # figure out where they want to go
        px, py = 0, 0
        if self.game.keys[RIGHT]:
            px += push_x
        if self.game.keys[LEFT]:
            px -= push_x
        if self.has_rocket:
            px = 0
        if self.game.keys[SPACE]:
            if self.has_jetpack and not self.jetpack_ignite_time:
                self.jetpack_ignite_time = (
                    self.game.time + self.JETPACK_IGNITE_DELAY)
            self.space_pressed = True
            py += push_y
        else:
            self.jetpack_ignited = False
            self.jetpack_ignite_time = None
        if self.jetpack_ignited:
            if self.has_rocket:
                flame_classes = [RocketFlame, RocketFlameOrange,
                                 RocketFlameRed]
                smoke_cls = RocketSmoke
            else:
                flame_classes = [JetpackFlame]
                smoke_cls = JetpackSmoke
            for i, flame_cls in enumerate(flame_classes):
                self.game.spawn(flame_cls, self.x, self.y,
                                self.game.time + 0.05 * i)
            self.game.spawn(smoke_cls, self.x, self.y, self.game.time + 0.1)
        # push em
        self.push(px, py)
        super().update(dt)
        if defs.SOUND:
            pyglet.media.listener.position = (self.x, self.y, 0)

    def update_gravity(self):
        self.GRAVITY = (Actor.GRAVITY +
                        Actor.GRAVITY * 0.1 * len(self.civilians))


@register_actor
class RescuePlatform(Actor):

    CELL_TYPE = defs.CELL_HUMAN_RESCUE
    COLOR = (0, 1, 1, 0.25)
    LABEL_Y = 25
    PHYSICS = defs.PHYSICS_NONE
    RESCUE_COLOR = (1, 1, 0.5, 0.25)
    RESCUE_COLOR_FADE = 0.2
    RESCUE_COLOR_FADE_SPEED = 20
    RESCUE_DELAY = 10.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rescue_actors = []
        self.rescue_time = None
        self.cell = self.game.world.map.get_for_xy(self.x, self.y)
        if self.cell['platform']:
            self.cell = None
            return
        self.cell['platform'] = self
        self.x = self.cell.x
        self.y = self.cell.y
        self.WIDTH = self.cell.width
        self.HEIGHT = self.cell.height
        # also be the platform for the cell to our right, if it's also a rescue
        # platform... hack since we don't have spawns for 2-wide cells
        c = self.cell.neighbors.right
        if c and c.type == defs.CELL_HUMAN_RESCUE:
            if c['platform']:
                self.game.remove(c.platform)
            c['platform'] = self
            self.cell2 = c
            self.WIDTH += self.cell2.width
        else:
            self.cell2 = None
        self.label = self.game.draw.create_label(6)
        self.label.anchor_x = 'center'
        self.activate_sound = Sound(self, 'rescue_platform_activate.wav')
        self.ping_sound = Sound(self, 'rescue_platform_ping.wav')
        self.next_ping_sound = 0
        self.teleport_sound = Sound(self, 'rescue_platform_teleport.wav')

    def draw(self):
        if not self.cell:
            return
        if self.rescue_time:
            r, g, b, a = self.RESCUE_COLOR
            a += (self.RESCUE_COLOR_FADE *
                  math.sin(self.game.time * self.RESCUE_COLOR_FADE_SPEED))
        else:
            r, g, b, a = self.COLOR
        self.game.draw.quad(self.x, self.y, self.WIDTH, self.HEIGHT, self.Z,
                            c1=(r, g, b, 0), c3=(r, g, b, a))
        if self.rescue_time:
            time = int(self.rescue_time - self.game.time)
            if time < 0:
                time = 0
            if time == 0:
                self.label.text = 'teleporting'
            else:
                self.label.text = 'teleporting in %d' % time
            self.game.draw.label(self.label, self.x + self.WIDTH * 0.5,
                                 self.y + self.LABEL_Y)

    def rescue(self, actor):
        self.rescue_actors.append(actor)
        if not self.rescue_time:
            self.rescue_time = self.game.time + self.RESCUE_DELAY
            self.activate_sound.play()
            self.next_ping_sound = self.game.time + 1.0

    def update(self, dt):
        if not self.cell:
            self.game.remove(self)
            return
        super().update(dt)
        if self.rescue_time:
            if self.rescue_time <= self.game.time:
                self.teleport_sound.play()
                a = [act for act in set(self.rescue_actors) if not act.dead]
                n = len(a)
                self.game.score.add(self.game.score.HUMANS_SAVED, n)
                points = 0
                for actor in a:
                    points += actor.POINTS
                    self.game.remove(actor)
                if n > 5:
                    points *= 100
                elif n > 3:
                    points *= 50
                elif n > 1:
                    points *= 10
                self.game.score.add(self.game.score.POINTS, points,
                                    '%dx RESCUE!' % n)
                self.rescue_time = None
            elif self.next_ping_sound <= self.game.time:
                self.ping_sound.play()
                self.next_ping_sound += 1.0


@register_actor
class Rocket(Actor):

    CELL_TYPE = defs.CELL_HUMAN_ROCKET
    COLOR = (0.8, 0.8, 0.8, 1.0)
    WIDTH = 32
    HEIGHT = 32

    def on_collide(self, actor, collision):
        if not self.anchor and isinstance(actor, Player):
            actor.old_x = actor.x = (self.x + self.WIDTH * 0.5 -
                                     actor.WIDTH * 0.5)
            actor.old_y = actor.y = self.y
            self.attach(actor)

    def update(self, dt):
        if self.anchor:
            self.x = self.anchor.x + self.anchor.WIDTH * 0.5 - self.WIDTH * 0.5
            self.y = self.anchor.y
        else:
            super().update(dt)


@register_actor
class RocketPad(Actor):

    CELL_TYPE = defs.CELL_HUMAN_ROCKET_PAD
    COLLIDE_WITH_ACTORS = False
    COLLIDE_WITH_WORLD = False
    COLOR = (0.2, 1, 0.0, 0.5)
    PHYSICS = defs.PHYSICS_NONE
    Z = defs.Z_MAP_BACKGROUND

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell = self.game.world.map.get_for_xy(self.x, self.y)
        if self.cell['pad']:
            self.cell = None
            return
        self.cell['pad'] = self
        self.x = self.cell.x
        self.y = self.cell.y
        self.WIDTH = self.cell.width
        self.HEIGHT = self.cell.height
        # also be the platform for the cell to our right, if it's also a rescue
        # platform... hack since we don't have spawns for 2-wide cells
        c = self.cell.neighbors.right
        if c and c.type == defs.CELL_HUMAN_ROCKET_PAD:
            if c['pad']:
                self.game.remove(c.platform)
            c['pad'] = self
            self.cell2 = c
            self.WIDTH += self.cell2.width
        else:
            self.cell2 = None

    def draw(self):
        if not self.cell:
            return
        f = (math.sin(self.game.time) + 1) * 0.5
        f = f * f
        r, g, b, a = self.COLOR
        self.game.draw.quad(self.x, self.y, self.WIDTH, self.HEIGHT, self.Z,
                            c1=(r, g, b, 0), c3=(r, g, b, 0.1 + 0.3 * f))

    def update(self, dt):
        if not self.cell:
            self.game.remove(self)
            return
        super().update(dt)
