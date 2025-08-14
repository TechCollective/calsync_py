import sqlite3
import json
from datetime import datetime, date, time
from helpers import extract_date
from log import *


class ServiceCall:
    def __init__(self, call_id, startDateTime, endDateTime, lastModifiedDateTime, description, company, location, resources, ticketInfo, deleted, needs_sync):
        self.call_id = call_id
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
        self.lastModifiedDateTime = lastModifiedDateTime
        self.description = description
        self.company = company
        self.location = location
        self.resources = resources
        self.ticketInfo = ticketInfo
        self.deleted = deleted
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
                            ticketInfo = ?,
                            deleted = ?,
                            needs_sync = ?
                            WHERE id = ?''',
                           (self.startDateTime, self.endDateTime, self.lastModifiedDateTime, self.description, self.company, self.location, self.resources, self.ticketInfo, self.deleted, self.needs_sync, self.call_id))
        else:
            # Row does not exist, create a new row
            cursor.execute('''INSERT INTO service_calls 
                            (id, startDateTime, endDateTime, lastModifiedDateTime, description, company, location, resources, ticketInfo, deleted, needs_sync)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (self.call_id, self.startDateTime, self.endDateTime, self.lastModifiedDateTime, self.description, self.company, self.location, self.resources, self.ticketInfo, self.deleted, self.needs_sync))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    @staticmethod
    def get_rows_needing_sync():
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        query = "SELECT * FROM service_calls WHERE needs_sync = 1 AND deleted = 0"
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        result = []

        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
            result.append(row_dict)

        conn.close()

        return result

    @staticmethod
    def get_rows_needing_deletion():
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        query = "SELECT * FROM service_calls WHERE needs_sync = 1 AND deleted = 1"
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        result = []

        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
            result.append(row_dict)

        conn.close()

        return result


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

        # Flexible date parsing for arguments
        start_date = extract_date(start_date)
        end_date = extract_date(end_date)

        for id in ids:
            query = "SELECT id, startDateTime FROM service_calls WHERE id = ?"
            cursor.execute(query, (id,))
            rows = cursor.fetchall()

            for row_id, startDateTime in rows:
                parsed_date = extract_date(startDateTime)
                if start_date <= parsed_date <= end_date:
                    update_query = "UPDATE service_calls SET deleted = 1, needs_sync = 1 WHERE id = ?"
                    cursor.execute(update_query, (row_id,))
                    log_event(f"{id} marked as deleted in DB")

        conn.commit()
        conn.close()

    @staticmethod
    def delete(id):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM service_calls WHERE id=?", (id,))
        conn.commit()
        conn.close()

    @staticmethod
    def mark_as_synced(id):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        update_query = "UPDATE service_calls SET needs_sync = 0 WHERE id = ?"
        cursor.execute(update_query, (id,))

        conn.commit()
        conn.close()

    @staticmethod
    def delete_old_events(specified_date):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Convert the specified_date to a string in "%Y-%m-%d" format
        specified_date_str = specified_date.strftime("%Y-%m-%d")

        # Delete events with end_date older than the specified date
        delete_query = "DELETE FROM service_calls WHERE endDateTime < ?"
        cursor.execute(delete_query, (specified_date_str,))

        conn.commit()
        conn.close()
