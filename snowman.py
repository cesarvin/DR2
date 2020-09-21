from gl import Raytracer, color, V2, V3
from obj import Obj, Texture
from sphere import Sphere, Material, PointLight, AmbientLight
import random

snowman = Material(diffuse = color(1, 1, 1), spec = 16)
button = Material(diffuse = color(0, 0, 0), spec = 32)
nose = Material(diffuse = color(1, 0.5, 0), spec = 64)

width = 960
height = 1280

# width = 240
# height = 320

r = Raytracer(width,height)
r.glClearColor(0.3,0.5,0.8)

r.pointLight = PointLight(position = V3(-2,2,0), intensity = 1)
r.ambientLight = AmbientLight(strength = 0.1)

r.glClearColor(0.3,0.5,0.8)

print('\nThis render gonna be legen—\n')

r.scene.append( Sphere(V3(0.15, 1.6,  -4), 0.05, button) )
r.scene.append( Sphere(V3(-0.15, 1.6,  -4), 0.05, button) )
r.scene.append( Sphere(V3(0, 1.4,  -3.9), 0.10, nose) )

r.scene.append( Sphere(V3(0.20, 1.25,  -4), 0.04, button) )
r.scene.append( Sphere(V3(-0.08, 1.20,  -4), 0.04, button) )
r.scene.append( Sphere(V3(0.08, 1.20,  -4), 0.04, button) )
r.scene.append( Sphere(V3(-0.20, 1.25,  -4), 0.04, button) )

r.scene.append( Sphere(V3(0, 1.1,  -6.3), 0.18, button) )
r.scene.append( Sphere(V3(0, 0.2,  -6.4), 0.20, button) )
r.scene.append( Sphere(V3(0, -0.8,  -6.0), 0.22, button) )

r.scene.append( Sphere(V3(0, 2.6,  -8), 0.90, snowman) )
r.scene.append( Sphere(V3(0, 1,  -8), 1.25, snowman) )
r.scene.append( Sphere(V3(0, -1.1,  -8), 1.6, snowman) )
 
r.rtRender()
print('\n—dary!\n')

r.glFinish('snowman.bmp')
