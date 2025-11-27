from JLink.ui_function import *
import serial.tools.list_ports
import JLink.serialReader as srr
import JLink.insign_db as insign_db 
from JLink.controller_data import *
from PyQt5.QtGui import QIntValidator
from JLink.limitter import *
import media_generator as media_gen
from PyQt5.QtWidgets import QWidget, QVBoxLayout

def set_lineedit_int_only(line_edit):
    validator = QIntValidator()
    line_edit.setValidator(validator)

def button_interface(ui):
    # Helper Functions
    #ui.show_done_lot.stateChanged.connect(lambda: on_checkbox_state_changed(ui))
    #set_lineedit_int_only(ui.income_qt) 
    def connect_buttons(buttons, function):
        for button in buttons:
            button.clicked.connect(function)
    def connect_pages(buttons, page):
        for button in buttons:
            button.clicked.connect(lambda: change_page(ui, page))
    # MENU BAR ===========================================================================
    #insign_db.incoming_list(ui,0)
    populate_table_view(ui.devicesTableView, header, mac_id_list)
    onboard_show(ui)
    check_com_ports(ui)
    insign_db.lot_id_box(ui)
    #ui.big_export_btn.hide()
    #=====================================================================================
    #ui.mini_menu.hide()
    #ui.mini_controller_btn.hide()
    ui.big_controller_btn.hide()
    connect_buttons([ui.big_menu_btn], lambda: check_com_ports(ui))
    connect_buttons([ui.finish_test], lambda: insign_db.finish_lot())
    connect_buttons([ui.finish_test], lambda: insign_db.incoming_list(ui,0))
    connect_pages([ui.finish_test], 3)
    connect_buttons([ui.finish_test], lambda: hide_for_export(ui))
    def hide_for_export(ui) :
        ui.big_controller_btn.hide()
        ui.big_insign_bt.show()
        ui.big_db_btn.hide()
    connect_buttons([ui.big_controller_btn, ui.big_controller_btn], lambda: insign_db.lot_id_box(ui))
    connect_buttons([ui.big_db_btn], lambda: onboard_show(ui))
    connect_pages([ui.big_controller_btn], 0)
    connect_pages([ui.big_db_btn], 1)
    connect_pages([ui.big_insign_bt], 2)
    #connect_buttons([ui.big_insign_bt], lambda: on_checkbox_state_changed(ui))
    connect_buttons([ui.big_insign_bt,ui.lot_finder_butto], lambda: insign_db.lot4export(ui))
    # Device Config Bar ==================================================================
    ui.powerOffButton.clicked.connect(lambda: power_on_event(ui))
    ui.powerOnButton.clicked.connect(lambda: power_off_event(ui))
    ui.programFileComboBox.currentIndexChanged.connect(lambda: range_on_display(ui))
    # Controller Page ====================================================================
    connect_buttons([ui.flashButton], lambda: flash_config(ui))
    connect_buttons([ui.clearListButton], lambda: clear_list_event(ui))
    # Insign Page ========================================================================
    connect_buttons([ui.income_submit], lambda: insign_db.incoming_device(ui))
    # connect_buttons([ui.income_submit], lambda: insign_db.lot_id_box(ui))
    connect_pages([ui.income_submit], 0) 

    connect_pages([ui.big_export_btn], 3)
    connect_buttons([ui.big_export_btn], lambda: insign_db.incoming_list(ui,1))
     

    connect_buttons([ui.export_document_butt], lambda: media_gen.csv_create_dir(ui))
    # Controller Data ====================================================================
    connect_buttons([ui.controller_finder], lambda: onboard_show(ui))
    ui.big_db_btn.hide()

def addGood_action(ui) :
    print(ui.boxlot_Box.count())
    if ui.boxlot_Box.count() :
        add_good_device_event(ui)
    else :
        ui.flashStatusLabel.setText(
        "Device Status : <span style=\"color:RED\">Not Found Lot No.</span></p>")

def reject_action(ui) :
    print(ui.boxlot_Box.count())
    if ui.boxlot_Box.count() :
        add_bad_device_event(ui)
    else :
        ui.flashStatusLabel.setText(
        "Device Status : <span style=\"color:RED\">Not Found Lot No.</span></p>")

def check_com_ports(ui):
    ports = serial.tools.list_ports.comports()
    ui.uart_portBox.clear()
    for port in ports:
        port_info = {
            'device': port.device,
            'description': port.description
        }
        #print(port.description)
        if port.description.startswith("USB Serial Port") :
            ui.uart_portBox.addItem(port.device)

def ComboBoxInitialize(ui):
    program_combobox_click_event(ui)

def change_page(ui, index):
    ui.main_page.setCurrentIndex(index)
    page_color(ui)
    check_com_ports(ui)

def page_color(ui):
    # Get the current index of the main page
    index = ui.main_page.currentIndex()
    # Define the styles for highlighting and un-highlighting buttons
    highlight_style = "text-align:left;color:white;background-color:#f44336;border-radius:0px;padding:5px 10px;"
    un_highlight_style = "text-align:left;color:white;background-color:#222222;border-radius:0px;padding:5px 10px;"

    # List of tuples containing big and mini buttons for each section
    buttons = [
        (ui.big_controller_btn),
        (ui.big_db_btn),
        (ui.big_insign_bt),
        (ui.big_export_btn),
        #(ui.big_set_range_bt, ui.mini_set_range_bt),
    ]
    
    # Iterate over buttons and set the appropriate style
    for i, (big_btn) in enumerate(buttons):
        style = highlight_style if index == i else un_highlight_style
        big_btn.setStyleSheet(style)
    
def serial_switching_readMode(ui) :
    srr.start_reading(ui)
    ui.serial_r.setChecked(True)
    ui.serial_s.setChecked(False)
    pass
# =============================================
def serial_switching_stopMode(ui) :
    srr.stop_reading(ui)
    ui.serial_s.setChecked(True)
    ui.serial_r.setChecked(False)
    pass
# =============================================
def on_checkbox_state_changed(ui) :
    if ui.show_done_lot.isChecked():
        insign_db.incoming_list(ui,1)
        insign_db.lot4export(ui)
        ui.lot_finder.clear()
    else:
        insign_db.incoming_list(ui,0)
        insign_db.lot4export(ui)
        ui.lot_finder.clear()