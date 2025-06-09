import sqlite3
from datetime import datetime

conn = sqlite3.connect("detections.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    confidence REAL,
    camera_ip TEXT,
    timestamp TEXT
)
''')
conn.commit()

def insert_detection(label, confidence, camera_ip):
    cursor.execute('''
        INSERT INTO detections (label, confidence, camera_ip, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (label, confidence, camera_ip, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()

def get_all_detections(cutoff_time):
    return cursor.execute(
        "SELECT * FROM detections WHERE timestamp > ?", (cutoff_time,)
    ).fetchall()

def get_detections_by_label(label, cutoff_time):
    return cursor.execute(
        "SELECT * FROM detections WHERE label = ? AND timestamp > ?", (label, cutoff_time)
    ).fetchall()

def clear_detections(camera_ip):
    cursor.execute("DELETE FROM detections WHERE camera_ip = ?", (camera_ip,))
    conn.commit()
