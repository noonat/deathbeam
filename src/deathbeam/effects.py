from __future__ import absolute_import
import random

from pyglet.gl import GL_SRC_ALPHA, GL_DST_COLOR

from . import defs


_effect_classes = []


def iter_registered_effects():
    for cls in _effect_classes:
        yield cls


def register_effect(cls):
    _effect_classes.append(cls)
    return cls


class Effect(object):

    @classmethod
    def pre_draw(self, game):
        pass

    @classmethod
    def post_draw(self, game):
        pass


@register_effect
class Mothership(Effect):

    DISTANCE = 320
    SHAKE = 5

    @classmethod
    def pre_draw(self, game):
        self.f = 0.0
        if game.mothership:
            self.x = abs(game.player.x - game.mothership.x)
            if self.x < self.DISTANCE:
                self.f = 1.0 - (self.x / self.DISTANCE)
                self.f *= self.f
                game.camera_x += (
                    random.uniform(-self.SHAKE, self.SHAKE) * self.f)
                game.camera_y += (
                    random.uniform(-self.SHAKE, self.SHAKE) * self.f)

    @classmethod
    def post_draw(self, game):
        game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                       game.camera_height, z=defs.Z_OVERLAY,
                       c1=(1, 1, 1, self.f * self.f),
                       bf=(GL_SRC_ALPHA, GL_DST_COLOR))


@register_effect
class Space(Effect):

    ATMOSPHERE = (256, 720)
    SPACE = (720, 960)

    @classmethod
    def lerp_for_y(self, game, min_y, max_y):
        f = game.player.y * 1.0 - min_y
        if f > 0:
            f /= max_y - min_y
            if f > 1.0:
                f = 1.0
            return f
        else:
            return 0

    @classmethod
    def pre_draw(self, game):
        f = self.lerp_for_y(game, *self.ATMOSPHERE)
        if f:
            game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                           game.camera_height, z=-0.99, c1=(0, 0, 0, f),
                           c3=(0, 0, 0, 0))
        f = self.lerp_for_y(game, *self.SPACE)
        if f:
            game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                           game.camera_height, z=-0.98, c1=(0, 0, 0, f))
