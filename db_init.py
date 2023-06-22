import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Create the service_calls table
cursor.execute('''CREATE TABLE IF NOT EXISTS service_calls (
                    id INTEGER PRIMARY KEY,
                    lastModifiedDateTime TEXT,
                    start_date_time TEXT,
                    end_date_time TEXT,
                    description TEXT,
                    company TEXT,
                    resources TEXT,
                    location TEXT,
                    deleted INTEGER,
                    needs_sync INTEGER
                )''')

# Commit the changes and close the connection
conn.commit()
conn.close()
