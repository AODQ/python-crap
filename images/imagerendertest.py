from pyshader import *

img = misc.imread("image.png")
dim = vec2(img.shape[1], img.shape[0])

def div(u, v):
  return u/(0.0001 if v==0.0 else v)

#640x480
for x in range(0, img.shape[1]):
  for y in range(0, img.shape[0]):
    o = vec2(x, y)/dim;
    q = o - vec2(0.5)

    c = vec3(0.25)

    c.x += sin(o.x)
    c.y += sin(o.y) - cos(o.y)*0.25
    c.y += sin(o.y) - cos(o.y)*0.25

    box = length(vmax(vabs(q)-vec2(0.1), vec2(0.0)))-0.02
    box = abs(div(0.5, (box)*4.0))*cos(q.y*443.0)*0.2
    circle = abs(div(0.2, abs(length(q)-0.2)*8.0))*cos(q.x*443.0)*0.4

    c = c*vec3(circle) + c*vec3(box)
    img[y, x, :] = Apply_Col([ c.x, c.y, c.z ])


plt.imshow(img)
plt.show()
