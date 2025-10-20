
from sqlite_dbcon import db_connect
from utils import *
dt_string = get_date_time()
import JLink.insign_db as insign_db
import JLink.ui_function as uif
import media_generator as qr_gen
import JLink.limitter as comperator
import JLink.limitter as pop_up

def device_update(ui,mac_id,controller_type,first_stack,second_stack,note): 
    # Check Duplicate Device ID ===================================
    print(controller_type)
    f_select = "device_id"
    t_select = "db_sde.devices_income"
    box_lot_id = ui.boxlot_Box.currentText()
    c_select = None
    port_array = []
    db_con = db_connect()
    results = db_con.connect_select(t_select, c_select, f_select)
    #==============================================================
    fw_version = uif.production_fw_path(ui)
    #==============================================================
    this_mac_con = db_connect()
    condition = "device_id = '"+mac_id+"' AND lot_box_id = '"+box_lot_id+"' AND inspec_note = 'GOOD' "
    this_mac_results = this_mac_con.connect_select(t_select, condition, f_select)
    this_mac_array = []
    for this_mac in this_mac_results:
        this_mac_array.append(this_mac[0])
    if note.startswith('GOOD') :
        qty_status = 'good_product'
        insign_db.addDevice_action(ui,qty_status,controller_type)
    elif note.startswith('NG') :
        qty_status = 'ng_product'
        insign_db.addDevice_action(ui,qty_status,controller_type)
    state_id = str(ui.programFileComboBox.currentIndex())
    print(state_id)
    #=============================================================
    if controller_type.startswith('Sensor Controller') :
            data = [
                    ['pm_1',str(first_stack[0])],
                    ['pm_2_5',str(first_stack[1])],
                    ['pm_10',str(first_stack[2])],
                    ['scd_co2',str(second_stack[0])],
                    ['scd_temp',str(second_stack[1])],
                    ['scd_hum',str(second_stack[2])],
                    ['firmware_version',fw_version], ## FW version
                    ['inspec_note',note],
                    ['issue_name',''],
                    ['create_at',dt_string],
                    ['lot_box_id',box_lot_id],
                    ['state_id',state_id]
                    ]
            fill_db = [note,"","0"]
            sensor_db_value = "('"+mac_id+"','"+fill_db[0]+"','"+controller_type+"','"+str(first_stack[0])+"','"+str(first_stack[1])+"','"+str(first_stack[2])+"','"+str(second_stack[0])+"','"+str(second_stack[1])+"','"+str(second_stack[2])+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+box_lot_id+"','"+state_id+"','"+fill_db[1]+"','"+fill_db[2]+"','"+fw_version+"','"+dt_string+"')"
            print(sensor_db_value)
            device_db_table = "db_sde.devices_income"
            device_sensor = db_connect()
            device_sensor.connect_insert(device_db_table,sensor_db_value)
            # QR Generator --------------------------------------------------
            if len(this_mac_array) == 0  and note.startswith('GOOD'):
                    qr_gen.qr_create_path(mac_id,box_lot_id)
    #===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
    if controller_type.startswith('Actuator Controller 3CH') :
            level_all = []
            for level in first_stack :
                if level.startswith('3') :
                    level_st = 'HIGH'
                elif level.startswith('2') :
                    level_st = 'MID'
                elif level.startswith('1') :
                    level_st = 'LOW'
                else :
                    level_st = 'OFF'
                level_all.append(level_st)
            print(level_all)
            print("----------------------------------------->")
            data = [
                    ['sw_1st',level_all[0]],
                    ['current_1st',second_stack[1]],
                    ['sw_2nd',level_all[1]],
                    ['current_2nd',second_stack[2]],
                    ['sw_3rd',level_all[2]],
                    ['current_3rd',second_stack[3]],
                    ['sw_4th',level_all[3]],
                    ['current_4th',second_stack[4]],
                    ['firmware_version',fw_version], 
                    ['issue_name',''], 
                    ['inspec_note',note],
                    ['create_at',dt_string],
                    ['lot_box_id',box_lot_id],
                    ['state_id',state_id]
                    ]
            fill_db = ["GOOD","","0"]
            actuator_db_value = "('"+mac_id+"','"+note+"','"+controller_type+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+fill_db[1]+"','"+level_all[0]+"','"+second_stack[1]+"','"+level_all[1]+"','"+second_stack[2]+"','"+level_all[2]+"','"+second_stack[3]+"','"+level_all[3]+"','"+second_stack[4]+"','"+box_lot_id+"','"+state_id+"','"+fill_db[1]+"','"+fill_db[2]+"','"+fw_version+"','"+dt_string+"')"
            print(actuator_db_value)
            device_db_table = "db_sde.devices_income"
            device_actuator = db_connect()
            device_actuator.connect_insert(device_db_table,actuator_db_value)
            # QR Generator --------------------------------------------------
            if len(this_mac_array) == 0  and note.startswith('GOOD'):
                    qr_gen.qr_create_path(mac_id,box_lot_id)
    #===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
    # Store Device ID =====================
    for port_data in results:
        #==================================
        port_array.append(port_data[0])
    #============================================================
        if mac_id == port_data[0] :
                print("Duplicated Device")
                for update in data :
                    where = "device_id = '"+mac_id+"'"
                    set_to = ""+update[0]+" = '"+(update[1])+"'"
                    #print(set_to)
                    #print("--------------------------------------------------------------------------------")
                    # db_con_up = db_connect()
                    # db_con_up.connect_update(t_select,set_to,where)
#==========================================================================================================================================================================================================================================================================================================================================================================================================================
def reject_device(ui,device_id,device_type,timestamp) :
    # Check Duplicate Device ID ===================================
    f_select = "device_id"
    t_select = "db_sde.devices_income"
    lot_no = ui.boxlot_Box.currentText()
    issue_name = ui.error_point_Box.currentText()
    #print(lot_no)
    c_select = None
    db_con = db_connect()
    results = db_con.connect_select(t_select, c_select, f_select)
    #=============================================================
    this_mac_con = db_connect()
    condition = "device_id = '"+device_id+"'"
    this_mac_results = this_mac_con.connect_select(t_select, condition, f_select)
    this_mac_array = []
    for this_mac in this_mac_results:
        print("====================================================")
        print(this_mac)
        this_mac_array.append(this_mac)
    if len(this_mac_array) != 0:
        ui.flashStatusLabel.setText(
            "Device Status : <span style=\"color:red\">Device ID are Duplicated</span></p>")
        return
    else :
        #=============================================================
        reject_data = db_connect()
        null = ''
        table = "db_sde.devices_income"
        value = "('"+device_id+"','NG','"+device_type+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+str(lot_no)+"','"+str(issue_name)+"','0','"+null+"','"+str(timestamp)+"')"
        reject_data.connect_insert(table,value)
        #==============================================================
        qty_status = 'ng_product'
        note = 'NG'
        comperator.alert_helper.show_alert_signal.emit(note)
        insign_db.addDevice_action(ui,qty_status,device_type)
    #==========================================================================================================================================================================================================================================================================================================================================================================================================================

def error_inbetween(ui,issue):
    lot_no = ui.boxlot_Box.currentText()
    #=============================================================
    count_lot = db_connect()
    count_table = "db_sde.devices_income_lot"
    condition = " lot_no = '"+lot_no+"'"
    field = 'qty_inspected,ng_product'
    count_results = count_lot.connect_select(count_table, condition, field)
    for counts in count_results:
        print(counts)
    count_result = counts
    print(count_result[0])
    error_id = lot_no +"_"+ str(count_result[0])
    print(error_id)
    #=============================================================
    reject_data = db_connect()
    null = ''
    table = "db_sde.devices_income"
    value = "('"+error_id+"','NG','Failure','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+null+"','"+lot_no+"','"+null+"','"+issue+"','"+null+"','"+null+"','"+dt_string+"')"
    print(value)
    reject_data.connect_insert(table,value)
    #==============================================================
    value_up = ["qty_inspected","ng_product"]
    for update in range(2) :
        increasing_ng_data = db_connect()
        in_table = "db_sde.devices_income_lot"
        in_condition = " lot_no = '"+lot_no+"'"
        up_date = count_result[update] + 1
        value_update = " "+value_up[update]+"  = '"+str(up_date)+"'"
        print(value_update)
        increasing_ng_data.connect_update(in_table,value_update,in_condition)
        insign_db.incoming_list(ui,0)
    pop_up.alert_helper.show_alert_signal.emit(issue)
