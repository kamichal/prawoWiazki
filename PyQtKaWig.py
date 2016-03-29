'''
Created on 24 Jan 2016

@author: kamichal
'''

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import random
from PyQt4 import QtGui, QtCore


class SuwakPoziomy(QtGui.QWidget):
    SygnSuwakPoszedl = QtCore.pyqtSignal()

    def __init__(self, parent=None, nazwa='', jednostka=''):
        super(SuwakPoziomy, self).__init__(parent)
        
        
        self.nazwa = QtGui.QLabel(self)
        self.nazwa.setText(nazwa + ' = ')
        
        self.wartosc = QtGui.QSpinBox(self)

        self.postfiks = QtGui.QLabel(self)
        self.postfiks.setText(jednostka)
        
        self.suwak = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.suwak.valueChanged.connect(self.wartosc.setValue)
        self.suwak.valueChanged.connect(self.SygnSuwakPoszedl)
        self.wartosc.valueChanged.connect(self.suwak.setValue)
        self.wartosc.valueChanged.connect(self.SygnSuwakPoszedl)
     
        self.ukladWidzetu = QtGui.QHBoxLayout(self)        
        self.ukladWidzetu.addWidget(self.nazwa)
        self.ukladWidzetu.addWidget(self.wartosc)
        self.ukladWidzetu.addWidget(self.postfiks)
        self.ukladWidzetu.addWidget(self.suwak)

    def UstawMin(self, maxWart):
        self.suwak.setMinimum(maxWart)
        self.wartosc.setMinimum(maxWart)
        
    def UstawMax(self, maxWart):
        self.suwak.setMaximum(maxWart)
        self.wartosc.setMaximum(maxWart)
        
    
class WidzetWykres(QtGui.QWidget):
    def __init__(self, parent=None):
        super(WidzetWykres, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.axis = self.figure.add_subplot(111)
        
        self.ukladPionowy = QtGui.QVBoxLayout(self)
        self.ukladPionowy.addWidget(self.canvas)
    
    def kolorLini(self, n=0):        
        kolory = (
        'b'  # blue
        'g'  # green
        'r'  # red
        'c'  # cyan
        'm'  # magenta
        'y'  # yellow
        'k'  # black
        'w'  # white
        )
        return kolory[n % len(kolory)]
        
    
    def stylMarkera(self, n=0):
        znaczniki = (
        'x', #     x
        'o', #     circle
        'v', #     triangle_down
        '^', #     triangle_up
        '<', #     triangle_left
        '>', #     triangle_right
        '1', #     tri_down
        '2', #     tri_up
        '3', #     tri_left
        '4', #     tri_right
        '8', #     octagon
        's', #     square
        'p', #     pentagon
        '*', #     star
        'h', #     hexagon1
        '.', #     point
        'H', #     hexagon2
        '+', #     plus
        ',', #     pixel
        'D', #     diamond
        'd', #     thin_diamond
        '|', #     vline
        '_'  #     hline   
        )
        return znaczniki[n%len(znaczniki)]
    
class TestOknoGlowne(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TestOknoGlowne, self).__init__(parent)
        
#         self.suwak = SuwakPoziomy(self)
        
        self.tA = SuwakPoziomy(self,'Asd',"opis moze\nbyc lamany")
        self.tA.UstawMax(1000)
        
        self.tB = SuwakPoziomy(self,'N','[Watt]')
        self.tB.wartosc.setMaximum(200)
        self.tB.postfiks.setText('[laczy]')
        
        self.tC = SuwakPoziomy(self,'E','[V]')
        
        self.uklad = QtGui.QVBoxLayout(self)
        self.uklad.addWidget(self.tA)
        self.uklad.addWidget(self.tB)
        self.uklad.addWidget(self.tC)

class TestWykresow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TestWykresow, self).__init__(parent)
        
#         self.suwak = SuwakPoziomy(self)
        
        self.W = WidzetWykres(self)
    
#         self.RysujCosTam()
        self.RysujSlownikiem()
        self.zatwierdz = QtGui.QPushButton(self)
        self.zatwierdz.setText("Jeszcze raz")
        self.zatwierdz.clicked.connect(self.RysujCosTam)
        
        self.uklad = QtGui.QVBoxLayout(self)
        self.uklad.addWidget(self.W)
        self.uklad.addWidget(self.zatwierdz)

    @QtCore.pyqtSlot()
    def RysujCosTam(self):
        self.W.axis.clear()
        
        N = 16
        XX = range(N)
        YY = []
        
        for _ in range(4):
            tmp = random.sample(range(N), N)
            YY.append(tmp)
            
        for i, seria in enumerate(YY):
            self.W.axis.plot(XX, seria, 
                             c=self.W.kolory[i], 
                             marker=self.W.styleMarkerow[i])
        self.W.canvas.draw()

    @QtCore.pyqtSlot()
    def RysujSlownikiem(self):
        self.W.axis.clear()
        N = 16
        XX = range(N)
        dane = []
        
        for _ in range(4):            
            tmp = random.randint(0,5)
            YY = random.sample(range(N), N)
            dane.append({'xx':XX, 
                         'yy':YY,
                         'ma':self.W.styleMarkerow[tmp],
                         'ko':self.W.kolory[tmp]
                         })
            
        for seria in dane:
            self.W.axis.plot(seria['xx'], 
                             seria['yy'],
                             c=seria['ko'],
                             marker=seria['ma'])
        
        self.W.canvas.draw()


         
if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('OknoGlowne')

#     main = TestOknoGlowne()
    main = TestWykresow()
    main.resize(666, 333)
    main.show()

    sys.exit(app.exec_())