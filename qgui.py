import sys
from drange import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def New_Layout(layout_type, *args):
  for a in args:
    try:
      layout_type.addWidget(a);
    except:
      layout_type.addLayout(a);
    layout_type.addStretch();
  return layout_type

def New_Grid ( _range ):
  blah = QGridLayout();
  _range.Each(lambda t: blah.addWidget(t[0], t[1][0], t[1][1]))
  return blah

class Example(QMainWindow):

  def __init__(s, _type):
    super().__init__()
    s.initUIB();

  def New_Button(s, label):
    return QPushButton(label, s);
  def Change ( s, _str ):
    s.lbl.setText((_str))

  def initUIB(s):
    s.qw = QWidget()

    s.vbox = QVBoxLayout()
    s.ql = QLineEdit("type")
    s.ql.textChanged.connect(s.Change)
    s.vbox.addStretch()
    s.vbox.addWidget(s.ql)
    s.vbox.addStretch()

    s.lbl = QLabel("type")
    s.vbox.addWidget(s.lbl)
    s.vbox.addStretch()


    s.qw.setLayout(s.vbox);

    s.setCentralWidget(s.qw);

    s.setGeometry(300, 300, 300, 200)
    s.setWindowTitle('Simple menu')
    s.show()

  def initUIV(s):
    s.qw = QWidget()

    # s.vbox = New_Layout(QVBoxLayout(),
    #                     New_Layout(QHBoxLayout(),
    #                                s.New_Button("h"), s.New_Button("v")),
    #                     s.New_Button("button"),
    #         );
    s.vbox = QTreeWidget()
    s.vbox.addWidget(QLineEdit("1"))
    s.vbox.addWidget(QLineEdit("2"))
    s.vbox.addWidget(QLineEdit("2"))
    s.vbox.addWidget(QLineEdit("2"))
    s.vbox.addWidget(QLineEdit("2"))
    s.vbox.addWidget(QLineEdit("2"))

    s.qw.setLayout(s.vbox);

    s.setCentralWidget(s.qw);

    s.setGeometry(300, 300, 300, 200)
    s.setWindowTitle('Simple menu')
    s.show()


if __name__ == '__main__':

  app = QApplication(sys.argv)
  ex = Example("ui")
  # ex2 = Example("bvi")
  sys.exit(app.exec_())
