from __future__ import absolute_import
import math

import pyglet

from . import defs, helpers


_actor_classes = []


def iter_registered_actors():
    for cls in _actor_classes:
        yield cls


def register_actor(cls):
    _actor_classes.append(cls)
    return cls


class Actor(object):

    ATTACHED_DISTANCE = 4
    CELL_TYPE = None
    COLLIDE_WITH_ACTORS = True
    COLLIDE_WITH_WORLD = True
    COLOR = (1, 1, 1, 1)
    DAMAGE = 0.0
    DAMAGE_ON_COLLIDE = False
    DRAG = 0.9
    GRAVITY = 1.5
    MAX_VELOCITY_X = 64
    MAX_VELOCITY_Y = 384
    PHYSICS = defs.PHYSICS_VELOCITY
    REMOVE_ON_COLLIDE = False
    WIDTH = 3
    HEIGHT = 3
    Z = defs.Z_ACTOR_BACKGROUND

    def __init__(self, game, x=0.0, y=0.0, image=None):
        self.game = game
        self.x = x
        self.y = y
        self.old_x = x
        self.old_y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.anchor = None
        self.cell = None
        self.image = image
        self.on_ground = False

    def attach(self, actor):
        if self.anchor:
            if self.anchor is actor:
                return
            self.detach()
        self.anchor = actor
        self.anchor.on_attached(self)
        self._old_physics = self.PHYSICS
        self.PHYSICS = defs.PHYSICS_ATTACHED

    def attach_text(self, text):
        from .particles import Text  # imported here for circular dependencies

        text = self.game.spawn(Text, text)
        text.attach(self)
        return text

    def detach(self):
        if not self.anchor:
            return
        self.anchor.on_detached(self)
        self.anchor = None
        self.PHYSICS = self._old_physics
        self._old_physics = None

    def _collide_with_actors(self):
        if isinstance(self.COLLIDE_WITH_ACTORS, list):
            for cell_type in self.COLLIDE_WITH_ACTORS:
                if cell_type not in self.game.actors_by_type:
                    continue
                for actor in self.game.actors_by_type[cell_type]:
                    if actor is self:
                        continue
                    if not actor.COLLIDE_WITH_ACTORS:
                        continue
                    if (self.x > actor.x + actor.WIDTH or
                            self.x + self.WIDTH < actor.x):
                        continue
                    if (self.y > actor.y + actor.HEIGHT or
                            self.y + self.HEIGHT < actor.y):
                        continue
                    if (isinstance(actor.COLLIDE_WITH_ACTORS, list) and
                            self.CELL_TYPE not in actor.COLLIDE_WITH_ACTORS):
                        continue
                    self.on_collide(actor, True)
                    actor.on_collide(self, True)
        else:
            for actor in self.game.actors:
                if actor is self:
                    continue
                if not actor.COLLIDE_WITH_ACTORS:
                    continue
                if (self.x > actor.x + actor.WIDTH or
                        self.x + self.WIDTH < actor.x):
                    continue
                if (self.y > actor.y + actor.HEIGHT or
                        self.y + self.HEIGHT < actor.y):
                    continue
                if (isinstance(actor.COLLIDE_WITH_ACTORS, list) and
                        self.CELL_TYPE not in actor.COLLIDE_WITH_ACTORS):
                    continue
                self.on_collide(actor, True)
                actor.on_collide(self, True)

    def _collide_with_world(self):
        self.x, self.y, hit_1, hit_ground_1, cell = self.game.world.map.trace(
            self.old_x, self.old_y, self.x, self.y)
        self.x, self.y, hit_2, hit_ground_2, cell = self.game.world.map.trace(
            self.old_x, self.old_y, self.x, self.y)
        if not self.on_ground and (hit_ground_1 or hit_ground_2):
            self.on_ground = True
        cell = self.game.world.map.get_for_xy(self.x, self.y)
        if self.cell is not cell:
            self.cell = cell
            if cell and cell.type:
                self.on_cell(cell)
        if hit_1 or hit_2:
            if self.REMOVE_ON_COLLIDE:
                self.game.remove(self)

    def draw(self):
        x = self.x
        y = self.y
        self.game.draw.quad(x, y, self.WIDTH, self.HEIGHT, self.Z, self.COLOR)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        if isinstance(new_image, str) or isinstance(new_image, unicode):
            new_image = pyglet.image.load(new_image)
            helpers.set_nearest(new_image)
        self._image = new_image
        if self._image:
            helpers.set_anchor(self._image, 0.5, 0.0)
        return self._image

    @image.deleter
    def image(self):
        del self._image

    def on_attached(self, actor):
        pass

    def on_cell(self, cell):
        pass

    def on_collide(self, actor, collision):
        if actor.DAMAGE_ON_COLLIDE:
            self.on_damage(actor)
        if self.REMOVE_ON_COLLIDE:
            self.game.remove(self)

    def on_damage(self, inflictor):
        pass

    def on_detached(self, actor):
        pass

    def on_remove(self):
        pass

    def push(self, x, y):
        self.vel_x = helpers.abs_clamp(self.vel_x + x, self.MAX_VELOCITY_X)
        self.vel_y = helpers.abs_clamp(self.vel_y + y, self.MAX_VELOCITY_Y)
        if self.vel_y > 0:
            self.on_ground = False

    def update(self, dt):
        if self.vel_y > 0:
            self.on_ground = False
        # physics
        if self.PHYSICS == defs.PHYSICS_VELOCITY:
            self._update_velocity(dt)
        elif self.PHYSICS == defs.PHYSICS_ATTACHED:
            self._update_attached(dt)
        # collision
        if self.x != self.old_x or self.y != self.old_y:
            if self.COLLIDE_WITH_WORLD:
                self._collide_with_world()
            if self.COLLIDE_WITH_ACTORS:
                self._collide_with_actors()
        # attachment physics need correction after collision
        if self.PHYSICS == defs.PHYSICS_ATTACHED:
            self._update_attached_distance(dt)
        self.old_x = self.x
        self.old_y = self.y

    def _update_attached(self, dt):
        if self.anchor:
            self.y -= self.GRAVITY * 0.5

    def _update_attached_distance(self, dt):
        if self.anchor:
            dx = self.anchor.x - self.x
            dy = self.anchor.y - self.y
            length = math.sqrt(dx*dx + dy*dy)
            if length > self.ATTACHED_DISTANCE:
                dx /= length
                dy /= length
                self.x += dx * (length - self.ATTACHED_DISTANCE)
                self.y += dy * (length - self.ATTACHED_DISTANCE)

    def _update_velocity(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.y -= self.GRAVITY
        self.vel_x *= self.DRAG
        self.vel_y *= self.DRAG
        if abs(self.vel_x) < 0.001:
            self.vel_x = 0
        if abs(self.vel_y) < 0.001:
            self.vel_y = 0
