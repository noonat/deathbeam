from __future__ import absolute_import
import ctypes

import pyglet
from pyglet import gl


def abs_clamp(value, max):
    if value < -max:
        return -max
    elif value > max:
        return max
    else:
        return value


def clamp(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


def create_program(vertex_source, fragment_source):
    """Create a program from a vertex shader and fragment shader.

    :param str vertex_source: Source for the vertex shader.
    :param str fragment_source: Source for the fragment shader.
    :returns: Handle for the fragment program.
    :raises ValueError: if there is an error compiling the shaders or linking
        the program.
    """
    program = gl.glCreateProgram()
    vertex_shader = create_shader(gl.GL_VERTEX_SHADER, vertex_source)
    fragment_shader = create_shader(gl.GL_FRAGMENT_SHADER, fragment_source)
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    log = get_log(program, gl.glGetProgramInfoLog)
    if log:
        raise ValueError('Error linking program: {}'.format(log))
    return program


def create_shader(shader_type, source):
    """Create a shader from source.

    :param shader_type: Type of shader. Should be one of gl.GL_FRAGMENT_SHADER
        or gl.GL_VERTEX_SHADER.
    :param str source: Source code for the shader.
    :returns: Handle for the shader.
    :raises ValueError: if there is an error compiling the shader.
    """
    # turn source into a char[]
    c_source = ctypes.create_string_buffer(source)

    # get a char ** pointing to the char[]
    c_source_pointer = ctypes.cast(
        ctypes.pointer(ctypes.pointer(c_source)),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))

    shader = gl.glCreateShader(shader_type)
    gl.glShaderSource(shader, 1, c_source_pointer, None)
    gl.glCompileShader(shader)
    log = get_log(shader, gl.glGetShaderInfoLog)
    if log:
        raise ValueError('Error compiling shader: {}'.format(log))
    return shader


def get_log(handle, log_fn):
    """Get logs from OpenGL.

    :param handle: Handle for the associated object.
    :param func log_fn: Function to call to get logs.
    :returns: str
    """
    c_buffer = ctypes.create_string_buffer(4096)
    c_buffer_pointer = ctypes.cast(ctypes.pointer(c_buffer),
                                   ctypes.POINTER(ctypes.c_char))
    c_written = ctypes.c_int()
    log_fn(handle, 4096, ctypes.pointer(c_written), c_buffer_pointer)
    return c_buffer.value


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
    gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
