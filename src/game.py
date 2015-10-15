import time

import pyglet
from pyglet import gl
from pyglet.window.key import C, ENTER, SPACE

import defs
import helpers


class Draw(object):

    @classmethod
    def __init__(self):
        self.callbacks = {}
        self.labels = []
        self.quads = {}

    @classmethod
    def create_label(self, size=12, x=0.0, y=0.0, text='', **kwargs):
        return pyglet.text.Label(text, font_name=defs.FONT, font_size=size,
                                 x=x, y=y)

    @classmethod
    def flush(self):
        gl.glPushMatrix()
        gl.glScalef(defs.WINDOW_SCALE[0], defs.WINDOW_SCALE[1], 1)
        gl.glTranslatef(-Game.camera_x, -Game.camera_y, 0)
        # draw quads
        keys = list(set(self.callbacks.keys() + self.quads.keys()))
        keys.sort()
        for k in keys:
            gl.glBegin(gl.GL_QUADS)
            quads = self.quads.get(k)
            if quads:
                for x, y, w, h, z, c1, c2, c3, c4, bf in quads:
                    if bf:
                        gl.glEnd()
                        gl.glBlendFunc(bf[0], bf[1])
                        gl.glBegin(gl.GL_QUADS)
                    if c1:
                        gl.glColor4f(c1[0], c1[1], c1[2], c1[3])
                    gl.glVertex3f(x, y + h, z)
                    if c2:
                        gl.glColor4f(c2[0], c2[1], c2[2], c2[3])
                    gl.glVertex3f(x + w, y + h, z)
                    if c3:
                        gl.glColor4f(c3[0], c3[1], c3[2], c3[3])
                    gl.glVertex3f(x + w, y, z)
                    if c4:
                        gl.glColor4f(c4[0], c4[1], c4[2], c4[3])
                    gl.glVertex3f(x, y, z)
                    if c1 or c2 or c3 or c4:
                        gl.glColor3f(1, 1, 1)
                    if bf:
                        gl.glEnd()
                        gl.glBlendFunc(gl.GL_SRC_ALPHA,
                                       gl.GL_ONE_MINUS_SRC_ALPHA)
                        gl.glBegin(gl.GL_QUADS)
            gl.glEnd()
            callbacks = self.callbacks.get(k)
            if callbacks:
                for callback, args, kwargs in callbacks:
                    callback(*args, **kwargs)
        gl.glPopMatrix()
        self.callbacks = {}
        self.quads = {}
        self.flush_labels()

    @classmethod
    def flush_labels(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glPushMatrix()
        gl.glTranslatef(-Game.camera_x * defs.WINDOW_SCALE[0],
                        -Game.camera_y * defs.WINDOW_SCALE[1], 0)
        for label, x, y, scale in self.labels:
            if scale:
                gl.glPushMatrix()
                label.anchor_x = 'center'
                label.anchor_y = 'center'
                gl.glTranslatef(x * defs.WINDOW_SCALE[0],
                                y * defs.WINDOW_SCALE[1], 0)
                gl.glScalef(*scale)
                label.x = label.y = 0
                label.draw()
                gl.glPopMatrix()
            else:
                label.x = x * defs.WINDOW_SCALE[0]
                label.y = y * defs.WINDOW_SCALE[1]
                label.draw()
        self.labels = []
        gl.glColor3f(1, 1, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glPopMatrix()
        # self.fps_label.draw()
        Score.draw()

    @classmethod
    def callback(self, callback, *args, **kwargs):
        if kwargs['z'] not in self.callbacks:
            self.callbacks[kwargs['z']] = []
        self.callbacks[kwargs['z']].append((callback, args, kwargs))

    @classmethod
    def label(self, label, x, y, scale=None):
        self.labels.append((label, x, y, scale))

    @classmethod
    def quad(self, x, y, w, h, z, c1=None, c2=None, c3=None, c4=None, bf=None):
        if z not in self.quads:
            self.quads[z] = []
        self.quads[z].append((x, y, w, h, z, c1, c2, c3, c4, bf))


class Game(object):

    window = None

    @classmethod
    def run(self):
        self.__init__()
        pyglet.app.run()

    @classmethod
    def __init__(self):
        from actors import AmbientSound

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
        Draw.__init__()
        Score.__init__()

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

    @classmethod
    def get_world(self):
        return self.world

    @classmethod
    def load(self):
        if self.loaded:
            return
        print 'loading'

        # These modules need to be imported because they register things
        # that we need to load the world.
        import tiles   # noqa
        import aliens  # noqa
        import humans  # noqa

        import worlds
        from actors import iter_registered_actors
        from effects import iter_registered_effects
        from particles import Arrow

        for cls in iter_registered_effects():
            self.effects.append(cls)

        # Load the world, and spawn all the actors in it
        self.world = worlds.load('tiles')
        self.world.load_map('test_map_horiz')
        for cls in iter_registered_actors():
            cell_type = cls.CELL_TYPE
            if cell_type:
                for cell in self.world.map.get_for_type(cell_type):
                    self.spawn(cls(x=cell.x, y=cell.y))

        self.player = self.actors_by_type[defs.CELL_HUMAN_PLAYER][0]
        self.mothership = self.actors_by_type[defs.CELL_ALIEN_MOTHERSHIP][0]

        # Create an arrow pointing to the right, above the player's start point
        self.spawn(Arrow(self.player.x, self.player.y + 100))

        # Create an arrow pointing up, at the ending of the level
        rocket = self.actors_by_type[defs.CELL_HUMAN_ROCKET][0]
        self.spawn(Arrow(rocket.x - 35, rocket.y - 15))

        self.loaded = True

    @classmethod
    def on_close(self):
        print self.time

    @classmethod
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
                effect.pre_draw()
            self.world.map.draw()
            for actor in self.actors:
                actor.draw()
            for particle in self.particles:
                particle.draw()
            for effect in self.effects:
                effect.post_draw()

        Draw.flush()

        self.window.invalid = False

    @classmethod
    def on_game_over(self):
        pass

    @classmethod
    def on_key_press(self, symbol, modifiers):
        if symbol == C:
            self.screenshot()
        elif symbol == ENTER:
            self.__init__()

    @classmethod
    def on_key_release(self, symbol, modifiers):
        if symbol == SPACE:
            self.player.space_pressed = False

    @classmethod
    def on_update(self, dt, interval):
        from actors import AmbientSound

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

    @classmethod
    def remove(self, actor):
        from particles import Particle

        actor.on_remove()
        if isinstance(actor, Particle):
            helpers.remove(self.particles, actor)
        else:
            helpers.remove(self.actors, actor)
            helpers.remove(self.actors_by_type[actor.CELL_TYPE], actor)
        del actor

    @classmethod
    def screenshot(self):
        filename = 'screenshot_%d.png' % time.time()
        print 'writing screenshot to', filename
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)

    @classmethod
    def spawn(self, actor):
        from particles import Particle

        if isinstance(actor, Particle):
            self.particles.append(actor)
        else:
            self.actors.append(actor)
            if actor.CELL_TYPE not in self.actors_by_type:
                self.actors_by_type[actor.CELL_TYPE] = []
            self.actors_by_type[actor.CELL_TYPE].append(actor)
        return actor


class Score(object):

    HUMANS_LOST = 'humans_lost'
    HUMANS_SAVED = 'humans_saved'
    POINTS = 'points'
    VALUES = {
        HUMANS_LOST: {
            'text': 'HUMANS LOST: %d',
            'size': 6, 'x': defs.WINDOW_WIDTH - 130, 'y': 10},
        HUMANS_SAVED: {
            'text': 'HUMANS SAVED: %d',
            'size': 6, 'x': defs.WINDOW_WIDTH - 138, 'y': 25},
        POINTS: {
            'text': 'SCORE %d',
            'size': 10, 'x': 10, 'y': 10},
        }

    @classmethod
    def __init__(self):
        self.you_win = Draw.create_label(size=32, text='YOU WIN!',
                                         x=defs.WINDOW_WIDTH*0.5,
                                         y=defs.WINDOW_HEIGHT*0.5)
        self.you_win.anchor_x = 'center'
        self.you_win.anchor_y = 'center'
        self.you_died = Draw.create_label(size=32, text='YOU DIED :(',
                                          x=defs.WINDOW_WIDTH*0.5,
                                          y=defs.WINDOW_HEIGHT*0.5 + 50)
        self.you_died.color = (0, 0, 0, 255)
        self.you_died.anchor_x = 'center'
        self.you_died.anchor_y = 'center'
        self.you_died2 = Draw.create_label(size=16,
                                           text='press enter to try again',
                                           x=defs.WINDOW_WIDTH*0.5,
                                           y=defs.WINDOW_HEIGHT*0.5 - 50)
        self.you_died2.color = (0, 0, 0, 255)
        self.you_died2.anchor_x = 'center'
        self.you_died2.anchor_y = 'center'
        self.died = False
        self.reset()

    @classmethod
    def add(self, name, value, why=None):
        if name == 'points':
            text = '+%d' % value
            if why:
                text = why + ' ' + text
            Game.player.attach_text(text)
        self.set(name, self.get(name) + value)

    @classmethod
    def get(self, name):
        if not hasattr(self, name):
            return 0
        return getattr(self, name)

    @classmethod
    def set(self, name, value):
        setattr(self, name, value)
        label = name + '_label'
        if not hasattr(self, label):
            setattr(self, label, Draw.create_label(**self.VALUES[name]))
            label = getattr(self, label)
        else:
            label = getattr(self, label)
        label.text = self.VALUES[name]['text'] % value
        return value

    @classmethod
    def draw(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        if Game.game_over:
            if Game.game_lost:
                gl.glBegin(gl.GL_QUADS)
                gl.glColor3f(1, 1, 1)
                gl.glVertex3f(0, 0, -0.9)
                gl.glVertex3f(0, defs.WINDOW_HEIGHT, -0.9)
                gl.glVertex3f(defs.WINDOW_WIDTH, defs.WINDOW_HEIGHT, -0.9)
                gl.glVertex3f(defs.WINDOW_WIDTH, 0, -0.9)
                gl.glEnd()
                self.you_died.draw()
                self.you_died2.draw()
                if not self.died:
                    for name in self.VALUES:
                        getattr(self, name + '_label').color = (0, 0, 0, 255)
                self.died = True
            else:
                gl.glBegin(gl.GL_QUADS)
                gl.glColor3f(0, 0, 0)
                gl.glVertex3f(0, 0, -0.9)
                gl.glVertex3f(0, defs.WINDOW_HEIGHT, -0.9)
                gl.glVertex3f(defs.WINDOW_WIDTH, defs.WINDOW_HEIGHT, -0.9)
                gl.glVertex3f(defs.WINDOW_WIDTH, 0, -0.9)
                gl.glEnd()
                self.you_win.draw()
        for name in self.VALUES:
            getattr(self, name + '_label').draw()

    @classmethod
    def reset(self):
        for name in self.VALUES:
            self.set(name, 0)
            getattr(self, name + '_label').color = (255, 255, 255, 255)
