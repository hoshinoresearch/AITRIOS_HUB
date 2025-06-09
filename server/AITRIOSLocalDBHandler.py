import sqlite3
from datetime import datetime

class AITRIOSLocalDBHandler:
    def __init__(self):
        
        self.connection = sqlite3.connect("aitrios_local_data.db")
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

# 推論結果Table
class InferenceResultTableHandler:
    def __init__(self):
        self.dbhandler = AITRIOSLocalDBHandler()
        self.dbhandler.cursor
        self.create_table()

    def create_table(self):
        self.dbhandler.cursor.execute("""
        CREATE TABLE IF NOT EXISTS t_inference_result  (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            class_id  TEXT,                            
            inference_datetime  TEXT,                            
            inference_percentage  REAL,                            
            x1 INTEGER,
            y1 INTEGER,
            x2 INTEGER,
            y2 INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """)
        self.dbhandler.connection.commit()


    def insert_data(self, data):
        self.dbhandler.cursor.execute("INSERT INTO t_inference_result  (device_id, class_id, inference_datetime , inference_percentage, x1, y1, x2, y2) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                            (data["device_id"], data["C"], data["T"], data["P"], data["X"], data["Y"], data["x"], data["y"]))
        self.dbhandler.connection.commit()

    def fetch_by_device_id(self, device_id: str):
        self.dbhandler.cursor.execute("SELECT * FROM t_inference_result WHERE device_id = ?", (device_id,))
        return self.dbhandler.cursor.fetchall()

    def fetch_latestdate_by_device_id(self, device_id: str):
        self.dbhandler.cursor.execute(
            "SELECT * FROM t_inference_result "
            "WHERE device_id = ? AND inference_datetime = ("
            "SELECT inference_datetime FROM t_inference_result "
            "WHERE device_id = ? ORDER BY inference_datetime DESC LIMIT 1)",
            (device_id, device_id)
        )
        return self.dbhandler.cursor.fetchall()
 
    def convert_to_json_multiple(self, data_tuples):
        inferences = []
        for data_tuple in data_tuples:
            data_dict = {
                "device_id": data_tuple[1],
                "C": data_tuple[2],
                "T": datetime.strptime(data_tuple[3][:-3] + data_tuple[3][-3:] + "000", "%Y%m%d%H%M%S%f"),
                "P": data_tuple[4],
                "X": data_tuple[5],
                "Y": data_tuple[6],
                "x": data_tuple[7],
                "y": data_tuple[8]
            }
            inferences.append(data_dict)

        result = {
            "count": len(inferences),
            "inferences": inferences
        }

        return result

    def close(self):
        self.dbhandler.close()