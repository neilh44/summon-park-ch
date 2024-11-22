import sqlite3
import datetime

# Database file path
db_path = "/Users/nileshhanotia/Projects/Parking_Valet/sqlite.db"  # Replace with the actual database path

# Name of the table and the column you're interested in
table_name = "tickets"  # Replace with your table name

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to get tickets from the last 2 days
    cursor.execute(f"""
        SELECT * 
        FROM {table_name} 
        WHERE createdat >= datetime('now', '-2 days');
    """)
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print(f"No tickets found in the last 2 days from the '{table_name}' table.")

except sqlite3.Error as e:
    print(f"Database error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection
    if conn:
        conn.close()
