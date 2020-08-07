import glob
import os
import sqlite3


def multi_to_one(fp, db):
    dir_list = glob.glob(fp + "*.db")

    conn = sqlite3.connect("./" + db)
    c = conn.cursor()

    c.execute("""
            CREATE TABLE IF NOT EXISTS central_acts (
            act_name TEXT,
            is_downloaded INT,
            is_bookmarked INT,
            act_data BLOB
            )
            """)
    conn.commit()
    to_write = []
    sorted_dir_list = sorted(dir_list)

    for dir in sorted_dir_list:
        name = os.path.basename(dir).replace('.db', '')
        blob = convert_to_binary_data(dir)
        to_write.append((
            name,
            1,
            0,
            blob

        ))

    c.executemany("INSERT INTO central_acts VALUES (?,?,?,?)", to_write)
    conn.commit()
    conn.close()


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


if __name__ == '__main__':
    file_path = "./Database/"
    db_name = "Laws of India"
    multi_to_one(file_path, db_name)
