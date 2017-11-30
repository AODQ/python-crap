import matplotlib.pyplot as plt
from numpy import *
from drange import *
from enum import Enum

############ USER DEFINED ######################################################
#airplane
mpns = ([200000, 60000])

class ScaleType(Enum):
  NoScale     = 0
  LogScale    = 1
  StdDevScale = 2
  ScaledScale = 3

scale_type = ScaleType.StdDevScale;

############ FILE/FORMAT #######################################################
#how to scales
std_avg = 0.0;
std_dev = 0.0;
std_max = 0.0;
std_min = 0.0;
def Scale(t, idx):
  t = int(t[idx]);
  return {
    ScaleType.NoScale:     t,
    ScaleType.LogScale:    log(t),
    ScaleType.StdDevScale: ((t) - std_avg[idx])/(std_dev[idx]),
    ScaleType.ScaledScale: (t-std_min[idx])/(std_max[idx]-std_min[idx])
  }[scale_type];

class PurifyFile(UFCS_Mixin):
  def __init__(s, fil):
    s.fp = open(fil, 'r', encoding='utf-8')
    s.nline = s.NLine()
  NLine = lambda s: s.fp.readline()[:-1]
  Empty = lambda s: s.nline == ''
  def Front(s):
    (t, s.nline) = (s.nline, s.NLine())
    t = Range(*(''.join([x for x in t if x != ' ' and x != '\n'])
                  .split(',')[:-1]))
    return t

# returns matrix file as a drange
def Load_File(s):
  return PurifyFile(s).Map(lambda arr: arr[:3]).Array()

dmat = (Range("before-1950.txt", "after-1950.txt")
        .Map(Load_File).Join(lambda t: False).Array())
dmat = dmat[0]
dnl = (dmat.Map(lambda t: PyRange(t[1:]
                         .Map(lambda t: int(t))))
           .Array());
# std deviation
def Avg(g):
  _len = g.Length()
  val = g.Reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]))
  return (val[0]/_len, val[1]/_len);
pdnl = PyRange(dnl)
std_dev = std(pdnl, axis=0)
std_avg = average(pdnl, axis=0)
std_max = dnl.Reduce(lambda x, y: (max(x[0],y[0]), max(x[1],y[1])))
std_min = dnl.Reduce(lambda x, y: (min(x[0],y[0]), min(x[1],y[1])))

dnl = dnl.Map(lambda P: (Scale(P, 0), Scale(P, 1)))


############ NUMPY #############################################################
plt.xlabel("weight")
plt.ylabel("horse power")

mp = ([Scale(mpns, 0), Scale(mpns, 1)])
def Distance(a, b):
  x = a[0]-b[0]; y = a[1]-b[1];
  return sqrt(x*x + y*y)

# TODO ; enumerate bug
bad_enumerate_t = 0
def BadEnumerate(t):
  global bad_enumerate_t
  bad_enumerate_t += 1
  return (t, bad_enumerate_t-1)
plot_dnl = dnl
dnl = dnl.Map(BadEnumerate)
idx = (dnl
          .Map(lambda t: (t[1], Distance(mp, t[0])))
          .Reduce(lambda g, y: (g,y)[g[1]>y[1]]))
print("CLOSEST OF\n", mpns, "\nIS\n", dmat[idx[0]],
      "\nDIST [scaled]: ", idx[1]);

# slope interscept/plot
from scipy import stats

pyrange = (array(PyRange(plot_dnl.Map(lambda g: g[0]).Array())),
           array(PyRange(plot_dnl.Map(lambda g: g[1]).Array())));
regress = stats.linregress(*pyrange)
line = regress[0]*pyrange[0] +  regress[1]
print(line)
plt.plot(pyrange[0], line)

# slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
# line = slope*xi+intercept

plot_dnl.Each(lambda g: plt.plot(*g, 'ro'))
plt.plot(*mp, 'go')
plt.show()
