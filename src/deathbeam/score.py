from pyglet import gl

from . import defs


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

    def __init__(self, game):
        self.game = game
        self.you_win = self.game.draw.create_label(
            size=32, text='YOU WIN!', x=defs.WINDOW_WIDTH*0.5,
            y=defs.WINDOW_HEIGHT*0.5)
        self.you_win.anchor_x = 'center'
        self.you_win.anchor_y = 'center'
        self.you_died = self.game.draw.create_label(
            size=32, text='YOU DIED :(', x=defs.WINDOW_WIDTH*0.5,
            y=defs.WINDOW_HEIGHT*0.5 + 50)
        self.you_died.color = (0, 0, 0, 255)
        self.you_died.anchor_x = 'center'
        self.you_died.anchor_y = 'center'
        self.you_died2 = self.game.draw.create_label(
            size=16, text='press enter to try again', x=defs.WINDOW_WIDTH*0.5,
            y=defs.WINDOW_HEIGHT*0.5 - 50)
        self.you_died2.color = (0, 0, 0, 255)
        self.you_died2.anchor_x = 'center'
        self.you_died2.anchor_y = 'center'
        self.died = False
        self.reset()

    def add(self, name, value, why=None):
        if name == 'points':
            text = '+%d' % value
            if why:
                text = why + ' ' + text
            self.game.player.attach_text(text)
        self.set(name, self.get(name) + value)

    def get(self, name):
        if not hasattr(self, name):
            return 0
        return getattr(self, name)

    def set(self, name, value):
        setattr(self, name, value)
        label = name + '_label'
        if not hasattr(self, label):
            setattr(self, label,
                    self.game.draw.create_label(**self.VALUES[name]))
            label = getattr(self, label)
        else:
            label = getattr(self, label)
        label.text = self.VALUES[name]['text'] % value
        return value

    def draw(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        if self.game.game_over:
            if self.game.game_lost:
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

    def reset(self):
        for name in self.VALUES:
            self.set(name, 0)
            getattr(self, name + '_label').color = (255, 255, 255, 255)
