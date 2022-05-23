#!/usr/bin/python3

import sqlite3, sys, json, glob, argparse
from collections import defaultdict
from datetime import datetime

def eval_exercise(c, gold_data, langs, skip_incomplete, date_from, date_to, ex_id = None):
    if ex_id:
        ex = c.execute("SELECT * FROM exercises WHERE id=?", (ex_id,)).fetchall()
    else:
        ex = c.execute("SELECT * FROM exercises")
    all_results = []
    file_results = {}
    for e in ex:
        if "ALL" not in langs and e["lang"] not in langs:
            continue
        results = json.loads(e["results"])
        if "current" in results:
            del results["current"]
            if skip_incomplete:
                print("WARNING: exercise %s is incomplete, skipping; use -a to include this" % e["id"], file=sys.stderr)
                continue
        results.pop("previous", None)
        ex_sets = results.keys()
        correct = 0
        skipped = 0
        total = len(ex_sets)
        mistakes = []
        for s in ex_sets:
            if "when" in results[s]:
                when = datetime.fromisoformat(results[s]["when"])
            else:
                when = None
            if when and ((date_from and when < date_from) or (date_to and when > date_to)):
                continue
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
                elif not outlier:
                    continue
                outlier = outlier.pop()
            if results[s]["outlier"] == "=SKIP=":
                skipped += 1
                file_results[s]["skipped"] += 1
                status = "skipped"
            if outlier not in file_results[s]["words"]:
                file_results[s]["words"][outlier] = {"correct": 0, "total": 0, "skipped": 0, "mistakes": defaultdict(int), "ids": []}
            file_results[s]["words"][outlier]["correct"] += int(status == "correct")
            file_results[s]["words"][outlier]["total"] += 1
            if status == "wrong":
                file_results[s]["words"][outlier]["mistakes"][results[s]["outlier"]] += 1
                mistakes.append((s, results[s]["outlier"], outlier))
            file_results[s]["words"][outlier]["skipped"] += int(status == "skipped")
            file_results[s]["words"][outlier]["ids"].append(e["id"])
        all_results.append({"id": e["id"], "name": e["name"], "lang": e["lang"], "mistakes": mistakes, "correct": correct, "total": total, "skipped": skipped})
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
    parser = argparse.ArgumentParser(description='Evalutes outlier detection annotations.')
    parser.add_argument('dbpath', metavar='SQLITE.db', help='path to the SQLITE database with annotations')
    parser.add_argument('datadir', metavar='DATADIR', help='path to the data directory with gold dataset')
    parser.add_argument('lang', metavar='LANG', help='ALL|CS,EN,IT...')
    parser.add_argument('-a', '--all', help='include also incomplete exercises', action='store_false', dest='skip_incomplete')
    parser.add_argument('-f', '--from', help='limit evaluation to actions from this datetime in ISO format (e.g. 1970-01-01 23:02:13)', dest='date_from', type=datetime.fromisoformat)
    parser.add_argument('-t', '--to', help='limit evaluation to actions to this datetime in ISO format', dest='date_to', type=datetime.fromisoformat)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', default=0, help='verbosity, up to -vvv supported')
    group.add_argument('-e', '--ex-id', help='limit evaluation to particular exercise ID')
#    if len(sys.argv) < 4 or len(sys.argv) > 5:
#        print("Usage: %s [-a] SQLITE.db DATADIR LANG=ALL|CS,EN,.. [ VERBOSITY_LEVEL={default=0,1,2,3} | EXERCISE_ID ]", file=sys.stderr)
#        print("-a includes also incomplete exercises")
#        sys.exit(1)
    args = parser.parse_args()

    conn = sqlite3.connect(args.dbpath)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    langs = args.lang.split(",")

    if args.ex_id:
        r = eval_exercise (c, load_exercise_data(args.datadir), ["ALL"], args.skip_incomplete, args.date_from, args.date_to, args.ex_id)[0][0]
        print("exercise id: %s, name: %s, lang: %s" % (r["id"], r["name"], r["lang"]))
        if r["total"] > 0:
            print("correct = %d, total = %d, precision = %.2f, skipped = %d" % (r["correct"], r["total"], r["correct"]/r["total"], r["skipped"]))
        else:
            print("total = 0")
        print("mistakes:")
        for m in r["mistakes"]:
            exset, mistaken_outlier, correct_outlier = m
            print("%s instead of %s for %s" % (exset, mistaken_outlier, correct_outlier))
    else:
        def vp(msg, level):
            if level <= args.verbose:
                print(msg)
        rr, fr = eval_exercise (c, load_exercise_data(args.datadir), langs, args.skip_incomplete, args.date_from, args.date_to)
        per_lang = {}
        for r in rr:
            vp("exercise id: %s, name: %s, lang: %s" % (r["id"], r["name"], r["lang"]), 2)
            if not r["total"]:
                vp("skipping (total=0)", 2)
                continue
            vp("correct = %d, total = %d, precision = %.2f, skipped = %d" % (r["correct"], r["total"], r["correct"]/r["total"], r["skipped"]), 2)
            if r["lang"] not in per_lang:
                per_lang[r["lang"]] = {"correct": 0, "total": 0, "skipped": 0}
            per_lang[r["lang"]]["correct"] += r["correct"]
            per_lang[r["lang"]]["total"] += r["total"]
            per_lang[r["lang"]]["skipped"] += r["skipped"]
        vp("PER LANGUAGE:", 0)
        sum_total = 0
        sum_correct = 0
        sum_skipped = 0
        for l, v in per_lang.items():
            vp("Language %s: correct = %d, total = %d, precision = %.2f, skipped = %d" % (l, v["correct"], v["total"], v["correct"]/v["total"], v["skipped"]), 0)
            sum_total += v["total"]
            sum_correct += v["correct"]
            sum_skipped += v["skipped"]
        vp("TOTAL: correct = %d, total = %d, precision = %.2f, skipped = %d" % (sum_correct, sum_total, sum_correct/sum_total, sum_skipped), 0)
        vp("\nPER FILE:", 1)
        for f, k in fr.items():
            vp("\nFilename %s: correct = %d, total = %d, precision = %.2f, skipped = %d" % (f, k["correct"], k["total"], k["correct"]/k["total"], k["skipped"]), 1)
            for w, kk in k["words"].items():
                vp("Outlier %s: correct = %d, total = %d, precision = %.2f, skipped = %d, mistakes = %s, ids = %s" % (w, kk["correct"], kk["total"], kk["correct"]/kk["total"], kk["skipped"], dict(kk["mistakes"]), args.verbose > 2 and kk["ids"] or "[VERBOSITY3]"), 1)
