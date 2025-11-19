import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from sqlite_dbcon import db_connect
import JLink.log 
from utils import get_logger
# create.path(mac_id,lot_id,count)
# --> not NG devices to generate
# --> generate good device only
#      --> count = qty - ng_qty  

def qr_create_path(mac_id,lot_id) :
    # Create DIR for QR IMG ----------------------------------------------------------------------------------------------------------------
    qr_path = ("Output/"+lot_id+"")
    os.makedirs(qr_path, exist_ok=True)
    # Device Counter -------------------------
    counter = db_connect()
    counter_table = "db_sde.devices_income_lot"
    counter_condition = "lot_no = '"+lot_id+"'"
    counter_feild =  "good_product"
    results = counter.connect_select(counter_table,counter_condition,counter_feild)
    # Expecting a single row with one column (good_product). Fallback to 0 if missing.
    number = 0
    if results and len(results[0]) > 0 and results[0][0] is not None:
        try:
            number = int(results[0][0])
        except Exception:
            number = 0
    gen_qr(qr_path,mac_id,number)

logger = get_logger(__name__)

def gen_qr(qr_path, mac_id, number):
    # Generate and resize the QR code
    qr_data = mac_id
    qr_data1 = qr_data[0:6]
    qr_data2 = qr_data[6:] + "  "
    number = str(number)
    logger.debug(mac_id)
    img = qrcode.make(qr_data)
    qr_size = (250, 250)  # Resize dimensions (width, height)
    img = img.resize(qr_size, Image.LANCZOS)

    # Set up the font
    try:
        font = ImageFont.truetype("arial.ttf", 48)  # Use a TTF font file
    except IOError:
        font = ImageFont.load_default()  # Fallback if 'arial.ttf' isn't available

    # Calculate dimensions for text
    qr_data1_bbox = font.getbbox(qr_data1)
    qr_data1_width = qr_data1_bbox[2] - qr_data1_bbox[0]
    qr_data1_height = qr_data1_bbox[3] - qr_data1_bbox[1]

    qr_data2_bbox = font.getbbox(qr_data2)
    qr_data2_width = qr_data2_bbox[2] - qr_data2_bbox[0]
    qr_data2_height = qr_data2_bbox[3] - qr_data2_bbox[1]

    number_bbox = font.getbbox(number)
    number_width = number_bbox[2] - number_bbox[0]
    number_height = number_bbox[3] - number_bbox[1]

    # Calculate final image size
    final_width = img.width + max(qr_data1_width, qr_data2_width, number_width) + 20  # Add padding
    final_height = img.height  # Keep QR code height

    # Create a new image with a white background
    final_img = Image.new("RGB", (final_width, final_height), "white")

    # Paste the resized QR code onto the final image
    final_img.paste(img, (0, 0))

    # Draw the text beside the QR code
    draw = ImageDraw.Draw(final_img)
    text_x = img.width + 10  # Padding from QR code
    line_spacing = 10  # Spacing between lines

    # Line 1: qr_data1
    line1_y = 30  # Starting offset from the top
    draw.text((text_x, line1_y), qr_data1, font=font, fill="black")

    # Line 2: qr_data2
    line2_y = line1_y + qr_data1_height + line_spacing + 20
    draw.text((text_x, line2_y), qr_data2, font=font, fill="black")

    # Line 3: number
    line3_y = line2_y + qr_data2_height + 40
    draw.text((text_x, line3_y), number, font=font, fill="black")

    # Save the final image
    img_name = f"{number}_{qr_data}"
    final_img.save(os.path.join(qr_path, f"{img_name}.png"))
    logger.info(f"QR saved as {os.path.join(qr_path, f'{img_name}.png')}")

# CSV Generator ---------------------------------------------------------------------------------------------------------------------------
def csv_create_dir(ui) :
    # Create DIR for QR IMG ----------------------------------------------------------------------------------------------------------------
    dir_path = ("EXPORT_RAW_DATA")
    os.makedirs(dir_path, exist_ok=True)
    # Device Counter -------------------------
    select_data_csv(ui)

def select_data_csv(ui) :
    # Create Device Type DIR -------------------------------------
    type_data = db_connect()
    lot_no = ui.alive_lot_box.currentText()
    type_table = "db_sde.devices_income"
    type_condition = "lot_box_id = '"+lot_no+"' "
    type_feild =  "devices_type"
    type_rows = type_data.connect_select(type_table,type_condition,type_feild)
    # Determine device type from first row (if any)
    if type_rows and len(type_rows[0]) > 0 and type_rows[0][0]:
        device_type = str(type_rows[0][0])
    else:
        device_type = "UnknownType"
    logger.debug(device_type)
    logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #-------------------------------------------------------------
    csv_path = ("EXPORT_RAW_DATA/"+device_type+"")
    os.makedirs(csv_path, exist_ok=True)
    csv_file_path = ("EXPORT_RAW_DATA/"+device_type+"/"+lot_no+".csv")
    # Select Data to Insert in CSV Files -------------------------
    actuator_data_feilds = ("SELECT create_at,device_id,devices_type,inspec_note, "
                        "in_range.max_pm_2_5,in_range.min_pm_2_5, "
                        "in_range.max_scd_hum,in_range.min_scd_hum, "
                        "in_range.max_scd_temp,in_range.min_scd_temp, "
                        "in_range.max_scd_co2,in_range.min_scd_co2, "
                        "sw_1st,current_1st,sw_2nd,current_2nd,sw_3rd,current_3rd,sw_4th,current_4th,lot_box_id,issue_name,print_stat,firmware_version "
                        "FROM db_sde.devices_income as di "
                        "left join db_sde.devices_income_range as in_range on di.state_id = in_range.state_id "
                        "WHERE lot_box_id like '%"+lot_no+"%' ; ")
    
    sensor_data_feilds = ("SELECT create_at,device_id,devices_type,inspec_note, "
                        "in_range.max_pm_2_5,in_range.min_pm_2_5, "
                        "in_range.max_scd_co2,in_range.min_scd_co2, "
                        "in_range.max_scd_temp,in_range.min_scd_temp, "
                        "in_range.max_scd_hum,in_range.min_scd_hum, "
                        "pm_2_5,scd_co2,scd_temp,scd_hum,lot_box_id,issue_name,print_stat,firmware_version "
                        "FROM db_sde.devices_income as di "
                        "left join db_sde.devices_income_range as in_range on di.state_id = in_range.state_id "
                        "WHERE lot_box_id like '%"+lot_no+"%' ; ")
    # Create Data Set----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    raw_data = db_connect()
    if device_type.startswith("Actuator") :
        header = ["Time-Stamp","DeviceID", "DeviceType","Status","MAX_High_Current","MIN_High_Current", "MAX_Mid_Current","MIN_Mid_Current", "MAX_Low_Current","MIN_Low_Current", "MAX_Off_Current","MIN_Off_Current", "SW1","Current-1", "SW2","Current-2", "SW3","Current-3", "SW4","Current-4","Lot_ID","Issue-Name","Print_Status","Firmware_Version"]
        data_feild = actuator_data_feilds
        rows = raw_data.connect_select_join(data_feild)
    elif device_type.startswith("Sensor") :
        header = ["Time-Stamp","DeviceID", "DeviceType","Status", "MAX_pm2_5","MIN_pm2_5", "MAX_scd_co2","MIN_scd_co2", "MAX_scd_temp","MIN_scd_temp", "MAX_scd_hum","MIN_hum","pm_2_5","scd_co2","scd_temp","scd_hum","Lot_ID","Issue-Name","Print_Status","Firmware_Version"]
        data_feild = sensor_data_feilds
        rows = raw_data.connect_select_join(data_feild)
        logger.debug("Sensor")
    else:
        # Unknown device type; still attempt to export using sensor fields as a generic fallback
        header = ["Time-Stamp","DeviceID", "DeviceType","Status", "MAX_pm2_5","MIN_pm2_5", "MAX_scd_co2","MIN_scd_co2", "MAX_scd_temp","MIN_scd_temp", "MAX_scd_hum","MIN_hum","pm_2_5","scd_co2","scd_temp","scd_hum","Lot_ID","Issue-Name","Print_Status","Firmware_Version"]
        data_feild = sensor_data_feilds
        rows = raw_data.connect_select_join(data_feild)
    raws_data_list = []
    for raws in (rows or []):
        raws_data_list.append(raws)
    JLink.log.write_csv(header,raws_data_list,csv_file_path)
    #Show Status -------------------------------------------
    ui.insign_status_2.setText(
    "<span style=\"color:WHITE\">Status : </span></p>   <span style=\"color:#4CAF50\">Export Data Success</span></p>")
    #-------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
