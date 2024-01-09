import sqlite3
import json

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

save_table_to_json("service_calls", 'service_calls.json' )