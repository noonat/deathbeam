import math, random
import pyglet
from pyglet.gl import *
from pyglet.window import key

import defs, helpers

class Draw(object):
    @classmethod
    def __init__(self):
        self.callbacks = {}
        self.labels = []
        self.quads = {}

    @classmethod
    def create_label(self, size=12, x=0.0, y=0.0, text="", **kwargs):
        return pyglet.text.Label(text, font_name=defs.FONT, font_size=size, x=x, y=y)
    
    @classmethod
    def flush(self):
        glPushMatrix()
        glScalef(defs.WINDOW_SCALE[0], defs.WINDOW_SCALE[1], 1)
        glTranslatef(-Game.camera_x, -Game.camera_y, 0)
        # draw quads
        keys = list(set(self.callbacks.keys() + self.quads.keys()))
        keys.sort()
        for key in keys:
            glBegin(GL_QUADS)
            quads = self.quads.get(key)
            if quads:
                for x, y, w, h, z, c1, c2, c3, c4, bf in quads:
                    if bf:
                        glEnd()
                        glBlendFunc(bf[0], bf[1])
                        glBegin(GL_QUADS)
                    if c1:
                        glColor4f(c1[0], c1[1], c1[2], c1[3])
                    glVertex3f(x, y + h, z)
                    if c2:
                        glColor4f(c2[0], c2[1], c2[2], c2[3])
                    glVertex3f(x + w, y + h, z)
                    if c3:
                        glColor4f(c3[0], c3[1], c3[2], c3[3])
                    glVertex3f(x + w, y, z)
                    if c4:
                        glColor4f(c4[0], c4[1], c4[2], c4[3])
                    glVertex3f(x, y, z)
                    if c1 or c2 or c3 or c4:
                        glColor3f(1, 1, 1)
                    if bf:
                        glEnd()
                        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                        glBegin(GL_QUADS)
            glEnd()
            callbacks = self.callbacks.get(key)
            if callbacks:
                for callback, args, kwargs in callbacks:
                    callback(*args, **kwargs)
        glPopMatrix()
        self.callbacks = {}
        self.quads = {}
        self.flush_labels()

    @classmethod
    def flush_labels(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(-Game.camera_x * defs.WINDOW_SCALE[0], -Game.camera_y * defs.WINDOW_SCALE[1], 0)
        for label, x, y, scale in self.labels:
            if scale:
                glPushMatrix()
                label.anchor_x = "center"
                label.anchor_y = "center"
                glTranslatef(x * defs.WINDOW_SCALE[0], y * defs.WINDOW_SCALE[1], 0)
                glScalef(*scale)
                label.x = label.y = 0
                label.draw()
                glPopMatrix()
            else:
                label.x = x * defs.WINDOW_SCALE[0]
                label.y = y * defs.WINDOW_SCALE[1]
                label.draw()
        self.labels = []
        glColor3f(1, 1, 1)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        #self.fps_label.draw()
        Score.draw()
    
    @classmethod
    def callback(self, callback, *args, **kwargs):
        if not kwargs["z"] in self.callbacks:
            self.callbacks[kwargs["z"]] = []
        self.callbacks[kwargs["z"]].append((callback, args, kwargs))
    
    @classmethod
    def label(self, label, x, y, scale=None):
        self.labels.append((label, x, y, scale))
    
    @classmethod
    def quad(self, x, y, w, h, z, c1=None, c2=None, c3=None, c4=None, bf=None):
        if not z in self.quads:
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
        # window
        if not self.window:
            pyglet.font.add_file(defs.FONT_FILE)
            self.keys = key.KeyStateHandler()
            if defs.WINDOW_FULLSCREEN:
                self.window = pyglet.window.Window(fullscreen=defs.WINDOW_FULLSCREEN,
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
        glClearColor(0.6, 0.5, 0.7, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # game
        Draw.__init__()
        Score.__init__()
        import actors
        actors.AmbientSound.stop_all()
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
        print "loading"
        import worlds, tiles, actors, effects, particles
        for name in dir(effects):
            cls = getattr(effects, name)
            try:
                if cls is not effects.Effect and issubclass(cls, effects.Effect):
                    self.effects.append(cls)
            except TypeError:
                pass
        self.world = worlds.load("tiles")
        self.world.load_map("test_map_horiz")
        for name in dir(actors):
            cls = getattr(actors, name)
            try:
                if cls is not actors.Actor and issubclass(cls, actors.Actor):
                    cell_type = cls.CELL_TYPE
                    if cell_type:
                        for cell in self.world.map.get_for_type(cell_type):
                            self.spawn(cls(x=cell.x, y=cell.y))
            except TypeError:
                pass
        self.player = self.actors_by_type[defs.CELL_HUMAN_PLAYER][0]
        #self.player.x = 1024
        #self.player.y = 96
        self.spawn(particles.Arrow(self.player.x, self.player.y + 100))
        rocket = self.actors_by_type[defs.CELL_HUMAN_ROCKET][0]
        self.spawn(particles.Arrow(rocket.x - 35, rocket.y - 15))
        self.mothership = self.actors_by_type[defs.CELL_ALIEN_MOTHERSHIP][0]
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
            if self.player.has_rocket and self.player.y > 900 + self.camera_height:
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
        if symbol == key.C:
            self.screenshot()
        elif symbol == key.ENTER:
            self.__init__()
    
    @classmethod
    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.player.space_pressed = False
    
    @classmethod
    def on_update(self, dt, interval):
        self.window.invalid = True
        if self.game_over:
            return
        import actors
        self.time += dt
        self.dt += dt
        while self.dt >= 0.015:
            self.dt -= 0.015
            for actor in self.actors:
                actor.update(0.015)
            for particle in self.particles:
                particle.update(0.015)
        actors.AmbientSound.update_all()
    
    @classmethod
    def remove(self, actor):
        import particles
        actor.on_remove()
        if isinstance(actor, particles.Particle):
            helpers.remove(self.particles, actor)
        else:
            helpers.remove(self.actors, actor)
            helpers.remove(self.actors_by_type[actor.CELL_TYPE], actor)
        del actor
    
    @classmethod
    def screenshot(self):
        import time
        filename = "screenshot_%d.png" % time.time()
        print "writing screenshot to", filename
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
    
    @classmethod
    def spawn(self, actor):
        import particles
        if isinstance(actor, particles.Particle):
            self.particles.append(actor)
        else:
            self.actors.append(actor)
            if not actor.CELL_TYPE in self.actors_by_type:
                self.actors_by_type[actor.CELL_TYPE] = []
            self.actors_by_type[actor.CELL_TYPE].append(actor)
        return actor

class Score(object):
    HUMANS_LOST = "humans_lost"
    HUMANS_SAVED = "humans_saved"
    POINTS = "points"
    VALUES = {
        HUMANS_LOST: {
            "text": "HUMANS LOST: %d",
            "size": 6, "x": defs.WINDOW_WIDTH - 130, "y": 10},
        HUMANS_SAVED: {
            "text": "HUMANS SAVED: %d",
            "size": 6, "x": defs.WINDOW_WIDTH - 138, "y": 25},
        POINTS: {
            "text": "SCORE %d",
            "size": 10, "x": 10, "y": 10},
        }
    
    @classmethod
    def __init__(self):
        self.you_win = Draw.create_label(size=32, text="YOU WIN!", x=defs.WINDOW_WIDTH*0.5, y=defs.WINDOW_HEIGHT*0.5)
        self.you_win.anchor_x = "center"
        self.you_win.anchor_y = "center"
        self.you_died = Draw.create_label(size=32, text="YOU DIED :(", x=defs.WINDOW_WIDTH*0.5, y=defs.WINDOW_HEIGHT*0.5 + 50)
        self.you_died.color = (0, 0, 0, 255)
        self.you_died.anchor_x = "center"
        self.you_died.anchor_y = "center"
        self.you_died2 = Draw.create_label(size=16, text="press enter to try again", x=defs.WINDOW_WIDTH*0.5, y=defs.WINDOW_HEIGHT*0.5 - 50)
        self.you_died2.color = (0, 0, 0, 255)
        self.you_died2.anchor_x = "center"
        self.you_died2.anchor_y = "center"
        self.died = False
        self.reset()
    
    @classmethod
    def add(self, name, value, why=None):
        import particles
        if name == "points":
            text = "+%d" % value
            if why:
                text = why + " " + text
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
        label = name + "_label"
        if not hasattr(self, label):
            setattr(self, label, Draw.create_label(**self.VALUES[name]))
            label = getattr(self, label)
        else:
            label = getattr(self, label)
        label.text = self.VALUES[name]["text"] % value
        return value
    
    @classmethod
    def draw(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        if Game.game_over:
            if Game.game_lost:
                glBegin(GL_QUADS)
                glColor3f(1, 1, 1)
                glVertex3f(0, 0, -0.9)
                glVertex3f(0, defs.WINDOW_HEIGHT, -0.9)
                glVertex3f(defs.WINDOW_WIDTH, defs.WINDOW_HEIGHT, -0.9)
                glVertex3f(defs.WINDOW_WIDTH, 0, -0.9)
                glEnd()
                self.you_died.draw()
                self.you_died2.draw()
                if not self.died:
                    for name in self.VALUES:
                        getattr(self, name + "_label").color = (0, 0, 0, 255)
                self.died = True
            else:
                glBegin(GL_QUADS)
                glColor3f(0, 0, 0)
                glVertex3f(0, 0, -0.9)
                glVertex3f(0, defs.WINDOW_HEIGHT, -0.9)
                glVertex3f(defs.WINDOW_WIDTH, defs.WINDOW_HEIGHT, -0.9)
                glVertex3f(defs.WINDOW_WIDTH, 0, -0.9)
                glEnd()
                self.you_win.draw()
        for name in self.VALUES:
            getattr(self, name + "_label").draw()
    
    @classmethod
    def reset(self):
        for name in self.VALUES:
            self.set(name, 0)
            getattr(self, name + "_label").color = (255, 255, 255, 255)
