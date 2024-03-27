#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import glfw                         # lean window system wrapper for OpenGL
from PIL import Image

from core import Shader, Mesh, Viewer, Node, load
from transform import translate, identity, rotate, scale


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)


class Triangle(Mesh):
    """Hello triangle object"""
    def __init__(self, shader):
        position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
        self.color = (1, 1, 0)
        attributes = dict(position=position, color=color)
        super().__init__(shader, attributes=attributes)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, global_color=self.color, **uniforms)

    def key_handler(self, key):
        if key == glfw.KEY_C:
            # self.color = (0, 0, 0)
            glfw.set_time(0)
            
class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file
        

class Skybox(Mesh):
    def __init__(self, shader, texture_files):
        position = np.array([
            # Front face
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            # Back face
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,
            # Top face
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
            # Bottom face
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,
            # Right face
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            # Left face
            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0
        ], dtype=np.float32)
        
        indices = np.array([
             0,  1,  2,    0,  2,  3,  # front
             4,  5,  6,    4,  6,  7,  # back
             8,  9, 10,    8, 10, 11,  # top
            12, 13, 14,   12, 14, 15,  # bottom
            16, 17, 18,   16, 18, 19,  # right
            20, 21, 22,   20, 22, 23   # left
        ], dtype=np.uint32)
        
        self.textures = [self.load_texture(filename) for filename in texture_files]
        attributes = dict(position=position)
        super().__init__(shader, attributes=attributes, indices=indices)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, global_color=self.color, **uniforms)

def loadCubeMap(faces): # vecteur de string (faces)
    textureID = None
    GL.glGenTextures(1, textureID)
    GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, textureID)

    for i in range(len(faces)):
        image = Image.open(faces[i])
        image_data = np.array(list(image.getdata()), np.uint8)
    
        GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGB, image.width, image.height, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, image_data)
    
    GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

    return textureID

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    #skybox
    
    skybox_texture_id = loadCubeMap(["right.jpg", "left.jpg", "top.jpg", "bottom.jpg", "front.jpg", "back.jpg"])


    # default color shader
    shader = Shader("color.vert", "color.frag")
    skybox_shader = Shader("skybox.vert", "skybox.frag")

    # place instances of our basic objects
    viewer.add(*[mesh for file in sys.argv[1:] for mesh in load(file, shader)])
    if len(sys.argv) < 2:
        viewer.add(Axis(shader))
        #viewer.add(Node(children=[Cylinder(shader)], transform=translate(x=+2)))
        #viewer.add(Node(children=[Triangle(shader)], transform=translate(x=-1)))
        
        #Ajout de la skybox
        skybox = Skybox(skybox_shader, ["right.png", "left.png", "top.png", "bottom.png", "front.png", "back.png"])
        viewer.add(skybox)
        
        print('Usage:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
              ' format supported by assimp.' % (sys.argv[0],))

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
