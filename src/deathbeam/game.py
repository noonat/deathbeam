from __future__ import absolute_import
import time

import pyglet
from pyglet import gl
from pyglet.window.key import C, ENTER, SPACE

from . import defs, helpers, worlds
from .actors import iter_registered_actors
from .draw import Draw
from .effects import iter_registered_effects
from .particles import Arrow, Particle
from .score import Score
from .sounds import AmbientSound


class Game(object):

    window = None

    def __init__(self):
        # window
        if not self.window:
            pyglet.font.add_file(defs.FONT_FILE)
            self.keys = pyglet.window.key.KeyStateHandler()
            if defs.WINDOW_FULLSCREEN:
                self.window = pyglet.window.Window(
                    fullscreen=defs.WINDOW_FULLSCREEN,
                    vsync=defs.WINDOW_VSYNC)
                defs.WINDOW_SCALE[0] *= self.window.width / defs.WINDOW_WIDTH
                defs.WINDOW_SCALE[1] *= self.window.height / defs.WINDOW_HEIGHT
            else:
                self.window = pyglet.window.Window(vsync=defs.WINDOW_VSYNC,
                                                   width=defs.WINDOW_WIDTH,
                                                   height=defs.WINDOW_HEIGHT)
            self.window.push_handlers(self.on_close)
            self.window.push_handlers(self.on_draw)
            self.window.push_handlers(self.on_key_press)
            self.window.push_handlers(self.on_key_release)
            self.window.push_handlers(self.keys)
            pyglet.clock.schedule(self.on_update, 1.0 / 60)

        # gl
        gl.glClearColor(0.6, 0.5, 0.7, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # game
        self.draw = Draw(self)
        self.score = Score(self)

        AmbientSound.stop_all()
        self.actors = []
        self.actors_by_type = {}
        self.camera_x = 0
        self.camera_y = 0
        self.camera_target = None
        self.camera_width = self.window.width / defs.WINDOW_SCALE[0]
        self.camera_height = self.window.height / defs.WINDOW_SCALE[1]
        self.dt = 0
        self.fps_label = pyglet.clock.ClockDisplay()
        self.effects = []
        self.game_lost = False
        self.game_over = False
        self.loaded = False
        self.mothership = None
        self.particles = []
        self.player = None
        self.time = 0
        self.load()

    def get_world(self):
        return self.world

    def load(self):
        if self.loaded:
            return
        print 'loading'

        for cls in iter_registered_effects():
            self.effects.append(cls)

        # Load the world, and spawn all the actors in it
        self.world = worlds.load(self, 'tiles')
        self.world.load_map('test_map_horiz')
        for cls in iter_registered_actors():
            cell_type = cls.CELL_TYPE
            if cell_type:
                for cell in self.world.map.get_for_type(cell_type):
                    self.spawn(cls, x=cell.x, y=cell.y)

        self.player = self.actors_by_type[defs.CELL_HUMAN_PLAYER][0]
        self.mothership = self.actors_by_type[defs.CELL_ALIEN_MOTHERSHIP][0]

        # Create an arrow pointing to the right, above the player's start point
        self.spawn(Arrow, self.player.x, self.player.y + 100)

        # Create an arrow pointing toward the rocket, at the end
        rocket = self.actors_by_type[defs.CELL_HUMAN_ROCKET][0]
        self.spawn(Arrow, rocket.x - 35, rocket.y - 15)

        self.loaded = True

    def on_close(self):
        print self.time

    def on_draw(self):
        self.window.clear()

        if self.camera_target is None:
            self.camera_target = self.player
        self.camera_x = self.camera_target.x - self.camera_width / 2
        self.camera_y = self.camera_target.y - self.camera_height / 2
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_y < 0:
            self.camera_y = 0
        if self.camera_y > 800:
            self.camera_y = 800

        if not self.game_over:
            if (self.player.has_rocket and
                    self.player.y > 900 + self.camera_height):
                self.game_over = True
                self.game_lost = False
            if self.player.y < 0 or self.player.x < self.mothership.x:
                self.game_over = True
                self.game_lost = True
            self.on_game_over()

        if not self.game_over:
            for effect in self.effects:
                effect.pre_draw(self)
            self.world.map.draw()
            for actor in self.actors:
                actor.draw()
            for particle in self.particles:
                particle.draw()
            for effect in self.effects:
                effect.post_draw(self)

        self.draw.flush()

        self.window.invalid = False

    def on_game_over(self):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == C:
            self.screenshot()
        elif symbol == ENTER:
            self.__init__()

    def on_key_release(self, symbol, modifiers):
        if symbol == SPACE:
            self.player.space_pressed = False

    def on_update(self, dt, interval):
        self.window.invalid = True
        if self.game_over:
            return
        self.time += dt
        self.dt += dt
        while self.dt >= 0.015:
            self.dt -= 0.015
            for actor in self.actors:
                actor.update(0.015)
            for particle in self.particles:
                particle.update(0.015)
        AmbientSound.update_all()

    def remove(self, actor):
        actor.on_remove()
        if isinstance(actor, Particle):
            helpers.remove(self.particles, actor)
        else:
            helpers.remove(self.actors, actor)
            helpers.remove(self.actors_by_type[actor.CELL_TYPE], actor)
        del actor

    def screenshot(self):
        filename = 'screenshot_%d.png' % time.time()
        print 'writing screenshot to', filename
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)

    def spawn(self, actor_cls, *args, **kwargs):
        actor = actor_cls(self, *args, **kwargs)
        if isinstance(actor, Particle):
            self.particles.append(actor)
        else:
            self.actors.append(actor)
            if actor.CELL_TYPE not in self.actors_by_type:
                self.actors_by_type[actor.CELL_TYPE] = []
            self.actors_by_type[actor.CELL_TYPE].append(actor)
        return actor
