import glob
import json
import _sqlite3


def start(dir_path):
    dir_files = glob.glob(dir_path + '*json')
    list_collection = []
    list_collection_m = {}
    dir_files.sort()
    for file in dir_files:
        with open(file) as f:

            data = json.load(f)
            len_data = len(data)
            i = 0
            while i < len_data:
                list_collection.append(data[str(i)])
                i = i + 1
    j = 0
    for l in list_collection:
        list_collection_m[str(j)] = l
        j = j + 1

    with open('merged' + '.json', 'w') as js:
        json.dump(list_collection_m, js)

    conn = _sqlite3.connect('merged.db')
    c = conn.cursor()
    c.execute("""
    
    CREATE TABLE IF NOT EXISTS terms(
    term TEXT,
    definition TEXT
    )
    """)
    k = 0
    for m in list_collection:
        to_write = (m['term'], m['definition'])

        c.execute("""
        INSERT INTO terms VALUES (?,?)
        """, to_write)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    fp = '/run/media/razein/internal_hdd/Projects/Git_Projects/Laws/Acts in India/Legal Terms/'
    start(fp)
