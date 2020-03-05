#!/usr/bin/python3

import sqlite3, sys, json, glob

def eval_exercise(c, gold_data, ex_id = None):
    if ex_id:
        ex = c.execute("SELECT * FROM exercises WHERE id=?", (ex_id,)).fetchall()
    else:
        ex = c.execute("SELECT * FROM exercises")
    all_results = []
    file_results = {}
    for e in ex:
        results = json.loads(e["results"])
        if "current" in results:
            print("WARNING: exercise is incomplete", file=sys.stderr)
            del results["current"]
        ex_sets = results.keys()
        correct = 0
        skipped = 0
        total = len(ex_sets)
        for s in ex_sets:
            if s not in file_results:
                file_results[s] = {"correct": 0, "total": 0, "skipped": 0, "words": {}}
            file_results[s]["total"] += 1
            outlier = results[s]["outlier"]
            status = "wrong"
            if outlier in gold_data[s]["outliers"]:
                correct += 1
                file_results[s]["correct"] += 1
                status = "correct"
            else:
                outlier = set(results[s]["words"]) & set(gold_data[s]["outliers"])
                if len(outlier) > 1:
                    raise RuntimeError("More than one outlier in the set!")
                outlier = outlier.pop()
            if results[s]["outlier"] == "=SKIP=":
                skipped += 1
                file_results[s]["skipped"] += 1
                status = "skipped"
            if outlier not in file_results[s]["words"]:
                file_results[s]["words"][outlier] = {"correct": status == "correct" and 1 or 0, "total": 1, "skipped": status == "skipped" and 1 or 0}
            else:
                file_results[s]["words"][outlier]["correct"] += (status == "correct") and 1 or 0
                file_results[s]["words"][outlier]["total"] += 1
                file_results[s]["words"][outlier]["skipped"] += (status == "skipped") and 1 or 0
        all_results.append({"id": e["id"], "name": e["name"], "lang": e["lang"], "correct": correct, "total": total, "skipped": skipped})
    return all_results, file_results

def load_exercise_data(datadir):
    ex_sets = glob.iglob(datadir + "/*/??-*")
    exercises = {}
    for ex in ex_sets:
        exercises[ex] = load_exercise_file(ex)
    return exercises

def load_exercise_file(filename):
    ex_file = open(filename).readlines()
    ex_data = [l.strip() for l in ex_file if not l.startswith("#")]
    if len(ex_data) != 17 or ex_data[8] != "":
        raise Exception("Invalid exercise format for file %s" % ex_filename)
    return {"words": ex_data[:8], "outliers": ex_data[9:]}

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: %s SQLITE.db DATADIR [EXERCISE_ID]", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(sys.argv[1])
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if len(sys.argv) == 4:
        r, fr = eval_exercise (c, load_exercise_data(sys.argv[2]), sys.argv[3])[0]
        print("exercise id: %s, name: %s, lang: %s" % (r["id"], r["name"], r["lang"]))
        print("correct = %d, total = %d, precision = %.2f, skipped = %d" % (r["correct"], r["total"], r["correct"]/r["total"], r["skipped"]))
    else:
        rr, fr = eval_exercise (c, load_exercise_data(sys.argv[2]))
        per_lang = {}
        for r in rr:
            print("exercise id: %s, name: %s, lang: %s" % (r["id"], r["name"], r["lang"]))
            print("correct = %d, total = %d, precision = %.2f, skipped = %d" % (r["correct"], r["total"], r["correct"]/r["total"], r["skipped"]))
            if r["lang"] not in per_lang:
                per_lang[r["lang"]] = {"correct": 0, "total": 0, "skipped": 0}
            per_lang[r["lang"]]["correct"] += r["correct"]
            per_lang[r["lang"]]["total"] += r["total"]
            per_lang[r["lang"]]["skipped"] += r["skipped"]
        print("PER LANGUAGE:")
        sum_total = 0
        sum_correct = 0
        sum_skipped = 0
        for l, v in per_lang.items():
            print("Language %s: correct = %d, total = %d, precision = %.2f, skipped= %d" % (l, v["correct"], v["total"], v["correct"]/v["total"], v["skipped"]))
            sum_total += v["total"]
            sum_correct += v["correct"]
            sum_skipped += v["skipped"]
        print("TOTAL: correct = %d, total = %d, precision = %.2f, skipped = %d" % (sum_correct, sum_total, sum_correct/sum_total, sum_skipped))
        for f, k in fr.items():
            print("Filename %s: correct = %d, total = %d, precision = %.2f, skipped= %d" % (f, k["correct"], k["total"], k["correct"]/k["total"], k["skipped"]))
            for w, kk in k["words"].items():
                print("Outlier %s: correct = %d, total = %d, precision = %.2f, skipped= %d" % (w, kk["correct"], kk["total"], kk["correct"]/kk["total"], kk["skipped"]))
