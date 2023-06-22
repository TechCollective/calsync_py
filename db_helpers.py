import sqlite3
import json
from datetime import datetime


def get_column_names():
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Get the column names
    cursor.execute("PRAGMA table_info(service_calls)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Close the connection
    conn.close()

    return column_names


# Example usage
# column_names = get_column_names()
# print("Column names:", column_names)


def add_column(column_name, data_type):
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Alter table to add a new column
    cursor.execute(
        f"ALTER TABLE service_calls ADD COLUMN {column_name} {data_type}")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Example usage
# add_column("testing", "TEXT")


def upsert_service_call(call_id, start_date_time, end_date_time, lastModifiedDateTime, description, company, resources, needs_sync):
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Check if the row exists based on the call_id
    cursor.execute("SELECT * FROM service_calls WHERE id = ?", (call_id,))
    existing_row = cursor.fetchone()

    if existing_row is not None:
        # Row exists, update the row with new data
        cursor.execute('''UPDATE service_calls SET 
                          start_date_time = ?,
                          end_date_time = ?,
                          lastModifiedDateTime = ?,
                          description = ?,
                          company = ?,
                          resources = ?,
                          needs_sync = ?
                          WHERE id = ?''',
                       (start_date_time, end_date_time, lastModifiedDateTime, description, company, resources, needs_sync, call_id))
    else:
        # Row does not exist, create a new row
        cursor.execute('''INSERT INTO service_calls 
                          (id, start_date_time, end_date_time, lastModifiedDateTime, description, company, resources, needs_sync)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (call_id, start_date_time, end_date_time, lastModifiedDateTime, description, company, resources, needs_sync))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Example usage
# upsert_service_call(1, '2023-06-17 10:00', '2023-06-17 11:00', 'Sample description', 'Company A', 'Resource 1', 0)


def save_table_to_json(table_name, file_path):
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve the table data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get the column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Prepare a list of dictionaries representing each row
    data = []
    for row in rows:
        row_dict = dict(zip(column_names, row))
        data.append(row_dict)

    # Write the data to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Close the connection
    conn.close()


# Example usage
# save_table_to_json("service_calls", "service_calls.json")


# __________ convert all rows of db into a list __________
def fetch_table_rows(table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Retrieve the table data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get the column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Prepare a list of dictionaries representing each row
    data = []
    for row in rows:
        row_dict = dict(zip(column_names, row))
        data.append(row_dict)

    # Close the connection
    conn.close()

    return data


# Example usage
# table_data = fetch_table_rows("service_calls")
# for row in table_data:
#     print(row)


def mark_rows_as_deleted(ids, start_date, end_date):
    # Connect to the database
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    # Iterate over the IDs and check the rows in the table
    for id in ids:
        query = "SELECT id, start_date_time FROM service_calls WHERE id = ?"
        cursor.execute(query, (id,))
        rows = cursor.fetchall()

        # Iterate over the rows and update the "deleted" column if the start date is within the range
        for row in rows:
            row_id, start_date_time = row
            parsed_start_date_time = datetime.strptime(
                start_date_time, "%Y-%m-%dT%H:%M:%SZ").date()

            if start_date <= parsed_start_date_time <= end_date:
                update_query = "UPDATE service_calls SET deleted = 1 WHERE id = ?"
                cursor.execute(update_query, (row_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Example usage
# ids = [1, 2, 3]
# start_date = datetime.strptime("2023-06-01", "%Y-%m-%d").date()
# end_date = datetime.strptime("2023-06-30", "%Y-%m-%d").date()

# mark_rows_as_deleted(ids, start_date, end_date)
