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
  dist = length(o) - (6.0 + 2.0*sin(o.y*o.x))
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
def JuliaSet ( d, o, c ):
  zoom = 1.0
  z = vec2(1.5 * (o.x - d.x*0.5)/(0.5*zoom*d.x),
                 (o.y - d.y*0.5)/(0.5*zoom*d.y))
  (max_it, it) = (512, 0)
  while ( it < max_it ):
    if ( length(z) >= 20000.0 ): break;
    z = vec2(z.x*z.x - z.y*z.y, z.x*z.y + z.y*z.x) + c
    it += 1

  return [-1, it/max_it, ((it*2.0)%256)/256.0, (it<max_it)]
def noise( u ):
  return sin(u.x*1.5)*cos(1.5*u.y)
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

def lerp(x, y, a):
  return x * (1.0 - a) + y*a;

#http://www.iquilezles.org/www/articles/smin/smin.htm
def smin(a, b, k):
  h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0)
  return lerp(b, a, h) - k*h*(1.0-h)

fract = lambda x: x-int(x)

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

    # square = Square(o-d/2, vec2(45.0), 2.0)
    # circle = Circle_Modulo(d, o)
    # dist = opUnion(square, circle)

    # square = Square(o-d/4, vec2(45.0), 4.0)
    # circle = Circle(o-d/2+d/16, 45.0)
    # dist = opUnion(square, circle)
    # dist = [0.0, 1.0, 1.0, 1.0]
    # dist[0] = smin(square[0], circle[0], 32.4)

    # circle = Circle_Modulo(d, o)
    # circle2 = Circle_Modulo(d, o+d*0.5)
    # dist = [0.0, 1.0, 1.0, 1.0]
    # dist[0] = smin(circle[0], circle2[0], 40.4)
    # dist[0] = opSubtraction(dist, Circle_Lipschitz(d, o))[0]

    # ---- fractals ----
    # dist = MandelbrotFractal(d, o)
    # dist = JuliaSet(d, o, vec2(-0.7269, 0.1889))
    # dist = JuliaSet(d, o, vec2(-0.835, 0.232))
    # dist = JuliaSet(d, o, vec2(1.61803398) - vec2(2.0, 1.0))
    # dist = [-1.0, 0.0, 0.0, 0.0]
    # p = (0.0 + 2.0*(o/d))*4.0
    # dist[1] = dist[2] = dist[3] = FBM(p)
    # dist[1] = dist[2] = dist[3] = FBM(p + FBM(p))
    # dist[1] = FBM(p*0.42 +
    #             FBM(p*vec2(0.23, 1.232) + FBM(p*1.3+fract(80.0*sin(p.x*12.232)) +
    #             FBM(p*9.1*sin(8.392*p.y+p.x*423.232)))))


    t = lambda a: int(a*255);
    plane[y, x, :] = (
      (Apply_Col(dist), Apply_Col([0, 0, 0]))[int(dist[0] > 0)])

plt.imshow(plane)
plt.show()
