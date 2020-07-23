import glob
import json as js
import os
import datetime
import sqlite3


def check_for_errors(json_directory):
    if os.path.isdir(json_directory):

        dir_list = glob.glob(json_directory + "*.json")

        for path in dir_list:
            act = os.path.basename(path)
            try:
                with open(path) as jsn:
                    json_data = js.load(jsn)
                print(act + '-- OK')
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

            # Insert contents to db
            insert_contents_to_db(db_path, json_data)

            # Insert sections to db
            insert_sections_to_db(db_path, json_data)

            # Insert schedule
            insert_schedules_to_db(db_path, json_data, act_name, sch_dir)

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
                    last_modified TEXT
                )
                """)

    # create contents table
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS contents (
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
                CREATE TABLE IF NOT EXISTS schedules(
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
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        dt
    )

    c.execute("""INSERT INTO act_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", act_details_to_write)
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
            jsn_data['contents'][str(i)]['min_index'] + 1,
            jsn_data['contents'][str(i)]['max_index'] + 1
        ))

        i += 1

    c.executemany("INSERT INTO contents VALUES (?,?,?,?,?)", contents_to_write)

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
            content_string = content_string + content

        if len(jsn_data['sections'][str(i)]['footnotes']) > 0:
            footnotes_string = ""
            for footnote in jsn_data['sections'][str(i)]['footnotes']:
                footnotes_string = footnotes_string + footnote
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


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


if __name__ == '__main__':
    print("Select option:")
    print("1. Check for errors Json file.")
    print("2. Convert Json to Sqlite.")

    option = int(input("Enter Option(1 or 2):"))
    if option == 1:
        path_to_json_files = str(input("Enter location of json file/s: "))
        path_to_schedules = str(input("Enter location of schedules: "))
        check_for_errors(path_to_json_files)
    else:
        path_to_json_files = str(input("Enter location of json file/s: "))
        path_to_schedules = str(input("Enter location of schedules: "))
        convert_to_sqlite(path_to_json_files, path_to_schedules)
