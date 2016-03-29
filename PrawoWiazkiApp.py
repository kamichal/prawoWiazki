#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 5 Feb 2016

@author: kamichal
'''

from PyQt4 import QtGui, QtCore

from WzorErlanga import ErlangB
from PyQtKaWig import SuwakPoziomy, WidzetWykres

from matplotlib.font_manager import FontProperties

class WatekObliczeniowy(QtCore.QThread):
    ''' Obliczenia sa wykonywane w osobnym watku. 
    Kiedy watek sie konczy, sane sa wysylane przez sygnal '''
    sygnalPoliczone = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):
        super(WatekObliczeniowy, self).__init__(parent)
        self.parent = parent

    @QtCore.pyqtSlot(dict)
    def SlotZamowNowy(self, slownik):
            self.zamowienie = slownik
            self.start()  # uruchom watek

    def run(self):
        try:
            sloZ = self.zamowienie
            if 'typ' in sloZ.keys():
                A = sloZ['wartA']
                N = sloZ['wartN']
                XX = self.__dziedzinaX(A, sloZ['typ'])
                self.zamowienie['EbX'] = XX
                self.zamowienie['EbY'] = ErlangB(XX, N)
                (self.zamowienie['kursorX'],
                 self.zamowienie['kursorY']) = self.__GenerujKursor(A,N)
                
                if 'podpis' in self.zamowienie.keys():
                    self.zamowienie['podpisPlus'] = \
                    (self.zamowienie['podpis'] + '= %.3f' % ErlangB(A, N))
                
                if self.zamowienie['podgPW']:
                    ErB2 = ErlangB(2*A, 2*N)
                    self.zamowienie['kursor2X'] = 2*A
                    self.zamowienie['kursor2Y'] = ErB2
                    if 'podpis' in self.zamowienie.keys():
                        self.zamowienie['podpisPlus'] += (
                               ' (Eb2= %.3f)' % ErB2)
                    
                self.sygnalPoliczone.emit(self.zamowienie)
            else:
                print 'bledny slownik zamowienia'

        except (RuntimeError, TypeError, NameError):
            raise ('Blad slownika')

    def __dziedzinaX(self, x_zamawiane, typ):
        if typ == 'podglad':
            Npkt = 32
        else:
            Npkt = 200
        x_max = max(32, x_zamawiane)
        return [(1.0 * x * x_max / Npkt) for x in range(Npkt)]

    def __GenerujKursor(self, A, N):
        XX = [A, A, 0]
        erlb = ErlangB(A, N)
        YY = [0, erlb, erlb]
        return (XX, YY)
    

class FormularzKreslenia(QtGui.QWidget):
    sygNowyFormularz = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):
        super(FormularzKreslenia, self).__init__(parent)
        self.setMaximumHeight(72)

        
        self.ukladLewy = QtGui.QVBoxLayout()
        self.ukladPrawy = QtGui.QVBoxLayout()
        self.ukladPrzyciskow = QtGui.QHBoxLayout()
        
        self.parN = SuwakPoziomy(self, 'N', u'linii\nsieci')
        self.parN.UstawMax(170) # silnia wiecej nie wyrobi
        self.parN.SygnSuwakPoszedl.connect(self.__SlotZmianaFormularza)

        self.parA = SuwakPoziomy(self, 'A', u'abonentow')
        self.parA.UstawMax(600)
        self.parA.SygnSuwakPoszedl.connect(self.__SlotZmianaFormularza)

        self.ukladLewy.addWidget(self.parN)
        self.ukladLewy.addWidget(self.parA)
        
        self.opisSeriiDanych = QtGui.QLineEdit(self)
        self.opisSeriiDanych.setText('wykres')

        self.wyswPrawoWiazki = QtGui.QCheckBox(self)
        self.wyswPrawoWiazki.setText(u'wyświetl Prawo\nWiązki (2N,2A)')
        self.wyswPrawoWiazki.clicked.connect(self.__SlotZmianaFormularza)
        
        self.zatwierdz = QtGui.QPushButton(self)
        self.zatwierdz.setText(u'wykreśl')
        self.zatwierdz.setMinimumHeight(30)
        self.zatwierdz.clicked.connect(self.__SlotZlozZamowienie)

        self.zmazik = QtGui.QPushButton(self)
        self.zmazik.setText(u'wyczyść')
        self.zmazik.setMinimumHeight(30)
        self.zmazik.clicked.connect(parent.SlotCzysc)

        self.ukladPrzyciskow.addWidget(self.wyswPrawoWiazki)
        self.ukladPrzyciskow.addWidget(self.zatwierdz)
        self.ukladPrzyciskow.addWidget(self.zmazik)

        self.ukladPrawy.addWidget(self.opisSeriiDanych)
        self.ukladPrawy.addLayout(self.ukladPrzyciskow)
        
        self.formularz = QtGui.QHBoxLayout(self)
        self.formularz.addLayout(self.ukladLewy)
        self.formularz.addLayout(self.ukladPrawy)
        
    
        self.__aktualizujPodpis()
        
    @QtCore.pyqtSlot()
    def __SlotZmianaFormularza(self):
        self.__aktualizujPodpis()
        slownik = self.__FormuujZamowienie()
        slownik['typ'] = 'podglad'
        self.sygNowyFormularz.emit(slownik)

    @QtCore.pyqtSlot()
    def __SlotZlozZamowienie(self):
        slownik = self.__FormuujZamowienie()
        slownik['typ'] = 'zatwierdzone'
        slownik['podpis'] = str(self.opisSeriiDanych.text())
        self.sygNowyFormularz.emit(slownik)

    def __FormuujZamowienie(self):
        return {
               'wartN' : self.parN.wartosc.value() ,
               'wartA' : self.parA.wartosc.value(),
               'podgPW': self.wyswPrawoWiazki.isChecked()}

    def __aktualizujPodpis(self):
        #format = 'Eb 1,%dN (%dA)'
        formatWys = 'E 1,%d(%d)'
        podpis = formatWys % (self.parN.wartosc.value(),
                              self.parA.wartosc.value())

        self.opisSeriiDanych.setText(podpis)

class KontrolerWykresuErlanga(QtGui.QWidget):
    def __init__(self, parent = None):
        super(KontrolerWykresuErlanga, self).__init__(parent)

        self.formularz = FormularzKreslenia(self)
        self.oknoRysowania = WidzetWykres(self)

        self.ukladPionowy = QtGui.QVBoxLayout(self)
        self.ukladPionowy.addWidget(self.formularz)
        self.ukladPionowy.addWidget(self.oknoRysowania)

        self.watek = WatekObliczeniowy(self)
        self.watek.sygnalPoliczone.connect(self.SlotZamowienie)
        self.watek.finished.connect(self.SlotWatekZakonczony)

        self.formularz.sygNowyFormularz.connect(self.watek.SlotZamowNowy)

        self.SlotCzysc()

    @QtCore.pyqtSlot()
    def SlotCzysc(self):
        self.listaZamowien = []
        self.slownikPodgladu = {}

        self.oknoRysowania.axis.clear()
        self.oknoRysowania.canvas.draw()

    @QtCore.pyqtSlot(dict)
    def SlotZamowienie(self, slo):
        if 'typ' in slo.keys():
            if slo['typ'] == 'zatwierdzone':
                # zatwierdzone są akumulowane
                self.listaZamowien.append(slo)
                self.slownikPodgladu = {}
            elif  slo['typ'] == 'podglad':
                # podglad jest zastepowany
                self.slownikPodgladu = slo
        else:
            print 'bledny slownik zamowienia'

        self.__RysujZeSlownika()

    @QtCore.pyqtSlot()
    def SlotWatekZakonczony(self):
        pass  # print 'ol rajt!'

    def __RysujZeSlownika(self):

        self.oknoRysowania.axis.clear()
        
        for n, zam in enumerate(self.listaZamowien): 
            self.oknoRysowania.axis.plot(zam['kursorX'], 
                                         zam['kursorY'],
                                         label=zam['podpisPlus'],
                                         c=self.oknoRysowania.kolorLini(n),
                                         marker=self.oknoRysowania.stylMarkera(n),
                                         ls = '-.')
        
        if self.listaZamowien:
            fontP = FontProperties()
            fontP.set_size('small')
            self.oknoRysowania.axis.legend(prop = fontP, loc=4)
            
        for n, zam in enumerate(self.listaZamowien):
            self.oknoRysowania.axis.plot(
                     zam['EbX'],
                     zam['EbY'],
                     label = zam['podpis'],
                     c=self.oknoRysowania.kolorLini(n))
            
            if 'kursor2X' in zam.keys() and 'kursor2Y' in zam.keys():
                self.oknoRysowania.axis.plot(
                         zam['kursor2X'], 
                         zam['kursor2Y'],
                         label=zam['podpisPlus'],
                         c=self.oknoRysowania.kolorLini(n),
                         marker=self.oknoRysowania.stylMarkera(n),
                         ls = ':')

   
        if self.slownikPodgladu:
            pdg = self.slownikPodgladu
            self.oknoRysowania.axis.plot(pdg['EbX'], 
                                         pdg['EbY'], 
                                         c = '#040802', 
                                         ls = '--')
            self.oknoRysowania.axis.plot(pdg['kursorX'], 
                                         pdg['kursorY'], 
                                         c = '#040802', 
                                         ls = ':')
            
            if 'kursor2X' in pdg.keys() and 'kursor2Y' in pdg.keys():
                self.oknoRysowania.axis.plot(
                         pdg['kursor2X'], 
                         pdg['kursor2Y'],
                         c= '#040802',
                         marker='x',
                         ls = ':')
        
        self.oknoRysowania.axis.grid(b=None, which='major', color="#CCCCCC")
        self.oknoRysowania.axis.set_xlabel(u'Ilość abonentów')
        self.oknoRysowania.axis.set_ylabel(u'Prawd. blokady')
        self.oknoRysowania.canvas.draw()


class OknoGlowne(QtGui.QWidget):
    def __init__(self, parent = None):
        super(OknoGlowne, self).__init__(parent)

        self.zakladki = QtGui.QTabWidget(self)
        zakladka1 = QtGui.QWidget()
        zakladka2 = KontrolerWykresuErlanga(self)

        edytorTekstu = QtGui.QTextEdit(self)
        edytorTekstu.setText(self.__opis())
        edytorTekstu.setReadOnly(True)
        
        ukladZakladki1 = QtGui.QVBoxLayout()
        ukladZakladki1.addWidget(edytorTekstu)
        zakladka1.setLayout(ukladZakladki1)

        ukladOkna = QtGui.QVBoxLayout(self)
        ukladOkna.addWidget(self.zakladki)

        self.zakladki.addTab(zakladka1, "Opis programu")
        self.zakladki.addTab(zakladka2, "Wykres B-Erlang'a (A)")
        self.zakladki.setCurrentIndex(1)
        self.zakladki.setWindowTitle('ErlangB')
        self.zakladki.show()
    def __opis(self):
        return u''' Ten program wizualizuje wyniki obliczeń według wzoru Erlanga-B w następującej postaci:
    
    E1,N(A) = ( A^N / N! ) / ( suma dla i od 0 do N (A^i / i!))
    
    Ponieważ we wzorze użyta została silnia, to ograniczona jest wartość N do 170 linii sieci (wynik 170! jest liczbą całkowitą, która zajmuje bodajże tysiąc bitów, zatem to jest i tak niezły wynik). Silnia jest obliczana inkrementacyjnie, ale został wykorzystany dość szybki algorytm jej obliczania - dotychczas obliczone wartości dla kolejnych liczb naturalnych są umieszczane w tablicy wyników do przyszłego użycia.

Z polskiej wikipedii:
    Erlang – jednostka natężenia ruchu telekomunikacyjnego. Nazwa wywodzi się od nazwiska Agnera Krarupa Erlanga, autora teorii masowej obsługi, znanej również jako teoria kolejek, która stanowi uogólnienie zjawisk zaobserwowanych w telekomunikacji.

Dla danego systemu telekomunikacyjnego składającego się z N linii, i czasu obserwacji równego 1 godzinie (60 minut), jeśli linia ta zajęta jest cały czas przez pełną godzinę, to natężenie ruchu wynosi 1 Erlang; odpowiednio, jeśli linia ta zajęta jest przez 30 minut, natężenie to wynosi 0,5 Erlanga.

    Program został napisany w języku Python 2.7. z użyciem bibliotek matplotlib oraz PyQt4 i nakładki PyQt na matplotlib (FigureCanvasQTAgg z backend_qt4agg). Instalator programu dla środowisk bez interpretera Python 2.7. to PyInstaller
    
    Pierwotni autorzy: (Małgorzata Kania, Michał Kaczmarczyk) @ Politechnika Wrocławska, wydział Elektroniki. 

    ''' 
    
if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('OknoGlowne')

    main = OknoGlowne()
    main.resize(666, 333)
    main.show()

    sys.exit(app.exec_())
