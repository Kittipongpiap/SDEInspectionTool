'''
 Controller Board Database Serch Engine
 (c) All Right Reserved SDE Inspection Software 2024
'''

from sqlite_dbcon import db_connect
from utils import *
from PyQt6.QtGui import QStandardItemModel, QStandardItem

'''
SELECT * FROM db_sde.devices_income
WHERE create_at BETWEEN '2024-05-24 00:00:00' AND '2024-05-25 00:00:00';
'''

def onboard_show(ui):
    # Time Fram Set ==========================
    data_test = []
    select_time = ui.time_frame.currentIndex()
    select_type = ui.device_type.currentIndex()
    select_lot = ui.boxlot_finder.currentIndex()
    # Time Frame Management ===========================================================================================================================
    select_time_frame = [get_date_one_thousand_year_ago(),get_date_one_hour_ago(),get_date_one_day_ago(),get_date_one_week_ago(),get_date_one_month_ago(),get_date_one_year_ago()]
    in_between = "create_at BETWEEN '"+select_time_frame[select_time]+"' AND '"+get_date_time_db()+"'"
    # Device Header Table  ======================================================================================
    data_Header = (["Date","Device ID","Type"],
                   ["Date","Device ID","HIGH","OFF","LOW","MID"],
                   ["Date","Device ID"," PM2.5(ug/m3) "," CO2(ppm) "," Temp(*C) "," Humid(%) "])
    # Device Data Condition =====================================================================================
    device_type = ['',"AND devices_type LIKE '%Actuator%' ","AND devices_type LIKE '%Sensor%' "] ### Edit to AC back
    nrf_id = ui.device_id_input.text()
    device_id  = ['',"AND device_id LIKE '%"+nrf_id+"%'"]
    if nrf_id == '' :
        search_id = device_id[0]
        ui.device_id_input.clear()
    else : 
        search_id = device_id[1]
        ui.device_id_input.clear()
    #============================================================================================================
    lot_number = ui.boxlot_finder.currentText()
    device_lot = ['',"AND lot_box_id = '"+lot_number+"' "]
    if select_lot == 0 :
        chosen_lot = device_lot[0]
    else :
        chosen_lot = device_lot[1]
    # Device Status Condition =====================================================================================
    device_status = ['',"AND inspec_note = 'GOOD' ","AND inspec_note = 'NG' "] ### Edit to AC back
    device_status_index = ui.mcu_status.currentIndex()
    if device_status_index == 0 :
        device_status_selected = ' '
    else :
        device_status_selected = device_status[device_status_index]
    #============================================================================================================
    # UI Set Text================================================================================================
    if select_time == 0 :
        set_time_text = "Time Frame : <span style=\"color:Green\">""All Data""</span></p>"
    else : 
        set_time_text = "Time Frame : <span style=\"color:Green\">"+select_time_frame[select_time]+   "     ---->   "   +get_date_time_db()+"</span></p>"
    #============================================================================================================
    # Select Data to Show
    f_select = ["create_at,device_id,devices_type"
                ,"create_at,device_id,current_1st,current_2nd,current_3rd,current_4th"
                ,"create_at,device_id,pm_2_5,scd_co2,scd_temp,scd_hum"]
    t_select = "db_sde.devices_income"
    c_select = ""+in_between+" "+device_type[select_type]+" "+search_id+"  "+device_status_selected+"  "+chosen_lot+" "
    ui.controller_finder_status.setText(set_time_text)
    db_con = db_connect()
    results = db_con.connect_select(t_select, c_select, f_select[select_type])
    for data in results:
        data_test.append(data)
    TableData(ui.devicesDataView, data_Header[select_type], data_test)
    pass

# Table View = ui.devicesTableData
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
