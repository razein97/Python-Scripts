import glob
import json as js
import os
import sqlite3
import gzip

import time


def check_for_errors(json_directory):
    if os.path.isdir(json_directory):

        dir_list = glob.glob(json_directory + "*.json")

        for path in dir_list:
            act = os.path.basename(path)
            try:
                with open(path) as jsn:
                    json_data = js.load(jsn)

                # print(act + '-- OK')
            except:
                print(act + ' -- ERROR')

    elif os.path.isfile(json_directory):
        act = os.path.basename(json_directory)
        try:
            with open(json_directory) as jsn:
                json_data = js.load(jsn)
            print(act + '-- OK')
        except:
            print(act + ' -- ERROR')


def convert_to_sqlite(jsn_dir, sch_dir):
    if os.path.isdir(jsn_dir):
        dir_list = glob.glob(jsn_dir + "*.json")
        os.makedirs('./' + "Database", exist_ok=True)

        for path in dir_list:
            act = os.path.basename(path)
            act_name = act.replace('.json', '')
            try:
                with open(path) as jsn:
                    json_data = js.load(jsn)

                db_path = ("./Database/" + act_name + '.db')
                create_tables_in_db(db_path)
                insert_act_details_to_db(db_path, json_data)
                insert_tabs_to_db(db_path, json_data)
                insert_contents_to_db(db_path, json_data)
                insert_sections_to_db(db_path, json_data)
                insert_schedules_to_db(db_path, json_data, act_name, sch_dir)
                # print(act_name + '\tDone.')

            except:
                print(act + ' -- ERROR')


    elif os.path.isfile(jsn_dir):
        os.makedirs('./' + "Database", exist_ok=True)
        act = os.path.basename(jsn_dir)
        act_name = act.replace('.json', '')
        try:
            with open(jsn_dir) as jsn:
                json_data = js.load(jsn)
            db_path = ("./Database/" + act_name + '.db')

            # Create the tables in database
            create_tables_in_db(db_path)

            # Insert act details to db
            insert_act_details_to_db(db_path, json_data)
            print('ok1')

            # Insert tabs to db
            insert_tabs_to_db(db_path, json_data)

            # Insert contents to db
            insert_contents_to_db(db_path, json_data)
            print('ok2')

            # Insert sections to db
            insert_sections_to_db(db_path, json_data)
            print('ok3')

            # Insert schedule
            insert_schedules_to_db(db_path, json_data, act_name, sch_dir)
            print('ok4')




        except:
            print('Error')


def create_tables_in_db(d_path):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()

    # create act_details table
    c.execute("""CREATE TABLE IF NOT EXISTS act_details (
                    act_name TEXT,
                    act_no TEXT,
                    act_year TEXT,
                    summary TEXT,
                    sections TEXT,
                    chapters TEXT,
                    enactment_date TEXT,
                    commencement_date TEXT,
                    enacted_by TEXT,
                    ministry TEXT,
                    department TEXT,    
                    last_modified INT
                )
                """)

    # create tabs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS tabs (
    tab TEXT
    )
    
    """)

    # create contents table
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS chapters (
    title TEXT,
    subtitle TEXT,
    sections TEXT,
    min_index INT,
    max_index INT
    )
        """
    )

    # create sections table
    c.execute("""
                CREATE TABLE IF NOT EXISTS sections (
                title TEXT,
                subtitle TEXT,
                content TEXT,
                footnotes TEXT
                )
                """)

    # Create schedules table
    c.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                schedule_heading TEXT,
                schedule_content BLOB
                )
                """)

    # commit the command
    conn.commit()
    conn.close()


def insert_act_details_to_db(d_path, jsn_data):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()
    # insert to act_details

    act_details_to_write = (
        jsn_data['act_details']['act_name'],
        jsn_data['act_details']['act_no'],
        jsn_data['act_details']['act_year'],
        jsn_data['act_details']['summary'],
        jsn_data['act_details']['sections'],
        jsn_data['act_details']['chapters'],
        jsn_data['act_details']['enactment_date'],
        jsn_data['act_details']['commencement_date'],
        jsn_data['act_details']['enacted_by'],
        jsn_data['act_details']['ministry'],
        jsn_data['act_details']['department'],
        int(time.time())
    )

    c.execute("""INSERT INTO act_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", act_details_to_write)
    conn.commit()
    conn.close()


def insert_tabs_to_db(d_path, jsn_data):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()

    for tab in jsn_data['tabs']:
        c.execute("INSERT INTO tabs VALUES (?)", (tab,))

    conn.commit()
    conn.close()


def insert_contents_to_db(d_path, jsn_data):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()
    contents_to_write = []
    i = 0
    while i < len(jsn_data['contents']):
        contents_to_write.append((
            jsn_data['contents'][str(i)]['title'],
            jsn_data['contents'][str(i)]['subtitle'],
            jsn_data['contents'][str(i)]['sections'],
            jsn_data['contents'][str(i)]['min_index'],
            jsn_data['contents'][str(i)]['max_index']
        ))

        i += 1

    c.executemany("INSERT INTO chapters VALUES (?,?,?,?,?)", contents_to_write)

    conn.commit()
    conn.close()


def insert_sections_to_db(d_path, jsn_data):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()
    sections_to_write = []
    i = 0
    while i < len(jsn_data['sections']):
        content_string = ""
        for content in jsn_data['sections'][str(i)]['content']:
            content_string = content_string + content + '\n'

        if len(jsn_data['sections'][str(i)]['footnotes']) > 0:
            footnotes_string = ""
            for footnote in jsn_data['sections'][str(i)]['footnotes']:
                footnotes_string = footnotes_string + footnote + '\n'
        else:
            footnotes_string = ""

        sections_to_write.append((
            jsn_data['sections'][str(i)]['title'],
            jsn_data['sections'][str(i)]['subtitle'],
            content_string,
            footnotes_string

        ))

        i += 1

    c.executemany("INSERT INTO sections VALUES (?,?,?,?)", sections_to_write)

    conn.commit()
    conn.close()


def insert_schedules_to_db(d_path, jsn_data, act_name, sch):
    conn = sqlite3.connect(d_path)
    c = conn.cursor()
    schedules_to_write = []
    if len(jsn_data['schedules']) > 0:
        for schedule in jsn_data['schedules']:
            file_path = (sch + schedule + '-' + act_name + '.pdf')

            pdf_blob = convert_to_binary_data(file_path)

            schedules_to_write.append((schedule, pdf_blob))

        c.executemany("INSERT INTO schedules VALUES (?,?)", schedules_to_write)

        conn.commit()
        conn.close()

    else:
        pass


def compress_files(directory):
    dir_list = glob.glob(directory + '*.db')
    os.makedirs('./' + "Compressed DB", exist_ok=True)

    for f in dir_list:
        print(f)
        base_name = os.path.basename(f)
        binary_data = convert_to_binary_data(f)
        with gzip.open('./Compressed DB/' + base_name + '.gz', 'wb') as out:
            out.write(binary_data)


def compress_file(file_path):
    base_name = os.path.basename(file_path)
    binary_data = convert_to_binary_data(file_path)
    with gzip.open('./' + base_name + '.gz', 'wb') as out:
        out.write(binary_data)


def gen_acts_list(dir_path):
    dir_list = glob.glob(dir_path + '*.json')
    dir_list.sort()
    cen_acts_tmp = {}
    i = 0
    while i < len(dir_list):
        print(dir_list[i])

        basename = os.path.basename(dir_list[i]).replace('.json', '')
        cen_acts_tmp[str(i)] = {
            "title": basename
        }
        i = i + 1
    cen_acts = {
        "central_acts": cen_acts_tmp
    }
    with open('acts_list.json', 'w') as out:
        js.dump(cen_acts, out)

    compress_file('./acts_list.json')


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


if __name__ == '__main__':
    print("Select option:")
    print("1. Check for errors Json file.")
    print("2. Convert Json to Sqlite.")
    print("3. Compress all db files in a directory.")
    print("4. Compress single file.")
    print("5. Generate acts list.")

    option = int(input("Enter Option(1 or 2 or 3 or 4 or 5):"))
    if option == 1:
        path_to_json_files = str(input("Enter location of json file/s: "))
        path_to_schedules = str(input("Enter location of schedules: "))
        check_for_errors(path_to_json_files)
    elif option == 2:
        path_to_json_files = str(input("Enter location of json file/s: "))
        path_to_schedules = str(input("Enter location of schedules: "))
        convert_to_sqlite(path_to_json_files, path_to_schedules)
    elif option == 3:
        compress_dir = str(input('Enter directory to compress: '))
        compress_files(compress_dir)

    elif option == 4:
        compress_path = str(input('Enter file to compress: '))
        compress_file(compress_path)

    else:
        path_for_gen = str(input('Enter directory of json files: '))
        gen_acts_list(path_for_gen)
