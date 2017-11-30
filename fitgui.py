

import sys
from math import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from lmfit import  Model

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 640
        self.height = 400

        menubar = self.menuBar()

        loadAct = QAction( 'Load', self)
        loadAct.setShortcut('Ctrl+L')
        loadAct.triggered.connect(self.load)
        menubar.addAction(loadAct)

        fitAct = QAction( 'Line', self)
        fitAct.triggered.connect(lambda : self.fit(2))
        menubar.addAction(fitAct)

        fitAct = QAction( ' Gauss', self)
        fitAct.triggered.connect(lambda: self.fit(1))
        menubar.addAction(fitAct)

        fitAct = QAction( ' Poly3', self)
        fitAct.triggered.connect(lambda: self.fit(3))
        menubar.addAction(fitAct)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def load(self):
        print("start")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        self.setWindowTitle(self.fileName);
        if self.fileName:
            self.data = np.genfromtxt(self.fileName, delimiter=",")
            print(self.data)
            self.fit(1, self.fileName)

    def fit(self, type=1, nam=""):
            self.plot = PlotCanvas(parent=self, data=self.data, type=type, nam=nam)
            self.setCentralWidget(self.plot)
            self.show()

class PlotCanvas(FigureCanvas):
    def __init__(self, data=None, type=3, parent=None,width=5, height=4, dpi=100, nam=""):
        fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        print("About to make funcs")
        if type==1:
            def func(x, p1,p2,p3):
                "1-d gaussian: gaussian(x, amp, cen, wid)"
                return (p1 / (np.sqrt(2 * np.pi) * p2)) * np.exp(-(x - p3) ** 2 / (2 * p2 ** 2))
        elif type==2:
            def func(x,p1,p2,p3):
                "Straight   line"
                return p1*x+p2
        elif type==3:
            def func(x,p1,p2,p3):
                "poly"
                return p1*x*x + p2*x + p3

        print("after making gauss")
        print(data)
        x = data[:, 0]
        y = data[:, 1]
        gmodel = Model(func)
        result = gmodel.fit(y, x=x, p1=1, p2=1, p3=1)
        print(x)
        print(y)

        # #---- find outlier point ----
        # for p in zip(zip(x, y), :
        #   dist = np.abs((p

        best = 0
        bestdist = 0.0
        for i in range(0, len(result.best_fit)-1):
          l = (i,   result.best_fit[i  ])
          h = (i+1, result.best_fit[i+1])


          sqr = lambda x: x*x;

          dist = (abs((h[1] - l[1])*x[i] - (h[0] - l[0])*y[i] +
                      h[0]*l[1] - h[1]*l[0]));
          dist /= sqrt(sqr(h[1] - l[1]) + sqr(h[0] - l[0]))

          print(dist)
          if ( dist > bestdist ):
            best = i;
            bestdist = dist

        print(result.best_fit);
        print(result.best_values);
        # for pt in zip(x, y):
          # for i in result.best_fit:
          #   print(i[0])


        print(result.best_fit)
        ax = self.figure.add_subplot(111)
        ax.plot(data[:,0],data[:,1],'o')
        ax.plot(data[best,0], data[best,1], 'go')
        ax.plot(result.best_fit,"r")
        ax.grid(True)
        plt.title(nam)
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
