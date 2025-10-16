from sqlite_dbcon import db_connect
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import JLink.ui_funciton as uif
import JLink.db_controller as db_mcu
import JLink.insign_db as insgin_db
from utils import *
from PyQt5.QtWidgets import QMessageBox,QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject ,Qt
from PyQt5.QtGui import QFont
dt_string = get_date_time()
import JLink.log

def range_on_display(ui) :
    TyIndex = ui.programFileComboBox.currentIndex()
    val_type = ['Current_Value','Sensor_Value']
    cel_fl_done = []
    field = ["max_pm_2_5,max_scd_co2,max_scd_temp,max_scd_hum","min_pm_2_5,min_scd_co2,min_scd_temp,min_scd_hum"]
    for cel_fl_value in range(2) :
        cel_fl_range = db_connect()
        table = "db_sde.devices_income_range"
        condition = "value_type = '"+val_type[TyIndex]+"'"
        #field = "value_type,pm_2_5,scd_co2,scd_temp,scd_hum"
        results = cel_fl_range.connect_select(table, condition, field[cel_fl_value])
        for data in results:
            cel_fl_done.append(data)
    print(cel_fl_done)
    columnHeaders = [[" HIGH LEVEL "," OFF "," LOW LEVEL "," MID LEVEL "],[" PM2.5(ug/m3) "," CO2(ppm) "," Temp(*C) "," Humid(%) "]]
    # Defensive: ensure we have at least two rows (min and max) with 4 columns each
    if len(cel_fl_done) >= 2 and all(len(row) >= 4 for row in cel_fl_done[:2]):
        cel_fl_dude = [(""+cel_fl_done[1][0]+"-"+cel_fl_done[0][0]+"",""+cel_fl_done[1][1]+"-"+cel_fl_done[0][1]+"",""+cel_fl_done[1][2]+"-"+cel_fl_done[0][2]+"",""+cel_fl_done[1][3]+"-"+cel_fl_done[0][3]+""),]
        TableData(ui.sensorRangeView, columnHeaders[TyIndex], cel_fl_dude)
    else:
        # Not enough range data — display placeholders
        cel_fl_dude = [("N/A","N/A","N/A","N/A")]
        TableData(ui.sensorRangeView, columnHeaders[TyIndex], cel_fl_dude)


def TableData(tableView, columnHeaders, data):
    # Create a model and set it for the table view
    model = QStandardItemModel()
    tableView.setModel(model)

    # Set column headers
    model.setHorizontalHeaderLabels(columnHeaders)

    # Populate the model with data
    for row in data:
        item_list = [QStandardItem(str(item)) for item in row]
        model.appendRow(item_list)

    tableView.resizeColumnsToContents()

# Sensor Coperator ====================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton

class CustomAlertDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notification")
        
        # Set fixed size for the dialog
        self.setFixedSize(500, 300)  # Adjust as needed

        # Set a larger font for the message
        font = QFont()
        font.setPointSize(15)

        # Create a label and set the message text
        label = QLabel(message)
        label.setFont(font)
        label.setWordWrap(True)

        # Create a button to close the dialog
        close_button = QPushButton("OK")
        close_button.clicked.connect(self.accept)

        # Conditionally apply background color
        if message.startswith("GOOD") or message.startswith("Process Finish") :
            label.setStyleSheet("background-color: green; color: white; font-size:100px")
            label.setAlignment(Qt.AlignCenter)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;  /* Green background */
                    color: white;  /* White text */
                    font-size: 26px;  /* Font size */
                    padding: 10px 20px;  /* Padding */
                    border-radius: 10px;  /* Rounded corners */
                }
                QPushButton:hover {
                    background-color: #45a049;  /* Darker green on hover */
                }
            """)
        elif message.startswith("NG"):
            label.setStyleSheet("background-color: red; color: white; font-size: 100px;")
            label.setAlignment(Qt.AlignCenter)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;  /* Green background */
                    color: white;  /* White text */
                    font-size: 26px;  /* Font size */
                    padding: 10px 20px;  /* Padding */
                    border-radius: 10px;  /* Rounded corners */
                }
                QPushButton:hover {
                    background-color: #d32f2f;  /* Darker green on hover */
                }
            """)
        else :
            label.setStyleSheet("background-color: #FFBF00; font-size: 50px; color: white;")
            label.setAlignment(Qt.AlignCenter)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #f86f15;  /* Green background */
                    color: white;  /* White text */
                    font-size: 26px;  /* Font size */
                    padding: 10px 20px;  /* Padding */
                    border-radius: 10px;  /* Rounded corners */
                }
                QPushButton:hover {
                    background-color: #fbee0f;  /* Darker green on hover */
                }
            """)
        # Set a stylesheet for the button

        # Arrange widgets in a layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(close_button)
        self.setLayout(layout)

class AlertHelper(QObject):
    show_alert_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def show_alert(self, message):
        # Use custom dialog instead of QMessageBox
        dialog = CustomAlertDialog(message)
        dialog.exec_()

alert_helper = AlertHelper()
alert_helper.show_alert_signal.connect(alert_helper.show_alert)

def Comparator(ui,mac_id,controller_type,first_stack,second_stack) :
    global note
    m_curr_stack = []
    val_type = ['Current_Value','Sensor_Value']
    curr_done = []
    if controller_type.startswith("Actuator") :
        for current in second_stack : 
            curr_int = int(current[:2])
            print(curr_int)
            m_curr_stack.append(curr_int)
        val_type_dif = val_type[0]
        m_curr_stack = m_curr_stack[1:]
    elif controller_type.startswith("Sensor") :
        m_curr_stack = [int(first_stack[1]),int(second_stack[0]),int(second_stack[1]),int(second_stack[2])]
        val_type_dif = val_type[1]
    #--------------------------------------------------------------------
    print(m_curr_stack)
    print("--------->>>>")
    #-------------------------------------------------- Import Range 
    field = ["max_pm_2_5,max_scd_co2,max_scd_temp,max_scd_hum","min_pm_2_5,min_scd_co2,min_scd_temp,min_scd_hum"]
    for get_value in range(2) :
        curr_range = db_connect()
        table = "db_sde.devices_income_range"
        condition = "value_type = '"+val_type_dif+"'"
        #field = "value_type,pm_2_5,scd_co2,scd_temp,scd_hum"
        results = curr_range.connect_select(table, condition, field[get_value])
        for data in results:
            curr_done.append(data)
    min_data = curr_done[1]
    max_data = curr_done[0]
    all_note = []
    for the_range in range(4) :
        if int(min_data[the_range]) < m_curr_stack[the_range] <  int(max_data[the_range]) :
            note = 'GOOD'
        else :
            note = 'NG'
            #update_invalid_value(controller_type)
            alert_helper.show_alert_signal.emit(note)
            break
        all_note.append(note)
    #--------------------------------------------------------------------
    print("Result ----->")
    print(all_note)
    db_mcu.device_update(ui,mac_id,controller_type,first_stack,second_stack,note)
    uif.onboard_data_ui(ui,controller_type,first_stack,second_stack,note)
    insgin_db.incoming_list(ui,0)
    JLink.log.update_print_label_by_mac_id(mac_id)
    if note.startswith("GOOD") :
        alert_helper.show_alert_signal.emit(note)
    pass

def return_status() : 
    print(note)
    return note

def update_invalid_value(controller_type) :
    if controller_type.startswith("Actuator") :
        select_issue = db_connect()
        table = "db_sde.devices_income_range"
        issue = 'qty_ng_product'
    select_issue.connect_select()
    pass