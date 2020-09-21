# coding=utf-8
import struct
import numpy as np
from obj import Obj
from collections import namedtuple
from gl_aux import *

#import numpy as np
#from numpy import matrix, cos, sin

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z','w'])

def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # 2 bytes
    return struct.pack('=h',w)

def dword(d):
    # 4 bytes
    return struct.pack('=l',d)

def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])


def baryCoords(A, B, C, P):
    # u es para la A, v es para B, w para C
    try:
        u = ( ((B.y - C.y)*(P.x - C.x) + (C.x - B.x)*(P.y - C.y) ) /
              ((B.y - C.y)*(A.x - C.x) + (C.x - B.x)*(A.y - C.y)) )

        v = ( ((C.y - A.y)*(P.x - C.x) + (A.x - C.x)*(P.y - C.y) ) /
              ((B.y - C.y)*(A.x - C.x) + (C.x - B.x)*(A.y - C.y)) )

        w = 1 - u - v
    except:
        return -1, -1, -1

    return u, v, w

BLACK = color(0,0,0)
WHITE = color(1,1,1)

class Raytracer(object):
    def __init__(self, width, height):
        self.backcolor = BLACK
        self.pointcolor = WHITE
        #self.light = V3(0,0,1)
        #self.active_texture = None
        #self.active_shader = None
        self.glCreateWindow(width, height)
        self.camPosition = V3(0,0,0)
        self.fov = 60
        self.scene = []
        self.pointLight = None
        self.ambientLight = None

    #def glInit(self):
    #    self.pixels =[]
    
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewPort(0, 0, width, height)
        #self.createViewMatrix()
        #self.createProjectionMatrix()

    def glViewPort(self, x, y, width, height):
        self.glViewPortWidth = width - 1
        self.glViewPortHeight = height - 1
        self.glViewPortX = x
        self.glViewPortY = y
        self.viewportMatrix = matrix([[width/2,        0,   0,  x + width/2],
                                      [      0, height/2,   0, y + height/2],
                                      [      0,        0, 0.5,          0.5],
                                      [      0,        0,   0,            1]])

    def glClear(self):
        self.pixels = [ [ self.backcolor for x in range(self.width)] for y in range(self.height) ]
        self.zbuffer = [ [ float('inf') for x in range(self.width)] for y in range(self.height) ]

    def glClearColor(self, r, g, b):
        self.backcolor = color(r, g, b) 
        self.pixels = [ [ self.backcolor for x in range(self.width)] for y in range(self.height) ]
        self.zbuffer = [ [ float('inf') for x in range(self.width)] for y in range(self.height) ]

    def glVertex(self, x, y):
        glVertexX = ( x + 1 ) * ( self.glViewPortWidth / 2 ) + self.glViewPortX 
        glVertexY = ( y + 1 ) * ( self.glViewPortHeight / 2) + self.glViewPortY 
        #print (round(glVertexX))
        #print (round(glVertexY))
        self.pixels[round(glVertexY)][round(glVertexX)] = self.pointcolor

    def glColor(self, r, g, b):
        self.pointcolor = color(r, g, b)

    def glFinish(self, filename='out.bmp'):
        self.write(filename)        
    
    def write(self, filename):
        # Función write basada en ejemplo realizado en clase
        archivo = open(filename, 'wb')

        # File header 14 bytes
        archivo.write(char('B'))
        archivo.write(char('M'))

        archivo.write(dword(14 + 40 + self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(14 + 40))

        # Image Header 40 bytes
        archivo.write(dword(40))
        archivo.write(dword(self.width))
        archivo.write(dword(self.height))
        archivo.write(word(1))
        archivo.write(word(24))
        archivo.write(dword(0))
        archivo.write(dword(self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))

        # Pixeles, 3 bytes cada uno

        for x in range(self.height):
            for y in range(self.width):
                archivo.write(self.pixels[x][y])

        archivo.close()

    def point(self, x, y, color = None):
        if x < self.glViewPortX or x >= self.glViewPortX + self.glViewPortWidth or y < self.glViewPortY or y >= self.glViewPortY + self.glViewPortHeight:
            return

        if x >= self.width or x < 0 or y >= self.height or y < 0:
            return

        try:
            self.pixels[y][x] = color or self.pointcolor
        except:
            pass

    
    def glZBuffer(self, filename):
        archivo = open(filename, 'wb')

        # File header 14 bytes
        archivo.write(bytes('B'.encode('ascii')))
        archivo.write(bytes('M'.encode('ascii')))
        archivo.write(dword(14 + 40 + self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(14 + 40))

        # Image Header 40 bytes
        archivo.write(dword(40))
        archivo.write(dword(self.width))
        archivo.write(dword(self.height))
        archivo.write(word(1))
        archivo.write(word(24))
        archivo.write(dword(0))
        archivo.write(dword(self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))

        minZ = float('inf')
        maxZ = -float('inf')
        for x in range(self.height):
            for y in range(self.width):
                if self.zbuffer[x][y] != -float('inf'):
                    if self.zbuffer[x][y] < minZ:
                        minZ = self.zbuffer[x][y]

                    if self.zbuffer[x][y] > maxZ:
                        maxZ = self.zbuffer[x][y]

        for x in range(self.height):
            for y in range(self.width):
                depth = self.zbuffer[x][y]
                if depth == -float('inf'):
                    depth = minZ
                
                if (maxZ - minZ) > 0:
                    depth = (depth - minZ) / (maxZ - minZ)
                else:
                    depth = (depth - minZ)

                archivo.write(color(depth,depth,depth))
                

        archivo.close()

    
    def rtRender(self):
        count= 0
        print('wait for it...')
        #recorre pixel por pixel
        for y in range(self.height):
            for x in range(self.width):
                count = count + 1
                if count == 150000: 
                    print('wait for it...')
                    count= 0

                Px = 2 * ( ( x + 0.5 ) / self.width ) - 1
                Py = 2 * ( ( y + 0.5 ) / self.height ) - 1

                #FOV(angulo de vision), asumiendo que el near plane esta a 1 unidad de la camara
                t = tan( (self.fov * np.pi / 180) / 2 )
                r = t * self.width / self.height
                Px *= r
                Py *= t

                #Nuestra camara siempre esta viendo hacia -Z
                direction = V3(Px, Py, -1)
                normal_direction = vectNormal(direction)
                direction = V3(direction.x / normal_direction, direction.y / normal_direction, direction.z / normal_direction)

                material = None
                intersect = None

                for obj in self.scene:
                    hit = obj.ray_intersect(self.camPosition, direction)
                    if hit is not None:
                        if hit.distance < self.zbuffer[y][x]:
                            self.zbuffer[y][x] = hit.distance
                            material = obj.material
                            intersect = hit
                
                #Si hubo intersepcion, dibujamos el pixel
                if intersect is not None:
                    self.point(x, y, self.pointColor(material, intersect))

    def pointColor(self, material, intersect):

        objectColor = V3(material.diffuse[2] / 255,
                        material.diffuse[1] / 255,
                        material.diffuse[0] / 255)

        ambientColor = V3(0,0,0)
        diffuseColor = V3(0,0,0)
        specColor = V3(0,0,0)

        shadow_intensity = 0

        if self.ambientLight:
            ambientColor = V3(self.ambientLight.strength * self.ambientLight.color[2] / 255,
                                     self.ambientLight.strength * self.ambientLight.color[1] / 255,
                                     self.ambientLight.strength * self.ambientLight.color[0] / 255)                                     

        if self.pointLight:
            # Sacamos la direccion de la luz para este punto
            light_dir = vectSubtract(self.pointLight.position, intersect.point)
            light_dir_normal = vectNormal(light_dir)

            light_dir = V3(light_dir.x / light_dir_normal, light_dir.y / light_dir_normal, light_dir.z / light_dir_normal) 

            # Calculamos el valor del diffuse color
            intensity = self.pointLight.intensity * max(0, vectDot(light_dir, intersect.normal))
            diffuseColor = V3(intensity * self.pointLight.color[2] / 255,
                                     intensity * self.pointLight.color[1] / 255,
                                     intensity * self.pointLight.color[2] / 255)                                     

            # Iluminacion especular
            view_dir = vectSubtract(self.camPosition, intersect.point)
            view_dir_normal = vectNormal(view_dir)
            view_dir = V3(view_dir.x / view_dir_normal, view_dir.y / view_dir_normal, view_dir.z / view_dir_normal)
            
            # R = 2 * (N dot L) * N - L
            reflect = 2 * vectDot(intersect.normal, light_dir)
            reflect = V3(reflect * intersect.normal.x, reflect * intersect.normal.y, reflect * intersect.normal.z)
            reflect = vectSubtract(reflect, light_dir)

            spec_intensity = self.pointLight.intensity * (max(0, vectDot(view_dir, reflect)) ** material.spec)

            specColor = V3(spec_intensity * self.pointLight.color[2] / 255,
                                  spec_intensity * self.pointLight.color[1] / 255,
                                  spec_intensity * self.pointLight.color[0] / 255)                                  

            for obj in self.scene:
                if obj is not intersect.sceneObject:
                    hit = obj.ray_intersect(intersect.point,  light_dir)
                    if hit is not None and intersect.distance < vectNormal(vectSubtract(self.pointLight.position, intersect.point)):
                        shadow_intensity = 1

        # Formula de iluminacion
        finalColor = V3((ambientColor.x + (1 - shadow_intensity) * (diffuseColor.x + specColor.x)) * objectColor.x,
                        (ambientColor.y + (1 - shadow_intensity) * (diffuseColor.y + specColor.y)) * objectColor.y,
                        (ambientColor.z + (1 - shadow_intensity) * (diffuseColor.z + specColor.z)) * objectColor.z)
        
        r = min(1,finalColor.x)
        g = min(1,finalColor.y)
        b = min(1,finalColor.z)

        return color(r, g, b)


                











                











