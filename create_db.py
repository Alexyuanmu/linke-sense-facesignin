import sqlite3

conn = sqlite3.connect("FaceSignin.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE record(\
	id INTEGER PRIMARY KEY AUTOINCREMENT,\
	name CHAR(20) NOT NULL,\
	time DATETIME NOT NULL)")
cursor.close()
conn.commit()
conn.close()

