# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from helloword.ui.main_window import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
