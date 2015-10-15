from __future__ import absolute_import
import os
import sys


ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

CELL_HUMAN_PLAYER = 1        # 1-49 human actors
CELL_HUMAN_CIVILIAN = 2
CELL_HUMAN_SCIENTIST = 3
CELL_HUMAN_COMMANDER = 4
CELL_HUMAN_ROCKET = 25
CELL_HUMAN_RESCUE = 50       # 50-99 human buildings
CELL_HUMAN_ROCKET_PAD = 51
CELL_ALIEN_MOTHERSHIP = 100  # 150-199 alien buildings
CELL_ALIEN_TURRET = 150
CELL_INFO_BEAM = 200         # 200-255 generic
CELL_KILL = 255

CELL_EDGE_TOP = 1
CELL_EDGE_LEFT = 2
CELL_EDGE_BOTTOM = 4
CELL_EDGE_RIGHT = 8
CELL_EDGE_SLOPE = 128

FONT = 'Atari Classic Chunky'
FONT_FILE = os.path.join(ASSETS_DIR, 'atarcc__.ttf')

PHYSICS_NONE = 0      # don't apply any physics
PHYSICS_ATTACHED = 1  # like velocity, but anchored to another actor
PHYSICS_VELOCITY = 2  # apply normal velocity physics

SOUND = True
if '--no-sound' in sys.argv:
    SOUND = False

TEXT_CIVILIAN_DEATHS = (
    'MY SPLEEN!',
    'UGH!',
    'AAUUGHHH!',
    'MERCY!',
    'YEARRGGHH!',
    'IT BURNS!')

WINDOW_FULLSCREEN = False
if '--fullscreen' in sys.argv:
    WINDOW_FULLSCREEN = True
WINDOW_SCALE = [2, 2]
WINDOW_VSYNC = True
if '--no-vsync' in sys.argv:
    WINDOW_VSYNC = False
WINDOW_WIDTH = 640
if '--width' in sys.argv:
    i = sys.argv.index('--width')
    WINDOW_WIDTH = int(sys.argv[i+1])
WINDOW_HEIGHT = 480
if '--height' in sys.argv:
    i = sys.argv.index('--height')
    WINDOW_HEIGHT = int(sys.argv[i+1])

Z_GROUP_RANGE = 0.1   # groups get a 0.0-0.1 range
Z_LAYER_RANGE = 0.01  # layers get a 0.00-0.01 range within a group
Z_UI = 0.9
Z_OVERLAY = 0.8
Z_MAP_FOREGROUND = 0.3
Z_PARTICLE_FOREGROUND = 0.2
Z_ACTOR_FOREGROUND = 0.1
Z_PLAYER = 0
Z_ACTOR_BACKGROUND = -0.1
Z_PARTICLE_BACKGROUND = -0.2
Z_MAP_BACKGROUND = -0.3
Z_BEAM = -0.4
