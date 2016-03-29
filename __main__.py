'''
@author: kamichal
'''

import sys
from PyQt4 import QtGui
from PrawoWiazkiApp import OknoGlowne

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('OknoGlowne')

    main = OknoGlowne()
    main.resize(666, 333)
    main.show()

    sys.exit(app.exec_())

