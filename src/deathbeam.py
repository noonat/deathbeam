import pyglet

from game import Game

# These modules need to be imported, even though they aren't used, because
# they register things that we need to load the world.
import tiles   # noqa
import aliens  # noqa
import humans  # noqa


Game()
pyglet.app.run()
