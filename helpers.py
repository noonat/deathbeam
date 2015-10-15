import pyglet
from pyglet.gl import *

def abs_clamp(value, max):
	if value < -max:
		return -max
	if value > max:
		return max
	return value

def clamp(value, min, max):
	if value < min:
		return min
	if value > max:
		return max
	return value

def remove(container, item):
	try:
		container.remove(item)
		return True
	except ValueError:
		return False
	
def set_anchor(image, px, py):
	image.anchor_x = px * image.width
	image.anchor_y = px * image.height

def set_nearest(texture):
	if not isinstance(texture, pyglet.image.Texture):
		texture = texture.texture
	glTexParameteri(texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	glTexParameteri(texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
