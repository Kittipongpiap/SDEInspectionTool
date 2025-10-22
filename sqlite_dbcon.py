import mysql.connector
from mysql.connector import Error

class db_connect:
    def __init__(self):
        try:
            # Adjust for your environment (Mac / Office / Test)
            self.conn_db = mysql.connector.connect(
                host="localhost",
                database="db_sde",
                user="admin",
                password="Banana-Pi00"
            )

            if self.conn_db.is_connected():
                print("✅ Database connected successfully")
            else:
                print("❌ Database connection failed")

        except Error as e:
            print("❌ Error while connecting to MySQL:", e)

    def __del__(self):
        """Auto-close connection when object is destroyed."""
        if hasattr(self, "conn_db") and self.conn_db.is_connected():
            self.conn_db.close()
            print("🔒 MySQL connection closed")

    def connect_select(self, table, condition=None, field="*"):
        print("debug: select connect")
        print("SELECT from", table)
        cursor = None
        # Ensure we have a live connection
        if not hasattr(self, "conn_db") or not self.conn_db.is_connected():
            print("❌ No active DB connection for SELECT query")
            self.result = None
            return []

        try:
            cursor = self.conn_db.cursor()
            # Normalize field parameter
            if isinstance(field, (list, tuple)):
                field = ','.join(field)
            if not isinstance(field, str):
                field = str(field)
            # remove accidental leading commas/spaces
            field = field.lstrip(', ').strip()
            if field == '':
                field = '*'

            query = f"SELECT {field} FROM {table}"
            if condition:
                query += f" WHERE {condition}"

            # Debug: show the query being executed
            # print(f"Executing query: {query}")

            cursor.execute(query)
            print(query)
            self.query_result = cursor.fetchall()
            self.result = len(self.query_result)
            return self.query_result

        except Error as e:
            # If table doesn't exist (Error 1146), try to auto-create known table and retry once
            try:
                if getattr(e, 'errno', None) == 1146:
                    print("⚠️ Table not found. Attempting to create missing table and retry SELECT.")
                    self._create_known_table_if_missing(table)
                    # retry once
                    cursor = self.conn_db.cursor()
                    cursor.execute(query)
                    self.query_result = cursor.fetchall()
                    self.result = len(self.query_result)
                    return self.query_result
            except Exception:
                pass

            print("❌ Error in SELECT query:", e)
            self.result = None
            return []

        finally:
            if cursor:
                cursor.close()

    def connect_update(self, table, values, condition=None):
        cursor = None
        if not hasattr(self, "conn_db") or not self.conn_db.is_connected():
            print("❌ No active DB connection for UPDATE query")
            return 0

        try:
            cursor = self.conn_db.cursor()
            query = f"UPDATE {table} SET {values}"
            if condition:
                query += f" WHERE {condition}"

            cursor.execute(query)
            self.conn_db.commit()
            print(f"✅ Updated {cursor.rowcount} row(s)")
            return cursor.rowcount

        except Error as e:
            # If table doesn't exist (1146), attempt to create known table then retry once
            try:
                if getattr(e, 'errno', None) == 1146:
                    print("⚠️ Table not found. Attempting to create missing table and retry UPDATE.")
                    self._create_known_table_if_missing(table)
                    # retry once
                    cursor = self.conn_db.cursor()
                    cursor.execute(query)
                    self.conn_db.commit()
                    print(f"✅ Updated {cursor.rowcount} row(s)")
                    return cursor.rowcount
            except Exception:
                pass

            print("❌ Error in UPDATE query:", e)
            return 0

        finally:
            if cursor:
                cursor.close()

    def connect_delete(self, table, condition):
        cursor = None
        if not hasattr(self, "conn_db") or not self.conn_db.is_connected():
            print("❌ No active DB connection for DELETE query")
            return 0

        try:
            cursor = self.conn_db.cursor()
            query = f"DELETE FROM {table} WHERE {condition}"
            cursor.execute(query)
            self.conn_db.commit()
            print(f"🗑️ Deleted {cursor.rowcount} row(s)")
            return cursor.rowcount

        except Error as e:
            print("❌ Error in DELETE query:", e)
            return 0

        finally:
            if cursor:
                cursor.close()

    def connect_insert(self, table, values):
        cursor = None
        if not hasattr(self, "conn_db") or not self.conn_db.is_connected():
            print("❌ No active DB connection for INSERT query")
            return 0

        try:
            cursor = self.conn_db.cursor()
            query = f"INSERT INTO {table} VALUES {values}"
            cursor.execute(query)
            self.conn_db.commit()
            print(f"✅ Inserted {cursor.rowcount} row(s)")
            return cursor.rowcount

        except Error as e:
            print(f"cant insert {table} {values}")
            print("❌ Error in INSERT query:", e)
            return 0

        finally:
            if cursor:
                cursor.close()

    def connect_select_join(self, command):
        cursor = None
        if not hasattr(self, "conn_db") or not self.conn_db.is_connected():
            print("❌ No active DB connection for JOIN SELECT query")
            return []

        try:
            cursor = self.conn_db.cursor()
            cursor.execute(command)
            self.query_result = cursor.fetchall()
            return self.query_result

        except Error as e:
            print("❌ Error in JOIN SELECT query:", e)
            return []

        finally:
            if cursor:
                cursor.close()
    def _create_known_table_if_missing(self, full_table_name):
        """Attempt to create known tables when a SELECT/UPDATE fails due to missing table.

        full_table_name is expected to be 'db_sde.devices_income_lot' or similar.
        """
        try:
            # Extract schema and table
            if '.' in full_table_name:
                schema, table = full_table_name.split('.', 1)
            else:
                schema = None
                table = full_table_name

            # Only handle the known table for now
            if table == 'devices_income_lot':
                create_sql = (
                    "CREATE TABLE IF NOT EXISTS `devices_income_lot` ("
                    "`lot_no` varchar(20) NOT NULL,"
                    "`qty_product` int NOT NULL DEFAULT 0,"
                    "`qty_inspected` int DEFAULT 0,"
                    "`good_product` int DEFAULT 0,"
                    "`ng_product` int DEFAULT 0,"
                    "`status` char(1) DEFAULT '0',"
                    "`create_at` datetime DEFAULT CURRENT_TIMESTAMP,"
                    "PRIMARY KEY (`lot_no`)"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
                )
                cursor = self.conn_db.cursor()
                # If a schema was provided, ensure the schema exists (best-effort)
                if schema:
                    try:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {schema}")
                    except Exception:
                        pass
                cursor.execute(create_sql)
                self.conn_db.commit()
                cursor.close()
                print("✅ Created table devices_income_lot (if it did not exist).")
            elif table == 'devices_income_range':
                cursor = self.conn_db.cursor()
                if schema:
                    try:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {schema}")
                    except Exception:
                        pass
                cursor.execute(create_sql)
                self.conn_db.commit()
                # If table is empty, insert default seed rows (from repository SQL dump)
                try:
                    cursor.execute("SELECT COUNT(*) FROM devices_income_range")
                    cnt = cursor.fetchone()[0]
                except Exception:
                    cnt = 0

                if cnt == 0:
                    try:
                        seed_sql = (
                            "INSERT INTO devices_income_range (state_id,value_type,max_pm_2_5,max_scd_co2,max_scd_temp,max_scd_hum,min_pm_2_5,min_scd_co2,min_scd_temp,min_scd_hum,create_time) VALUES "
                            "(0,'Current_Value','1500','15','1500','1500','20','4','20','20',CURRENT_TIMESTAMP),"
                            "(1,'Sensor_Value','20','2300','33','82','0','300','16','35',CURRENT_TIMESTAMP);"
                        )
                        cursor.execute(seed_sql)
                        self.conn_db.commit()
                        print("✅ Seeded devices_income_range with default rows.")
                    except Exception as e:
                        print("⚠️ Could not seed devices_income_range:", e)

                cursor.close()
                print("✅ Created table devices_income_range (if it did not exist).")
        except Exception as e:
            print("❌ Failed to auto-create table:", e)
    def close(self):
        """Manually close the MySQL connection."""
        if hasattr(self, "conn_db") and self.conn_db.is_connected():
            self.conn_db.close()
            print("🔒 Database connection closed manually")

