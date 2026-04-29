import sqlite3
from src.domain.entities.sensor import SensorReading
from src.domain.ports.repository_port import SensorRepositoryPort
from typing import List
from datetime import datetime

class SQLiteSensorRepository(SensorRepositoryPort):
    def __init__(self, db_path: str = "garden.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    humedad_suelo REAL,
                    temperatura REAL,
                    luminosidad REAL,
                    humedad_ambiental REAL,
                    fecha TEXT
                )
            """)

    def save(self, reading: SensorReading) -> SensorReading:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO readings (humedad_suelo, temperatura, luminosidad, humedad_ambiental, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (reading.humedad_suelo, reading.temperatura, reading.luminosidad, reading.humedad_ambiental, reading.fecha.isoformat()))
            reading.id = cursor.lastrowid
            return reading

    def get_latest(self) -> SensorReading:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM readings ORDER BY fecha DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return SensorReading(id=row[0], humedad_suelo=row[1], temperatura=row[2], luminosidad=row[3], humedad_ambiental=row[4], fecha=datetime.fromisoformat(row[5]))
            return None

    def get_history(self, limit: int = 24) -> List[SensorReading]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM readings ORDER BY fecha DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [SensorReading(id=row[0], humedad_suelo=row[1], temperatura=row[2], luminosidad=row[3], humedad_ambiental=row[4], fecha=datetime.fromisoformat(row[5])) for row in rows]
