from PySide2 import QtCore, QtGui, QtWidgets
import jinja2
import codecs
import os

from .editor import CircleEditor
from .osu_file import OsuFile


class MainWindow(QtWidgets.QWidget):
    def __init__(self, command_prefix, command_dir, out_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("osu! DiffCalc")
        self.out_file = out_file
        self.command_prefix = command_prefix
        self.command_dir = command_dir
        vSplitter = QtWidgets.QSplitter(QtGui.Qt.Orientation.Vertical, self)
        hSplitter = QtWidgets.QSplitter(QtGui.Qt.Orientation.Horizontal, vSplitter)
        vSplitter.addWidget(hSplitter)
        mainLayout = QtWidgets.QHBoxLayout()
        form = QtWidgets.QWidget(vSplitter)
        formLayout = QtWidgets.QFormLayout()
        form.setLayout(formLayout)

        self.setLayout(mainLayout)
        mainLayout.addWidget(vSplitter)
        
        self.editor = CircleEditor(hSplitter)
        hSplitter.addWidget(self.editor)
        hSplitter.addWidget(form)



        self.csSpinBox = QtWidgets.QDoubleSpinBox(form)
        self.csSpinBox.setMinimum(1)
        self.csSpinBox.setMaximum(20)
        self.bpmSpinBox = QtWidgets.QDoubleSpinBox(form)
        self.bpmSpinBox.setMinimum(10)
        self.bpmSpinBox.setMaximum(500)
        self.arSpinBox = QtWidgets.QDoubleSpinBox(form)
        self.arSpinBox.setMinimum(1)
        self.arSpinBox.setMaximum(20)
        self.odSpinBox = QtWidgets.QDoubleSpinBox(form)
        self.odSpinBox.setMinimum(1)
        self.odSpinBox.setMaximum(20)
        self.beatDivisorSpinBox = QtWidgets.QSpinBox(form)
        self.beatDivisorSpinBox.setMinimum(1)
        self.beatDivisorSpinBox.setMaximum(20)
        self.lengthSpinBox = QtWidgets.QSpinBox(form)
        self.lengthSpinBox.setMinimum(1)
        self.lengthSpinBox.setMaximum(1000)

        self.repeatsSpinBox = QtWidgets.QSpinBox(form)
        self.repeatsSpinBox.setMinimum(1)
        self.repeatsSpinBox.setMaximum(1000)
        self.lengthLabel = QtWidgets.QLabel(form)
        self.commandTextEdit = QtWidgets.QLineEdit(form)
        self.addCircleButton = QtWidgets.QPushButton("Add Circle", form)
        self.deleteCircleButton = QtWidgets.QPushButton("Delete", form)
        self.updateButton = QtWidgets.QPushButton("Update", form)
        self.output = QtWidgets.QPlainTextEdit(vSplitter)
        vSplitter.addWidget(self.output)

        font = QtGui.QFont("Courier")
        self.output.setFont(font)


        formLayout.addRow("CS",self.csSpinBox)
        formLayout.addRow("AR",self.arSpinBox)
        formLayout.addRow("OD",self.odSpinBox)
        formLayout.addRow("BPM",self.bpmSpinBox)
        formLayout.addRow("Length (beats)", self.lengthSpinBox)
        formLayout.addRow("Repeats", self.repeatsSpinBox)
        formLayout.addRow("Total Length (s)", self.lengthLabel)
        formLayout.addRow("Beat Divisor", self.beatDivisorSpinBox)
        formLayout.addRow("Command", self.commandTextEdit)

        formLayout.addRow(self.addCircleButton)
        formLayout.addRow(self.deleteCircleButton)
        formLayout.addRow(self.updateButton)
        vSplitter.addWidget(self.output)


        self.addCircleButton.clicked.connect(self.editor.add_circle)
        self.deleteCircleButton.clicked.connect(self.editor.delete_selected)
        self.csSpinBox.valueChanged.connect(self.editor.set_cs)
        self.beatDivisorSpinBox.valueChanged.connect(self.editor.set_beat_divisor)

        self.lengthSpinBox.valueChanged.connect(self.update_length)
        self.lengthSpinBox.valueChanged.connect(self.editor.set_length)

        self.repeatsSpinBox.valueChanged.connect(self.update_length)
        self.bpmSpinBox.valueChanged.connect(self.update_length)


        self.csSpinBox.setValue(8)
        self.arSpinBox.setValue(8)
        self.odSpinBox.setValue(8)
        self.lengthSpinBox.setValue(4)
        self.bpmSpinBox.setValue(200)
        self.repeatsSpinBox.setValue(50)
        self.beatDivisorSpinBox.setValue(4)
        self.commandTextEdit.setText("difficulty {}")
        self.process=None
        self.buffer=bytes()

        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.setInterval(10)

        self.editor.mapChanged.connect(self.run_command)
        self.updateTimer.timeout.connect(self.run_command)

        self.csSpinBox.valueChanged.connect(self.run_command)
        self.bpmSpinBox.valueChanged.connect(self.run_command)
        self.arSpinBox.valueChanged.connect(self.run_command)
        self.odSpinBox.valueChanged.connect(self.run_command)
        self.lengthSpinBox.valueChanged.connect(self.run_command)

        self.repeatsSpinBox.valueChanged.connect(self.run_command)
        self.commandTextEdit.returnPressed.connect(self.run_command)
        self.updateButton.clicked.connect(self.run_command)

        


    def get_length(self):
        bpm = self.bpmSpinBox.value()
        beatCount = self.lengthSpinBox.value()
        repeats = self.repeatsSpinBox.value()

        return (60/bpm) * beatCount * repeats

    def update_length(self):
        length = self.get_length()
        self.lengthLabel.setText(str(length))

    def save(self):
        file_name = self.out_file
        
        with open(file_name, "w") as f:
            OsuFile.save(
                f,
                points=self.editor.get_points(self.bpmSpinBox.value(), self.lengthSpinBox.value(), self.repeatsSpinBox.value()),
                cs=self.csSpinBox.value(),
                ar=self.arSpinBox.value(),
                od=self.odSpinBox.value(),
                bpm=self.bpmSpinBox.value(),
                version="-"
            )
    
    def processFinished(self):

        self.buffer += self.process.readAllStandardOutput().data()
        self.buffer += self.process.readAllStandardError().data()

        try:
            text = self.buffer.decode("utf-8")
        except UnicodeDecodeError:
            text= self.buffer.decode("CP437")
        
        self.output.setPlainText(text)
        self.process=None
        
    def readStdOut(self):
       pass

    def readStdErr(self):
        pass

    def run_command(self):
        if self.process is None or self.process.state() == QtCore.QProcess.ProcessState.NotRunning:       
            self.save()    
            self.buffer=bytes()
            command=self.commandTextEdit.text().format(os.path.realpath(self.out_file))
            if self.command_prefix is not None:
                command = " ".join((self.command_prefix, command))
            
            self.process = QtCore.QProcess(self)
            if self.command_dir is not None:
                self.process.setWorkingDirectory(self.command_dir)
            self.process.start(command)
            self.process.finished.connect(self.processFinished)
            self.process.readyReadStandardOutput.connect(self.readStdOut)
            self.process.readyReadStandardError.connect(self.readStdErr)
        else:
            self.updateTimer.start()
        
        
