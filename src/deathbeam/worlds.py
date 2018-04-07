from __future__ import absolute_import
import logging
import os
import pyglet

from . import defs, helpers


logger = logging.getLogger('deathbeam')
_worlds = {}


def add(name, tilesets, maps):
    global _worlds
    _worlds[name] = World(name, tilesets, maps)


def load(game, name):
    global _worlds
    world = _worlds.get(name)
    if world:
        world.load(game)
    return world


class Map(object):

    def __init__(self, **kwargs):
        self.loaded = False
        self.world = None
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def draw(self):
        game = self.world.game
        min_x, min_y = self.get_cxcy_for_xy(
            game.camera_x - self.tileset.tile_width,
            game.camera_y - self.tileset.tile_height)
        max_x, max_y = self.get_cxcy_for_xy(
            game.camera_x + game.camera_width + self.tileset.tile_width,
            game.camera_y + game.camera_height + self.tileset.tile_height)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                c = self.cells[y][x]
                if c.tile:
                    c.draw(game)

    def get_cxcy_for_xy(self, x, y):
        x = int(x / self.tileset.tile_width)
        y = int(y / self.tileset.tile_height)
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        return x, y

    def get_for_type(self, type):
        return self.cells_by_type.get(type, [])

    def get_for_cxcy(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[y][x]

    def get_for_xy(self, x, y):
        x = int(x / self.tileset.tile_width)
        y = int(y / self.tileset.tile_height)
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[y][x]

    def load(self, world):
        logging.info('loading %s.map:%s', world.name, self.name)
        if not self.loaded:
            self.world = world
            self.tileset = self.world.tilesets[self.tileset]
        self.cells = []
        self.cells_by_type = {}
        for y in range(self.height - 1, -1, -1):
            row = []
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile > 0:
                    tile = self.tileset.tiles[tile - 1]
                else:
                    tile = None
                cx = x
                cy = self.height - y - 1
                cell = MapCell(self, cx, cy,
                               self.tileset.tile_width * cx,
                               self.tileset.tile_height * cy,
                               self.tileset.tile_width,
                               self.tileset.tile_height,
                               tile, self.types[y][x], self.bounds[y][x])
                if cell.type not in self.cells_by_type:
                    self.cells_by_type[cell.type] = []
                self.cells_by_type[cell.type].append(cell)
                row.append(cell)
            self.cells.append(row)
        self.loaded = True

    def trace(self, old_x, old_y, new_x, new_y):
        new_cell = self.get_for_xy(new_x, new_y)
        if not new_cell:
            return (new_x, new_y, False, False, None)
        old_cell = self.get_for_xy(old_x, old_y)
        if not old_cell:
            return (new_x, new_y, False, False, new_cell)
        return new_cell.trace(old_cell, old_x, old_y, new_x, new_y)


class MapCell(object):

    def __init__(self, map, cx, cy, x, y, width, height, tile, type, bounds):
        self.map = map
        self.cx = cx
        self.cy = cy
        self.x = x  # x is the left
        self.y = y  # y is the bottom
        self.width = width
        self.height = height
        self.tile = tile  # tile is the tileset image for this cell
        self.type = type  # type is a map specific value 0-255
        self.bounds = bounds  # bounds is an edges bitmask for collision
        self.edgeLeft = self.bounds & defs.CELL_EDGE_LEFT and True or False
        self.edgeRight = self.bounds & defs.CELL_EDGE_RIGHT and True or False
        self.edgeTop = self.bounds & defs.CELL_EDGE_TOP and True or False
        self.edgeBottom = self.bounds & defs.CELL_EDGE_BOTTOM and True or False
        self.edgeSlope = self.bounds & defs.CELL_EDGE_SLOPE and True or False
        self.neighbors = MapCellNeighbors(self, self.cx, self.cy)
        self.metadata = {}

    def __delitem__(self, name):
        del self.metadata[name]

    def __getitem__(self, name):
        return self.metadata.get(name)

    def __setitem__(self, name, value):
        self.metadata[name] = value

    def __str__(self):
        return (
            '<MapCell cx=%d, cy=%d x=%d y=%d w=%d h=%d bounds=%d type=%d>' %
            (self.cx, self.cy, self.x, self.y, self.width, self.height,
             self.bounds, self.type))

    def draw(self, game, color=None):
        if not self.type and not (self.bounds & defs.CELL_EDGE_SLOPE):
            game.draw.quad(self.x, self.y, self.width, self.height,
                           defs.Z_MAP_BACKGROUND, (0, 0, 0, 1))
        else:
            game.draw.callback(self.tile.blit, self.x, self.y,
                               z=defs.Z_MAP_BACKGROUND)

    def trace(self, old_cell, old_x, old_y, new_x, new_y):
        hit = hit_ground = False
        if self.edgeSlope:
            dx = int(new_x - self.x)
            dy = int(new_y - self.y)
            if self.edgeTop:
                # top-left to bottom-right, y >= h - x
                if dy <= self.height - dx:
                    hit = hit_ground = True
                    new_y = self.y + (self.height - dx)
            else:
                # bottom-left to top-right, y >= x
                if dy <= dx:
                    hit = hit_ground = True
                    new_y = self.y + dx + 1
        else:
            if self.edgeLeft and self.x > old_cell.x:
                hit = True
                new_x = self.x - 1
            elif self.edgeRight and self.x < old_cell.x:
                hit = True
                new_x = self.x + self.width
            if self.edgeTop and self.y < old_cell.y:
                hit = hit_ground = True
                new_y = self.y + self.height
            elif self.edgeBottom and self.y > old_cell.y:
                hit = True
                new_y = self.y - 1
        return (new_x, new_y, hit, hit_ground, self)


class MapCellNeighbors(object):

    def __init__(self, cell, cx, cy):
        self.cell = cell
        self.cx = cx
        self.cy = cy

    @property
    def top(self):
        return self.cell.map.get_for_cxcy(self.cx, self.cy + 1)

    @property
    def bottom(self):
        return self.cell.map.get_for_cxcy(self.cx, self.cy - 1)

    @property
    def left(self):
        return self.cell.map.get_for_cxcy(self.cx - 1, self.cy)

    @property
    def right(self):
        return self.cell.map.get_for_cxcy(self.cx + 1, self.cy)


class TileSet(object):

    def __init__(self, **kwargs):
        self.loaded = False
        self.world = None
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
        self.tiles = []

    def load(self, world):
        if self.loaded:
            return
        self.world = world
        logging.info('loading %s.tileset:%s', world.name, self.name)
        self.image = pyglet.image.load(
            os.path.join(defs.ASSETS_DIR, self.name + '.png'))
        self.image_grid = pyglet.image.ImageGrid(self.image, self.length,
                                                 self.stride)
        self.tiles = [self.image_grid[i]
                      for i in range(len(self.image_grid) - 1, -1, -1)]
        for tile in self.tiles:
            helpers.set_nearest(tile.texture)
        self.loaded = True


class World(object):

    def __init__(self, name, tilesets, maps):
        self.loaded = False
        self.name = name
        self.maps = maps
        self.tilesets = tilesets

    def load(self, game):
        self.game = game
        logging.info('loading world: %s', self.name)
        for tileset in self.tilesets.values():
            tileset.load(self)
        for map in self.maps.values():
            map.load(self)
        self.loaded = True

    def load_map(self, name):
        self.map = self.maps.get(name)
        return self.map
