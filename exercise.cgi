#!/usr/bin/python3

import cgi, cgitb, random, sqlite3, json, glob
from exercise import load_exercise_file, load_exercise_data, eval_exercise
cgitb.enable()
conn = sqlite3.connect('exercise.db')
conn.row_factory = sqlite3.Row
form = cgi.FieldStorage()

print("Content-Type: text/json\n")
datapath = "data"

def get_exercise_sets(lang):
    return set(glob.glob(datapath + "/*/" + lang + "-*"))

def get_next_exercise(exercise_sets):
    ex_set = random.choice(exercise_sets)
    ex = load_exercise_file (ex_set)
    outlier = random.choice(ex["outliers"])
    ex["words"].append(outlier)
    random.shuffle(ex["words"])
    return ex_set, ex["words"]

def action_next(c, ex_id):
    ex = c.execute("SELECT * FROM exercises WHERE id=?", (ex_id,)).fetchone()
    results = json.loads(ex["results"])
    response = {"completed": False}
    if "current" in results:
        response["words"] = results["current"]["words"]
        return response
    all_ex = get_exercise_sets(ex["lang"])
    todo = list(all_ex - set(results.keys()))
    if len(todo) == 0:
        response["completed"] = True
        return response
    filename, response["words"] = get_next_exercise(todo)
    results["current"] = {"file": filename, "words": response["words"]}
    c.execute("UPDATE exercises SET results=? WHERE id=?", (json.dumps(results), ex_id))
    return response

def save_result(c, ex_id, outlier):
    ex = c.execute("SELECT results FROM exercises WHERE id=?", (ex_id,)).fetchone()
    results = json.loads(ex["results"])
    if not "current" in results:
        return
    if outlier != "=SKIP=" and outlier not in results["current"]["words"]:
        return
    filename = results["current"]["file"]
    results[filename] = {"words": results["current"]["words"], "outlier": outlier}
    del results["current"]
    c.execute("UPDATE exercises SET results=? WHERE id=?", (json.dumps(results), ex_id))

action = form["action"].value

if action == "new":
    name = form["name"].value
    lang = form["lang"].value
    c = conn.cursor()
    while True:
        try:
            c.execute("INSERT INTO exercises VALUES(LOWER(HEX(RANDOMBLOB(16))), ?, ?, '{}')", (name, lang))
        except sqlite3.IntegrityError:
            continue
        break
    new = c.execute("SELECT * FROM exercises WHERE ROWID=?", (c.lastrowid,))
    conn.commit()
    print('{"id": "%s"}' % new.fetchone()["id"])
elif action == "next":
    c = conn.cursor()
    ex_id = form["id"].value.lower()
    if "chosen" in form:
        save_result(c, ex_id, form["chosen"].value)
    response = action_next(c, ex_id)
    conn.commit()
    print(json.dumps(response))
elif action == "eval":
    c = conn.cursor()
    ex_id = form["id"].value.lower()
    r = eval_exercise (c, load_exercise_data(datapath), ex_id)[0]
    print(json.dumps(r))

