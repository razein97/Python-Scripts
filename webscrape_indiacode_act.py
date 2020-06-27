import json
import re
import time
import os.path

from bs4 import BeautifulSoup
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

s_act_name = "Short Title: "
s_act_number = "Act Number: "
s_act_year = "Act Year: "
s_act_summary = "Long Title: "
s_enactment_date = "Enactment Date: "
s_enforcement_date = "Enforcement Date: "
s_ministry = "Ministry: "
s_department = "Department: "


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


# Start Scrape
def scrape(url):
    opts = Options()
    # opts.headless = True
    # assert opts.headless
    browser = Firefox(options=opts)
    link_text = url

    # get the sections
    act_details = get_act_details(link_text, browser)
    section_data = get_section_data(link_text, browser)

    # write it to a json file
    write_json_data(act_details, section_data)

    # quit and close the browser
    browser.close()


# This will get the act details from the link you passed
def get_act_details(url, browser):
    browser.get(url)
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source, features='html.parser')

    act_name = '-'
    act_no = '-'
    act_year = '-'
    act_summary = '-'
    enactment_date = '-'
    commencement_date = '-'
    enacted_by = 'Parliament of India'
    ministry = '-'
    department = '-'
    act_dets = soup.find('table', {'class': 'table itemDisplayTable'})
    rows = act_dets.find_all('tr')
    for row in rows:

        xx = row.find_all('td')
        td = xx[0].get_text()
        if td == s_act_name:
            act_name = xx[1].get_text()
        elif td == s_act_number:
            act_no = xx[1].get_text()
        elif td == s_act_year:
            act_year = xx[1].get_text()
        elif td == s_act_summary:
            act_summary = xx[1].get_text()
        elif td == s_enactment_date:
            enactment_date = xx[1].get_text()
        elif td == s_enforcement_date:
            commencement_date = xx[1].get_text()
        elif td == s_ministry:
            ministry = xx[1].get_text()
        elif td == s_department:
            department = xx[1].get_text()

    act_details = {
        "act_name": act_name,
        "act_no": act_no,
        "act_year": act_year,
        "summary": act_summary,
        "sections": "",
        "chapters": "",
        "enactment_date": enactment_date,
        "commencement_date": commencement_date,
        "enacted_by": enacted_by,
        "ministry": ministry,
        "department": department
    }

    return act_details


sections_dict = {}


def get_section_data(url, browser):
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, features='html.parser')
    # -------------------------
    act_table = soup.find('table', {'id': 'myTableActSection'})
    section_container = act_table.find('div', {'id': 'accordion1'})
    link = section_container.find('a', href=True)
    section1link = 'https://indiacode.nic.in' + link['href']
    # -----------------------------

    browser.get(section1link)
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

            sections_dict[str(i)] = get_section_details(browser)
            browser.find_element_by_link_text("Next").click()
            i = i + 1
        else:
            # i = i +1
            sections_dict[str(i)] = get_section_details(browser)
            break

    return sections_dict


def get_section_details(browser):
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


def write_json_data(act_details_write, section_data_write):
    json_dump = {
        "act_details": act_details_write,
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
        "sections": section_data_write,

        "schedules": []
    }

    filename = act_details_write["act_name"]

    with open(filename + '.json', 'w') as write_file:
        json.dump(json_dump, write_file)


if __name__ == '__main__':
    print("###########################################################################################################")
    print("|                                                                                                         |")
    print("|                                 INDIA CODE WEBPAGE SCRAPER                                              |")
    print("|                                                                                                         |")
    print("###########################################################################################################")
    print("|        Please note that the scraping of copyright content is ILLEGAL. DO SO AT YOUR OWN RISK.           |")
    print("###########################################################################################################")

    url = str(input(
        'Enter The Act Url To Scrape(https://www.indiacode.nic.in/handle/xxxxx/xxxxx?view_type=browse&sam_handle=xxxxxx): '))
    scrape(url)
