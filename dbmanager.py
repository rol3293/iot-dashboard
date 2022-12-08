import sqlite3
con = sqlite3.connect("iot.db")

cur = con.cursor()

def getUserThresholds(id):
    res = cur.execute("SELECT * FROM Users WHERE user_id = ?", [id])
    return res.fetchone()