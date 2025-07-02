import re
import sqlite3
import sys

import numpy as np


def main(file, replacement):
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    cur.execute("select path, id from file")

    results = list(cur)
    patched = [
        (re.sub(r"/.*/RAiDER/", replacement, r[0]), r[1])
        for r in cur
    ]

    print(
        "Has any file path been changed?",
        np.any(np.array(results) != np.array(patched))
    )

    cur.executemany("update file set path=? where id=?", patched)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
