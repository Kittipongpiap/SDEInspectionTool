import os
import threading
import JLink.jlink as jlink
import JLink.log as log
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor,QFont
from utils import *
import JLink.serialReader as srr
import JLink.db_controller as db_controller
import JLink.ui_maneger  as UIM
import JLink.db_controller as db_controller
import JLink.limitter as pop_up

mac_id_list = []
mcu_data_list = []
header = ['Device ID', 'Note','Data']


def power_on_event(ui):
    ui.powerOnButton.setChecked(False) 
    ui.powerOffButton.setChecked(True)
    jlink.power_on()
    print("Power On")


def power_off_event(ui):
    ui.powerOnButton.setChecked(True) 
    ui.powerOffButton.setChecked(False)
    jlink.power_off()
    print("Power Off")

def flash_config(ui) :
    flash_event(ui)
def erase_event(ui):
    #recover = jlink.recover()
    erase = jlink.eraseall()
    jlink.recover()
    jlink.eraseall()
    if  erase :
        ui.flashStatusLabel.setText(
            "Erase Status : <span style=\"color:Green\">Erase All</span></p>")
    else :
        ui.flashStatusLabel.setText(
            "Erase Status : <span style=\"color:RED\">Erase All</span></p>")
    pass


def flash_event(ui):
    thr = threading.Thread(target=flashing_thread_callback, args=[ui])
    thr.start()
    ui.flashStatusLabel.setText(
        "Programming Status : <span style=\"color:orange\">In Progress</span></p>")


def flashing_thread_callback(ui):
    jlink.power_on()
    my_firmware_ = inspection_fw_path(ui)
    result = jlink.flash_program(os.path.join(
        "JLink/program_files/TestFW", my_firmware_))
    if result:
        ui.flashStatusLabel.setText(
            "Programming Status : <span style=\"color:green\">Success</span></p>")
        jlink.reset()
        UIM.addGood_action(ui)
    else:
        ui.flashStatusLabel.setText(
            "Programming Status : <span style=\"color:red\">Fail</span></p>")
        issue = 'Primary Flash Failed'
        db_controller.error_inbetween(ui,issue)

# def ap_flash_event(ui):
#     thr = threading.Thread(target=ap_flashing_thread_callback, args=[ui])
#     thr.start()
#     ui.flashStatusLabel.setText(
#         "Programming Status : <span style=\"color:orange\">In Progress</span></p>")


# def ap_flashing_thread_callback(ui):
#     jlink.power_on()
#     result = jlink.flash_program(os.path.join(
#         "JLink/program_files", ui.programFileComboBox.currentText()))
#     if result:
#         ui.flashStatusLabel.setText(
#             "Programming Status : <span style=\"color:green\">AP Programming Success</span></p>")
#         jlink.protection()
#     else:
#         ui.flashStatusLabel.setText(
#             "Programming Status : <span style=\"color:red\">AP Programming Fail</span></p>")

def afterLife_event(ui):
    thr = threading.Thread(target=afterLife_event_thread_callback, args=[ui])
    thr.start()
    ui.flashStatusLabel.setText(
        "Status : <span style=\"color:orange\">Production In Progress</span></p>")


def afterLife_event_thread_callback(ui):
    print(ui.programFileComboBox.currentIndex()) ### Marking ###
    my_firmware_ = production_fw_path(ui)
    jlink.power_on()
    result = jlink.flash_program(os.path.join(
        "JLink/program_files/ProductionFW", my_firmware_))
    if result:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:green\">Process Finish</span></p>")
        #jlink.protection()
        message = "Process Finish"
        pop_up.alert_helper.show_alert_signal.emit(message)
    else:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:red\">Process Fail</span></p>")
        issue = "Secoundary Flash Failed"
        db_controller.error_inbetween(ui,issue)

# Old Ways
def inspection_fw_path(ui):
    program_files_folder = "JLink/program_files/TestFW"
    firmware_type = ui.programFileComboBox.currentIndex()
    # Check if the folder exists
    if os.path.exists(program_files_folder) and os.path.isdir(program_files_folder):
        # Get a list of file names in the folder
        file_names = os.listdir(program_files_folder)
        # Filter out only the files (not directories) and add them to the combobox
        #print(file_names[firmware_type])
        return file_names[firmware_type]

def production_fw_path(ui):
    program_files_folder = "JLink/program_files/ProductionFW"
    firmware_type = ui.programFileComboBox.currentIndex()
    # Check if the folder exists
    if os.path.exists(program_files_folder) and os.path.isdir(program_files_folder):
        # Get a list of file names in the folder
        file_names = os.listdir(program_files_folder)
        # Filter out only the files (not directories) and add them to the combobox
        #print(file_names[ui.programFileComboBox.currentIndex()])
        return file_names[firmware_type]

def program_combobox_click_event(ui):
    devices_type = ["Actuator Controller","Sensor Controller"]
    # Clear the current items in the combobox
    currentText = ui.programFileComboBox.currentText()
    ui.programFileComboBox.clear()
    # Add Devices Type
    for devices in devices_type :
        ui.programFileComboBox.addItem(devices)
        ui.programFileComboBox.setCurrentText(currentText)
        data = production_fw_path(ui)
    print(data)

def add_good_device_event(ui):
    global mac_id_list
    # jlink.power_on()
    mac_id = jlink.mac_id_check()
    if not mac_id:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:red\">Read Device ID Fail</span></p>")
        issue = "Read Device ID Fail"
        db_controller.error_inbetween(ui,issue)
        return

    is_mac_id_duplicated = check_value_in_lists(mac_id_list, mac_id)

    if is_mac_id_duplicated:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:red\">Device ID are Duplicated, Press <span style=\"color:blue\">Clear</span></p> Button for RETEST</span></p>")
        issue = "Device ID are Duplicated"
        db_controller.error_inbetween(ui,issue)
        return
    else:
            srr.testing_event(ui)
            message = "Inspection In Progress, PRESS S1"
            pop_up.alert_helper.show_alert_signal.emit(message)
            #mac_id_list.append([mac_id, 'GOOD',''])
            mac_id_list.append([mac_id, 'GOOD']) ##### Old
            if len(mac_id_list) == 3:
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(mac_id_list)
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                log.write_csv(['macID', 'note'], mac_id_list, "JLink/database/devices.csv")
                # for device in mac_id_list:
                #     log.update_print_label_by_mac_id(device[0])
                mac_id_list = []


    
def add_bad_device_event(ui):  #### UPDATE
    jlink.power_on()
    global mac_id_list
    global mcu_data_list
    global header
    device_id = jlink.mac_id_check()
    timestamp = get_date_time()
    if not device_id:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:red\">Read Device ID Fail</span></p>")
        return
    is_mac_id_duplicated = check_value_in_lists(mac_id_list, device_id)
    if is_mac_id_duplicated:
        ui.flashStatusLabel.setText(
            "Status : <span style=\"color:red\">Device ID are Duplicated</span></p>")
        return
    else:
        device_type = ui.error_type_box.currentIndex()
        device_type_real = ["All","Actuator Controller 3CH","Sensor Controller"]
        db_controller.reject_device(ui,device_id,device_type_real[device_type],timestamp)
        note = ui.error_point_Box.currentText()
        mac_id_list.append([device_id, 'NG',note])
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(mac_id_list)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        if len(mac_id_list) == 3:
            mcu_data_list = []
        mcu_data_list.append([device_id, 'NG',note])
        if len(mac_id_list) == 3:
            log.write_csv(['macID', 'note'], mac_id_list, "JLink/database/devices.csv")
            for device in mac_id_list:
                print(device)
                #log.update_print_label_by_mac_id(device[0])
            mac_id_list = []
            mcu_data_list = []
        populate_table_view(ui.devicesTableView, header, mcu_data_list)

def clear_list_event(ui):
    global mac_id_list
    global mcu_data_list
    mac_id_list = []
    mcu_data_list = []

    ui.flashStatusLabel.setText(
            "Device Status : <span style=\"color:green\">Clear Table</span></p>")
    populate_table_view(ui.devicesTableView, header, mac_id_list)



def print_now_event(ui):
    global mac_id_list
    global mcu_data_list
    log.write_csv(['macID', 'note'], mac_id_list, "JLink/database/devices.csv")
    print("taeeeeeeeeeeeeeeeeeeeEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEeeeeeeeeeee")
    print(mac_id_list)
    print("taeeeeeeeeeeeeeeeeeeeEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEeeeeeeeeeee")
    for device in mac_id_list:
        log.update_print_label_by_mac_id(device[0])  # device 0 equal macId
    mac_id_list = []
    mcu_data_list = []

    populate_table_view(ui.devicesTableView, header, mac_id_list)
    ui.flashStatusLabel.setText(
            "Status : <span style=\"color:green\">Create Device Barcode</span></p>")

def onboard_data_ui(ui,type,data1,data2,note) :
    global mcu_data_list
    jlink.power_on()
    mac_id = jlink.mac_id_check()
    pm_all = []
    scd_all = []
    level_all = []
    current_all = []
    if type == 'Sensor Controller' :
        if len(mcu_data_list) == 3:
            mcu_data_list = []
        header = ['Device ID', 'Note',' PM2.5(ug/m3) ',' CO2(ppm) ',' Temp(*C) ',' Humid(%) ']
        for pm in data1 :
            pm_all.append(pm)
        for scd in data2 :
            scd_all.append(scd)
        mcu_data_list.append([mac_id,note,pm_all[1],scd_all[0],scd_all[1],scd_all[2]])
        #populate_table_view(ui.devicesTableView, header, mcu_data_list)
        pass
    elif type == 'Actuator Controller 3CH' :
        if len(mcu_data_list) == 3:
            mcu_data_list = []
        for level in data1 :
            if level == '3' :
                level = 'HIGH'
            elif level == '2' :
                level = 'MID'
            elif level == '1' :
                level = 'LOW'
            else :
                level = 'OFF'
            level_all.append(level)
        for current in data2 :
             current_all.append(current)
        current_all = current_all[1:]
        print(current_all)
        header = [' Device ID ', 'Note',level_all[0],level_all[1], level_all[2], level_all[3]]
        mcu_data_list.append([mac_id,note,current_all[0],current_all[1],current_all[2],current_all[3]])
        pass
    # if len(mcu_data_list) == 3:
    #     mcu_data_list = []
    print(mcu_data_list)
    populate_table_view(ui.devicesTableView, header, mcu_data_list)

# def populate_table_view(tableView, columnHeaders, data):
#     # Create a model and set it for the table view
#     model = QStandardItemModel()
#     tableView.setModel(model)

#     # Set column headers
#     model.setHorizontalHeaderLabels(columnHeaders)

#     # Populate the model with data
#     for row in data:
#         item_list = [QStandardItem(str(item)) for item in row]
#         model.appendRow(item_list)
#         print("Taeeeeeeee")
#         print(row[1])
    
#     tableView.resizeColumnsToContents()
# Create a helper class with a signal to display alerts

def populate_table_view(tableView, columnHeaders, data):
    # Create a model and set it for the table view
    model = QStandardItemModel()
    tableView.setModel(model)

    # Set column headers
    model.setHorizontalHeaderLabels(columnHeaders)

    # Populate the model with data
    for row in data:
        item_list = []
        for i, item in enumerate(row):
            item_obj = QStandardItem(str(item))
            
            # Check if the item in the second column should be marked red
            if i == 1 :
                if str(item) == 'GOOD':
                    color = 'green'
                    bg_color = 'white'
                elif i == 1 and str(item) == 'NG':
                    color = 'red'
                    bg_color = 'black'
                item_obj.setForeground(QBrush(QColor(color)))
                # Set text to bold
                font = QFont()
                font.setBold(True)
                item_obj.setFont(font)
                item_obj.setBackground(QBrush(QColor(bg_color)))
            
            item_list.append(item_obj)
        model.appendRow(item_list)
        print(item_list)
        for item in item_list :
            tableView.resizeColumnsToContents()
    # Resize columns to fit contents
    #tableView.resizeColumnsToContents()
