import random
from pyglet.gl import *

from game import Game, Draw
import defs

class Effect(object):
    @classmethod
    def pre_draw(self):
        pass
    
    @classmethod
    def post_draw(self):
        pass
        
class Mothership(Effect):
    DISTANCE = 320
    SHAKE = 5
    
    @classmethod
    def pre_draw(self):
        self.f = 0.0
        if Game.mothership:
            self.x = abs(Game.player.x - Game.mothership.x)
            if self.x < self.DISTANCE:
                self.f = 1.0 - (self.x / self.DISTANCE)
                self.f *= self.f
                Game.camera_x += random.uniform(-self.SHAKE, self.SHAKE) * self.f
                Game.camera_y += random.uniform(-self.SHAKE, self.SHAKE) * self.f

    @classmethod
    def post_draw(self):
        Draw.quad(Game.camera_x, Game.camera_y, Game.camera_width, Game.camera_height,
                  z=defs.Z_OVERLAY, c1=(1, 1, 1, self.f * self.f), bf=(GL_SRC_ALPHA, GL_DST_COLOR))

class Space(Effect):
    ATMOSPHERE = (256, 720)
    SPACE = (720, 960)
    
    @classmethod
    def lerp_for_y(self, min_y, max_y):
        f = Game.player.y * 1.0 - min_y
        if f > 0:
            f /= max_y - min_y
            if f > 1.0:
                f = 1.0
            return f
        else:
            return 0
    
    @classmethod
    def pre_draw(self):
        f = self.lerp_for_y(*self.ATMOSPHERE)
        if f:
            Draw.quad(Game.camera_x, Game.camera_y, Game.camera_width, Game.camera_height,
                      z=-0.99, c1=(0, 0, 0, f), c3=(0, 0, 0, 0))
        f = self.lerp_for_y(*self.SPACE)
        if f:
            Draw.quad(Game.camera_x, Game.camera_y, Game.camera_width, Game.camera_height,
                      z=-0.98, c1=(0, 0, 0, f))
