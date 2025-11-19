from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt

app = QApplication([])

window = QWidget()
layout = QVBoxLayout(window)

line = QLineEdit()
line.setPlaceholderText("Enter your name...")
line.setEchoMode(QLineEdit.Normal)
line.textChanged.connect(lambda t: print("Text changed:", t))
line.returnPressed.connect(lambda: print("Return pressed!"))
layout.addWidget(line)

window.show()
app.exec_()
