import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Example(QMainWindow):

  def __init__(self):
    super().__init__()
    self.initUI()

  def set_text(s, i):
    s.numlabel.setText("number: " + str(i));

  def SetZero(s): s.set_text(0);
  def SetFive(s): s.set_text(5);
  def SetTen(s):  s.set_text(10);


  def initUI(self):
    self.numlabel = QLineEdit()

    self.qw = QWidget()

    self.vbox = QHBoxLayout()
    self.vbox.addWidget(self.numlabel);

    self.qw.setLayout(self.vbox);

    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle('Simple menu')
    self.show()


if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Example()
  sys.exit(app.exec_())
