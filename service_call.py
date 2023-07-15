import sqlite3
import json
from datetime import datetime


class ServiceCall:
    def __init__(self, call_id, startDateTime, endDateTime, lastModifiedDateTime, description, company, location, resources, needs_sync):
        self.call_id = call_id
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
        self.lastModifiedDateTime = lastModifiedDateTime
        self.description = description
        self.company = company
        self.location = location
        self.resources = resources
        self.needs_sync = needs_sync

    def save(self):

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Check if the row exists based on the call_id
        cursor.execute(
            "SELECT * FROM service_calls WHERE id = ?", (self.call_id,))
        existing_row = cursor.fetchone()

        if existing_row is not None:
            # Row exists, update the row with new data
            cursor.execute('''UPDATE service_calls SET 
                            startDateTime = ?,
                            endDateTime = ?,
                            lastModifiedDateTime = ?,
                            description = ?,
                            company = ?,
                            location = ?,
                            resources = ?,
                            needs_sync = ?
                            WHERE id = ?''',
                           (self.startDateTime, self.endDateTime, self.lastModifiedDateTime, self.description, self.company, self.location, self.resources, self.needs_sync, self.call_id))
        else:
            # Row does not exist, create a new row
            cursor.execute('''INSERT INTO service_calls 
                            (id, startDateTime, endDateTime, lastModifiedDateTime, description, company, location, resources, needs_sync)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (self.call_id, self.startDateTime, self.endDateTime, self.lastModifiedDateTime, self.description, self.company, self.location, self.resources, self.needs_sync))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

# __________ convert all rows of db into a list __________
    @staticmethod
    def fetch_all():

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        table_name = "service_calls"

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

        conn.close()

        return data

    @staticmethod
    def mark_as_deleted(ids, start_date, end_date):

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        # Iterate over the IDs and check the rows in the table
        for id in ids:
            query = "SELECT id, startDateTime FROM service_calls WHERE id = ?"
            cursor.execute(query, (id,))
            rows = cursor.fetchall()

            # Iterate over the rows and update the "deleted" column if the start date is within the range
            for row in rows:
                row_id, startDateTime = row
                parsed_startDateTime = datetime.strptime(
                    startDateTime, "%Y-%m-%dT%H:%M:%SZ").date()

                if start_date <= parsed_startDateTime <= end_date:
                    update_query = "UPDATE service_calls SET deleted = 1 WHERE id = ?"
                    cursor.execute(update_query, (row_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def delete(id):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id=?", (id))
        conn.commit()
        conn.close()
