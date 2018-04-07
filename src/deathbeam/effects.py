from __future__ import absolute_import
import random

from pyglet.gl import GL_SRC_ALPHA, GL_DST_COLOR

from . import defs


_effect_classes = []


def iter_registered_effects():
    """Iterate over all of the registered effects."""
    for cls in _effect_classes:
        yield cls


def register_effect(effect_cls):
    """Add an effect to the effects applied by the game.

    :param Effect effect_cls: An subclass of effect.
    """
    _effect_classes.append(effect_cls)
    return effect_cls


class Effect(object):

    @classmethod
    def pre_draw(cls, game):
        pass

    @classmethod
    def post_draw(cls, game):
        pass


@register_effect
class Mothership(Effect):

    """Mothership handles shaking and whiting out when near the beam."""

    DISTANCE = 320
    SHAKE = 5

    @classmethod
    def pre_draw(cls, game):
        cls.f = 0.0
        if not game.mothership:
            # Mothership isn't active.
            return
        cls.x = abs(game.player.x - game.mothership.x)
        if cls.x >= cls.DISTANCE:
            # The mothership is too far away to show an effect.
            return
        cls.f = 1.0 - (cls.x / cls.DISTANCE)
        cls.f *= cls.f
        game.camera_x += (
            random.uniform(-cls.SHAKE, cls.SHAKE) * cls.f)
        game.camera_y += (
            random.uniform(-cls.SHAKE, cls.SHAKE) * cls.f)

    @classmethod
    def post_draw(cls, game):
        game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                       game.camera_height, z=defs.Z_OVERLAY,
                       c1=(1, 1, 1, cls.f * cls.f),
                       bf=(GL_SRC_ALPHA, GL_DST_COLOR))


@register_effect
class Space(Effect):

    """Space handles drawing the gradient for the sky."""

    ATMOSPHERE = (256, 720)
    SPACE = (720, 960)

    @classmethod
    def lerp_for_y(cls, game, min_y, max_y):
        f = game.player.y * 1.0 - min_y
        if f <= 0:
            return 0
        f /= max_y - min_y
        if f > 1.0:
            f = 1.0
        return f

    @classmethod
    def pre_draw(cls, game):
        f = cls.lerp_for_y(game, *cls.ATMOSPHERE)
        if f:
            game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                           game.camera_height, z=-0.99, c1=(0, 0, 0, f),
                           c3=(0, 0, 0, 0))
        f = cls.lerp_for_y(game, *cls.SPACE)
        if f:
            game.draw.quad(game.camera_x, game.camera_y, game.camera_width,
                           game.camera_height, z=-0.98, c1=(0, 0, 0, f))
