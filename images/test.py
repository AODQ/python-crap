from pyshader import *

def Circle(o, r):
  dist = length(o) - r
  return [dist, 1.0, 1.0, 1.0];
def Square(o, b, r):
  dist = length(vmax(vabs(o)-b,vec2(0.0)))-r;
  return [dist, 1.0, 1.0, 1.0]
def Square_Rotate(o, b, r):
  dist = length(vmax(vabs(o)-b,vec2(0.0)))-r;
  return [dist, 1.0, 1.0, 1.0]
def Circle_Lipschitz(d, o):
  dist = Circle(o-d/2, 128.0)[0] + sin(o.x*16.0)*12.5 + sin(o.y*16.0)*12.5
  return [dist, sin(o.x*3.0)/d.x, o.y/d.y, 1.0];
def Circle_Modulo(d, o):
  t = o
  o -= d/2
  o.x = (o.x % 32.0) - 16.0
  o.y = (o.y % 32.0) - 16.0
  dist = length(o) - (10.0 + 2.0*sin(o.y*o.x))
  return [dist, t.x/d.x, t.y/d.y, 1.0]
def BoxCircle(d, o):
  pass
def MandelbrotFractal ( d, o ):
  c = o/d * vec2(3.5, 2.0) - vec2(2.6, 1.0)
  z = vec2(0.0)
  it = 0
  for i in range(0, 128):
    if ( length(z) >= 20000.0 ): break;
    z = vec2(z.x*z.x - z.y*z.y, z.x*z.y + z.y*z.x) + c
    it += 1

  it *= 1.0/64.0
  return [-1, it, it*0.5, it]
def noise( u ):
  return sin(u.x*1.5)*sin(1.5*u.y)
def FMul(u, m):
  return vec2(m[0]*u.x + m[2]*u.y,
              m[1]*u.x + m[3]*u.y);
def FBM(u):
  f = 0.0
  m = [0.8, 0.6, -0.6, 0.8]
  f += 0.5    * noise(u); u = FMul(u, m) *2.02;
  f += 0.25   * noise(u); u = FMul(u, m) *2.03;
  f += 0.125  * noise(u); u = FMul(u, m) *2.01;
  f += 0.0625 * noise(u); u = FMul(u, m) *2.04;
  f += 0.03125* noise(u); u = FMul(u, m) *2.01;
  f += 0.015625*noise(u);
  return f/0.9375

opUnion        = lambda u, v: (u, v)[u[0] > v[0]]
opIntersection = lambda u, v: (u, v)[u[0] < v[0]]
opSubtraction  = lambda u, v: (u, v)[-u[0] < v[0]]

def clamp(u, a, b):
  if ( u < a ): return a;
  if ( u > b ): return b;
  return u

def lerp(x, y, a):
  return x * (1.0 - a) + y*a;

#http://www.iquilezles.org/www/articles/smin/smin.htm
def smin(a, b, k):
  h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0)
  return lerp(b, a, h) - k*h*(1.0-h)


def fbm_pattern(u):
  return FBM(u + FBM(u + FBM(u)))


plane = misc.imread("image.png")
d = vec2(plane.shape[1], plane.shape[0])
for x in range(0, plane.shape[1]):
  for y in range(0, plane.shape[0]):
    o = vec2(x, y);

    # ---- signed distance fields ----
    # dist = Circle(o-d/2, 128.0)
    # dist = Circle_Lipschitz(d, o)
    # dist = Circle_Modulo(d, o)
    # dist = Square(o-d/2, vec2(45.0), 2.0)

    square = Square(o-d/2, vec2(45.0), 2.0)
    circle = Circle_Modulo(d, o)
    dist = opSubtraction(square, circle)

    # square = Square(rot(o-d/4, vec2(45.0), 3.0)
    # circle = Circle(o-d/2+d/16, 45.0)
    # dist = opUnion(square, circle)
    # dist = [0.0, 1.0, 1.0, 1.0]
    # dist[0] = smin(square[0], circle[0], 32.4)

    # ---- fractals ----
    # dist = MandelbrotFractal(d, o)
    # dist = [-1.0, 1.0, 1.0, 1.0]
    # p = (-1.0 + 2.0*o/d)*2.0
    # dist[1] = dist[2] = dist[3] = FBM(p)
    # dist[1] = dist[2] = dist[3] = FBM(p + FBM(p))
    # dist[1] = dist[2] = dist[3] = fbm_pattern(p)

    t = lambda a: int(a*255);
    plane[y, x, :] = (
      [t(dist[1]), t(dist[2]), t(dist[3]), 255],
      [0, 0, 0, 255])[int(dist[0] > 0)]

plt.imshow(plane)
plt.show()
