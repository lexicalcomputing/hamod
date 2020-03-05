#!/usr/bin/python3

import sqlite3, os, stat
db = 'exercise.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('CREATE TABLE exercises (id BLOB PRIMARY KEY, name TEXT, lang TEXT, results TEXT)')
conn.commit()
conn.close()
st = os.stat(db)
os.chmod(db, st.st_mode | stat.S_IWGRP)
