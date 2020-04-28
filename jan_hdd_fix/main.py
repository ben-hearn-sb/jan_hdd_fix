import ui.ui as ui
import sys
from PySide2 import QtWidgets, QtGui
import qdarkstyle

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("HDD_Fix")

    dark_stylesheet = qdarkstyle.load_stylesheet_pyside2()
    # TODO: Fix the column selection on stylesheet
    app.setStyleSheet(dark_stylesheet)

    font = QtGui.QFont('Arial')
    font.setPointSize(10)
    app.setFont(font)

    window = ui.HDD_FIX()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()