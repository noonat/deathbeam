import os

import pyglet

from . import defs


class Sound(object):

    cache = {}

    def __init__(self, actor, filename, min_distance=10.0, pitch=1.0,
                 volume=1.0):
        if not defs.SOUND:
            return
        filename = os.path.join(defs.ASSETS_DIR, 'sounds', filename)
        if filename not in Sound.cache:
            Sound.cache[filename] = pyglet.media.load(filename,
                                                      streaming=False)
        self.sound = Sound.cache[filename]
        self.actor = actor
        self.min_distance = min_distance
        self.pitch = pitch
        self.volume = volume

    def play(self):
        if not defs.SOUND:
            return
        m = self.sound.play()
        m.min_distance = self.min_distance
        m.pitch = self.pitch
        m.position = (self.actor.x, self.actor.y, 0)
        m.volume = self.volume


class AmbientSound(Sound):

    sounds = []

    def __init__(self, actor, filename, auto_update=True, min_distance=10.0,
                 pitch=1.0, volume=1.0):
        if not defs.SOUND:
            return
        super(AmbientSound, self).__init__(actor, filename, min_distance,
                                           pitch, volume)
        AmbientSound.sounds.append(self)
        self.auto_update = auto_update
        self.player = pyglet.media.Player()
        self.player.eos_action = pyglet.media.Player.EOS_LOOP
        self.player.min_distance = min_distance
        self.player.pitch = pitch
        self.player.volume = volume
        self.update()
        self.player.queue(self.sound)
        self.player.play()

    @classmethod
    def stop_all(self):
        if not defs.SOUND:
            return
        for sound in self.sounds:
            sound.player.pause()
            del sound
        self.sounds = []

    def update(self, pos=None):
        if not defs.SOUND:
            return
        if pos:
            self.player.position = pos
        else:
            self.player.position = (self.actor.x, self.actor.y, 0)

    @classmethod
    def update_all(self):
        if not defs.SOUND:
            return
        for sound in self.sounds:
            if sound.auto_update:
                sound.update()
