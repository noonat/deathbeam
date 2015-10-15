from __future__ import absolute_import

import pyglet
from pyglet import gl

from . import defs


class Draw(object):

    def __init__(self, game):
        self.game = game
        self.callbacks = {}
        self.labels = []
        self.quads = {}

    def create_label(self, size=12, x=0.0, y=0.0, text='', **kwargs):
        return pyglet.text.Label(text, font_name=defs.FONT, font_size=size,
                                 x=x, y=y)

    def flush(self):
        gl.glPushMatrix()
        gl.glScalef(defs.WINDOW_SCALE[0], defs.WINDOW_SCALE[1], 1)
        gl.glTranslatef(-self.game.camera_x, -self.game.camera_y, 0)
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

    def flush_labels(self):
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        gl.glPushMatrix()
        gl.glTranslatef(-self.game.camera_x * defs.WINDOW_SCALE[0],
                        -self.game.camera_y * defs.WINDOW_SCALE[1], 0)
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
        self.game.score.draw()

    def callback(self, callback, *args, **kwargs):
        if kwargs['z'] not in self.callbacks:
            self.callbacks[kwargs['z']] = []
        self.callbacks[kwargs['z']].append((callback, args, kwargs))

    def label(self, label, x, y, scale=None):
        self.labels.append((label, x, y, scale))

    def quad(self, x, y, w, h, z, c1=None, c2=None, c3=None, c4=None, bf=None):
        if z not in self.quads:
            self.quads[z] = []
        self.quads[z].append((x, y, w, h, z, c1, c2, c3, c4, bf))
