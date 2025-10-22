from PyQt5 import QtWidgets
from ui import Ui_MainWindow
import sys
import JLink.ui_manager as page
import JLink.limitter as sensor_range
import JLink.insign_db as insign_db 


def ConnectUiWithEvent(ui):
    page.button_interface(ui)
  
class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui  # Store the ui reference

if __name__ == "__main__":
    # insign_db.finish_lot()
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    MainWindow = MyMainWindow(ui)
    ui.setupUi(MainWindow)
    ConnectUiWithEvent(ui)
    page.ComboBoxInitialize(ui)
    page.page_color(ui)
    sensor_range.range_on_display(ui)
    #page.list_com_ports()
    MainWindow.show()
    sys.exit(app.exec_())
