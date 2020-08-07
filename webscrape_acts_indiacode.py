import json
import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


def to_sup(s):
    sups = {u'1': u'\xb9',
            u'0': u'\u2070',
            u'3': u'\xb3',
            u'2': u'\xb2',
            u'5': u'\u2075',
            u'4': u'\u2074',
            u'7': u'\u2077',
            u'6': u'\u2076',
            u'8': u'\u2078',
            u'9': u'\u2079'

            }
    if s.isdigit():
        return ''.join([sups[i] for i in s])


super_script_values = [u'\xb9', u'\u2070', u'\xb3', u'\xb2', u'\u2075', u'\u2074', u'\u2077', u'\u2076', u'\u2079',
                       u'\u2078']

sections_dict = {}


def launch_instance(url, file_name):
    opts = Options()
    # opts.headless = True
    # assert opts.headless
    browser = Firefox(options=opts)
    browser.get(url)
    time.sleep(1)
    i = 1
    sections_dict["0"] = {
        "title": "Preamble",
        "subtitle": "Preamble",
        "content": [
            "\n",
            "\n"
        ],
        "footnotes": []
    }
    while True:
        if browser.find_element_by_link_text("Next").get_attribute('class') != 'disabled':

            sections_dict[str(i)] = get(browser)
            browser.find_element_by_link_text("Next").click()
            i = i + 1
        else:
            # i = i +1
            sections_dict[str(i)] = get(browser)
            break

    # write to file
    json_dump = {
        "act_details": {
            "act_name": "",
            "act_no": "",
            "act_year": "",
            "summary": "",
            "sections": "",
            "chapters": "",
            "enactment_date": "",
            "commencement_date": "",
            "enacted_by": "Parliament of India",
            "ministry": "",
            "department": ""
        },
        "tabs": [
            "CHAPTERS",
            "SCHEDULES",
            "ACT DETAILS"
        ],
        "contents": {
            "0": {
                "title": "All Sections",
                "subtitle": "-",
                "sections": "",
                "min_index": 0,
                "max_index": 0
            }, "1": {
                "title": "",
                "subtitle": "",
                "sections": "",
                "min_index": 0,
                "max_index": 0
            }
        },
        "sections": sections_dict,

        "schedules": []
    }

    # print(json_object)
    with open(file_name + '.json', 'w') as write_file:
        json.dump(json_dump, write_file)

    # quit and close browser
    browser.close()


def get(browser):
    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, features="html.parser")
    x = {
        "title": get_section_title(soup),
        "subtitle": get_section_subtitle(soup),
        "content": get_section_body(soup),
        "footnotes": get_section_footnotes(soup)
    }
    print(x)
    return x


def get_id(soup):
    section_heading = soup.find('p', {'class': 'sectionTitle title'})
    id = re.search(r"[^#]*$", section_heading.get('id'))
    return id


def get_section_title(soup):
    # The section heading
    section_heading = soup.find('p', {'class': 'sectionTitle title'})
    section_title = section_heading.find('span', {"class": 'label label-default'}).text
    section_title = section_title.lstrip(' ')
    section_title = section_title.rstrip('.')
    return section_title


def get_section_subtitle(soup):
    section_heading = soup.find('p', {'class': 'sectionTitle title'})
    section_subtitle = [re.strip() for re in section_heading if not re.name and re.strip()][0]
    return section_subtitle


def get_section_body(soup):
    # The section body || content
    section_body = soup.find("p", {"id": "secp" + get_id(soup).group()})
    data_body = []
    data_body_dup = []
    data_body_final = []
    for text in section_body.stripped_strings:
        result = text.replace('\n', ' ')
        if (len(result) == 1):
            data_body.append(to_sup(result))
            data_body_dup.append(to_sup(result))

        else:
            data_body.append(result)
            data_body_dup.append(result)

    for item in data_body:
        for supValue in super_script_values:

            if (supValue == item):
                val = data_body.index(item)
                newVal = len(data_body) - len(data_body_dup)
                val = val - newVal
                try:
                    data_body_dup[val - 1: val + 2] = [' '.join(data_body_dup[val - 1: val + 2])]
                except:
                    print(item)

    for item in data_body_dup:
        try:
            data_body_final.append(item + '\n')
        except:
            print(item)

    return data_body_final


def get_section_footnotes(soup):
    # The section footnotes
    section_footnotes = soup.find("p", {"id": "secf" + get_id(soup).group()})

    data_footnotes = []
    data_footnotes_dup = []
    data_footnotes_final = []

    for text in section_footnotes.stripped_strings:
        data_footnotes.append(text)
        data_footnotes_dup.append(text)

    for data in data_footnotes:
        if len(data.split()) > 1:
            val = data_footnotes.index(data)
            newVal = len(data_footnotes) - len(data_footnotes_dup)
            val = val - newVal
            data_footnotes_dup[val - 1: val + 2] = [' '.join(data_footnotes_dup[val - 1: val + 2])]

    for item in data_footnotes_dup:
        data_footnotes_final.append(item + '\n')
    return data_footnotes_final


if __name__ == '__main__':
    url = str(input('URL: '))
    file_name = str(input('Filename: '))
    # url = sys.argv[1]
    # file_name = sys.argv[2]
    launch_instance(url, file_name)
