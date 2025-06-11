import psycopg2
from datetime import datetime

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="fire_detection_db",     # replace with your DB name
    user="postgres",                # replace with your DB user
    password="yourpassword",        # replace with your DB password
    host="localhost",               # replace with your DB host if needed
    port="5432"                      # default PostgreSQL port
)
cursor = conn.cursor()

def insert_detection(label, confidence, camera_ip):
    cursor.execute('''
        INSERT INTO detected_objects (label, confidence, camera_ip, timestamp)
        VALUES (%s, %s, %s, %s)
    ''', (label, confidence, camera_ip, datetime.now()))
    conn.commit()

def get_all_detections(cutoff_time):
    cursor.execute('''
        SELECT id, label, confidence, camera_ip, timestamp
        FROM detected_objects
        WHERE timestamp > %s
        ORDER BY timestamp DESC
    ''', (cutoff_time,))
    return cursor.fetchall()

def get_detections_by_label(label, cutoff_time):
    cursor.execute('''
        SELECT id, label, confidence, camera_ip, timestamp
        FROM detected_objects
        WHERE label = %s AND timestamp > %s
        ORDER BY timestamp DESC
    ''', (label, cutoff_time))
    return cursor.fetchall()

def clear_detections(camera_ip):
    cursor.execute('''
        DELETE FROM alerts
        WHERE object_id IN (
            SELECT id FROM detected_objects WHERE camera_ip = %s
        )
    ''', (camera_ip,))

    cursor.execute('''
        DELETE FROM detected_objects WHERE camera_ip = %s
    ''', (camera_ip,))
    conn.commit()
