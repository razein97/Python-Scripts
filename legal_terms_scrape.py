import json
import glob
import os
from bs4 import BeautifulSoup


def launch_instance(fp, filename):
    dir_list = glob.glob(fp + '*.html')

    print(dir_list)
    for file in dir_list:
        soup = BeautifulSoup(open(file), features='html.parser')

        term = []

        # add all text to list
        fonts = soup.find_all('font')
        for font in fonts:
            t = font.get_text()
            term.append(t)

        even_list = []
        odd_list = []
        inc = 0
        length = len(term)
        while inc < length:
            if inc % 2 == 0:
                even_list.append(term[inc])
            else:
                odd_list.append(term[inc])

            inc = inc + 1

        to_edit = []
        dic = {}

        len_list = len(even_list)

        i = 0
        while i < len_list:
            dic[str(i)] = {
                "term": even_list[i],
                "definition": odd_list[i]
            }

            i = i + 1

        base_name = os.path.basename(file)
        base_name = base_name.replace('.html', '')
        print(base_name)
        with open(base_name + '.json', 'w') as js:
            json.dump(dic, js)


if __name__ == '__main__':
    # url = str(input('URL: '))

    # file_name = str(input('Filename: '))
    # url = sys.argv[1]
    # file_name = sys.argv[2]
    directory = './html/'
    file_name = 'd'

    launch_instance(directory, file_name)
