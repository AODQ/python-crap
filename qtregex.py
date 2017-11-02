"""
Take the code at http://euclid.nmu.edu/~rappleto/Classes/CS495.Python/dictionary.py

1 Add a status bar that offers a count of the number of words displayed in the word list window.  It should update as people search
2 Add a menubar with
  File
    Load
    Save
    Exit
3 Add a file-save-as dialog box accessable from the menubar that saves the words in the word list window. https://pythonspot.com/en/pyqt5-file-dialog/
4 Add a load-a-file accessable from the menubar that loads a text file into the word list window.
- Add a button that sets (using the font dialog box) the font of the word list window
- Add a dialog that sets (using the color selector box) the color of the word list window
5 Add a progress bar for some operation
6 Add a slider that controls font size  https://pythonprogramminglanguage.com/pyqt5-sliders/
7 Add a checbox that decides if this is case sensitive or not.
- Convert the progam to use a textarea instead of a QTreeWidget
  -or-
  Convert the program to use a QListWidget https://stackoverflow.com/questions/23835847/how-to-remove-item-from-qlistwidget


Do any 8 of the 10.
Due Thr Nov 2nd

"""
from drange import *
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re

class Example(QMainWindow):

  def __init__(self):
    super().__init__()
    self.ftsize = 10

    self.Load_Dict("dict.txt");

    # Left and right:  a label and a input box
    filterLayout = QHBoxLayout()
    self.filterInput = QLineEdit()
    self.filterInput.textChanged.connect(self.onChanged)
    filterLabel = QLabel("Filter")
    filterLayout.addWidget(filterLabel)
    filterLayout.addWidget(self.filterInput)

    #  .. a tree of words
    self.tree = QTreeWidget()
    self.tree.setAlternatingRowColors(True)
    self.tree.setColumnCount(1)
    self.tree.setHeaderLabels(["Word (99171)"])
    for word in self.words:
      self.tree.addTopLevelItem(QTreeWidgetItem([word]))

    self.menu = self.menuBar();
    self.fmenu = self.menu.addMenu('&File');
    self.fmenuload = QAction('Load', self);
    self.fmenuload.triggered.connect(self.Load);
    self.fmenusave = QAction('Save', self);
    self.fmenusave.triggered.connect(self.Save);
    self.fmenuexit = QAction('Exit', self);
    self.fmenuexit.triggered.connect(self.close);
    self.fmenu.addAction(self.fmenuload);
    self.fmenu.addAction(self.fmenusave);
    self.fmenu.addAction(self.fmenuexit);

    # Make a vbox with the filter stuff and the tree
    tmain = QWidget()
    main = QVBoxLayout()
    buts = QHBoxLayout()
    fontz = QPushButton("change colour");
    fontz.clicked.connect(self.Change_Colour);
    self.prog = QProgressBar();
    self.slid = QSlider();
    self.chex = QCheckBox();
    self.slid.valueChanged.connect(self.Change_Siz);
    self.chex.stateChanged.connect(self.Flip_Lower);
    self.lowercase = False
    buts.addWidget(self.prog)
    buts.addWidget(self.slid)
    buts.addWidget(self.chex)
    main.addLayout(filterLayout)
    main.addWidget(self.tree)
    main.addLayout(buts)
    tmain.setLayout(main)
    self.setCentralWidget(tmain);
    self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Tool);

    # Display everything
    self.setGeometry(300, 300, 300, 150)
    self.setWindowTitle('Buttons')
    self.show()


  def Load_Dict(s, _str):
    # Load the dictionary
    s.words = [word[:-1] for word in open(_str, "r").readlines()]

  def Save(s):
    regex = re.compile(s.filterInput.text())
    fwords = list(filter(regex.search, s.words));
    fname = QFileDialog.getOpenFileName(s, 'Open File', '.');
    file = open(fname[0], "w");
    for t in fwords:
      file.write(t);
      file.write("\n");
    file.close()

  def Flip_Lower(s):
    s.lowercase ^= 1
    s.onChanged()

  def Load(s):
    fname = QFileDialog.getOpenFileName(s, 'Open File', '.');
    s.Load_Dict(fname[0]);
    s.onChanged()

  def Change_Siz(s, i):
    f = s.filterInput.font()
    f.setPointSize(i)
    s.filterInput.setFont(f)
    s.ftsize = i
    s.onChanged()


  def Change_Colour(s):
    pass
    # all the below crashes ??
    # colour = QFileDialog.getOpenFileName(s, 'open file', '.');
    # s.onChanged();
    # s.show()
    # try:
    #   font, ok = QFontDialog.getFont()
    # except Exception:
    #   print(Exception);
    # if ok:
      # s.filterInput.setFont(font)


  def onChanged(s):
    s.prog.setValue(len(s.filterInput.text())/1.0);
    tx = s.filterInput.text()
    if ( s.lowercase ):
      regex = re.compile(tx, re.IGNORECASE)
    else:
      regex = re.compile(tx)
    fwords = list(filter(regex.search, s.words))
    #print("New Stuff" + self.filterInput.text())
    #print(list(filteredWords))
    s.tree.setHeaderLabels(["Word" + "(" + str(len(fwords)) + ")"])
    s.tree.clear()
    for word in fwords:
      #print("Added" + word)
      t = QTreeWidgetItem([word])
      tf = t.font(0)
      tf.setPointSize(s.ftsize)
      t.setFont(0, tf)
      s.tree.addTopLevelItem(t)

if __name__ == '__main__':
  print("Starting app")
  app = QApplication(sys.argv)
  ex = Example()
  sys.exit(app.exec_())
  print("Ending App")
