import csv
import os
from sqlite_dbcon import db_connect
from utils import *

def write_csv(fieldnames, data_list, file_path):
    pass
    # Check if the output file already exists and delete it
    if os.path.exists(file_path):
        os.remove(file_path)

    # Open the CSV file for writing
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write data rows
        for inner_list in data_list:
            if len(inner_list) == len(fieldnames):
                # Create a dictionary by zipping fieldnames and inner_list
                data_dict = dict(zip(fieldnames, inner_list))
                writer.writerow(data_dict)
            else:
                print(f"Skipping invalid data: {inner_list}")

def update_print_label_by_mac_id(mac_id):
    # Update Print Status - [ Table Name devices_incoming ]
    print(mac_id)
    print_up_table = "db_sde.devices_income"
    print_up_stat = "print_stat = '1'"
    print_up_value = "device_id = '"+mac_id+"'"
    print_update = db_connect()
    print_update.connect_update(print_up_table,print_up_stat,print_up_value)
