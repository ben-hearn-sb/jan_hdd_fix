__author__ = 'ben.hearn'

"""
	A generic re-use process dialog for all your console output needs
"""

from PySide2 import QtCore, QtGui, QtWidgets

class Process_Dialog(QtWidgets.QDialog):
	def __init__(self, parent=None, fixedHeight=-1, fixedWidth=-1, enableButton=False, progressBar=True,
	             defaultLabelTitle=''):
		QtWidgets.QDialog.__init__(self)
		if parent:
			self.parent = parent
			self.setParent(self.parent)
		self.hasProgressBar = progressBar
		self.defaultLabelTitle = defaultLabelTitle

		if fixedHeight != -1:
			self.setFixedHeight(fixedHeight)
		if fixedWidth != -1:
			self.setFixedWidth(fixedWidth)

		self.enableButtonFlag = enableButton
		self.resize(450, 350)
		self.setModal(True)
		# self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		self.setWindowTitle('Processing....')
		self.setObjectName('PROCESS_DIALOG')
		self.activityLog = QtWidgets.QListWidget()
		# self.activityLog = QtGui.QTextEdit()
		# self.activityLog.setReadOnly(True)

		if progressBar:
			self.dialogProgressBar = Progress_Bar()
			if self.defaultLabelTitle:
				self.dialogProgressBar.setLabelTitle(title=self.defaultLabelTitle)

		self.btnOK = QtWidgets.QPushButton('OK')
		self.btnOK.setDisabled(True)
		self.btnCancel = QtWidgets.QPushButton('Cancel')

		self.layout = QtWidgets.QVBoxLayout()
		# self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(self.activityLog, 0)
		if progressBar:
			self.layout.addWidget(self.dialogProgressBar, 0)
		if enableButton:
			self.layout.addWidget(self.btnOK, 0)
		self.setLayout(self.layout)

		self.btnOK.clicked.connect(self.close)

	# self.btnCancel.clicked.connect(self.cancelExport)

	def keyPressEvent(self, QKeyEvent):
		""" Disabling the ability to close the dialog using esc """
		if QKeyEvent.key() == QtCore.Qt.Key_Escape:
			return

	def closeEvent(self, event):
		""" On close we are removing the Qt window from memory """
		self.deleteLater()
		event.accept()

	def cancelExport(self):
		self.updateLog(message='Cancelled Export. Undoing process...', error=True)
		# self.enableButton()
		self.btnCancel.setDisabled(True)
		self.activateWindow()

	def updateLog(self, message, success=False, warning=False, error=False, good=False, icon=None):
		import datetime
		time = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute,
		                     datetime.datetime.now().second)
		time = str(time)
		processWidget = QtWidgets.QListWidgetItem(time + ': ' + message)
		processWidget.setFlags(QtCore.Qt.ItemIsEnabled)
		if icon:
			processWidget.setIcon(icon)
		color = None
		if warning == True:
			color = 'orange'
		if error == True:
			color = QtCore.Qt.red
		if good:
			color = QtCore.Qt.green
		if success:
			color = QtCore.Qt.green
			if self.enableButtonFlag:
				self.btnOK.setEnabled(True)
			self.activateWindow()
		if color:
			processWidget.setForeground(QtGui.QBrush(QtGui.QColor(color)))
		self.activityLog.addItem(processWidget)
		self.activityLog.scrollToItem(processWidget)
		QtWidgets.QApplication.processEvents()

	def clearLog(self):
		self.activityLog.clear()
		if self.hasProgressBar:
			self.dialogProgressBar.reset(label=self.defaultLabelTitle)

	def enableButton(self):
		self.btnOK.setEnabled(True)


class Progress_Bar(QtWidgets.QWidget):
	def __init__(self, parent=None, total=-1, windowTitle='Default'):
		super(Progress_Bar, self).__init__(parent)
		self.setObjectName('PROGRESS_BAR')
		self.progressbar = QtWidgets.QProgressBar()
		self.progressbar.setMinimum(1)
		self.progressbar.setMaximum(total)
		self.progressLabel = QtWidgets.QLabel('Run thy tool Jan...')
		main_layout = QtWidgets.QVBoxLayout()
		main_layout.addWidget(self.progressLabel)
		main_layout.addWidget(self.progressbar)
		main_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(main_layout)
		self.setWindowTitle(windowTitle)
		self._active = False

	def setActive(self):
		if not self._active:
			self._active = True
			if self.progressbar.value() == self.progressbar.maximum():
				self.progressbar.reset()
		else:
			self._active = False

	def closeEvent(self, event):
		self._active = False

	def setMax(self, max=2):
		self.progressbar.setMaximum(max)

	def reset(self, label='Run thy tool Jan...'):
		self.progressbar.reset()
		self.setLabelTitle(title=label) # Resetting the label title also

	def setLabelTitle(self, title=''):
		self.progressLabel.setText(title)

	def setValue(self, value=-1):
		self.progressbar.setValue(value)