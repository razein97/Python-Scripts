# In order to scrape the income tax act you have to get the json response that is being fetched
# by the iframe which displays the sections
# Do it by going the debugger of browser and monitoring for json response
# Date and Time of Current Url Path = 19-07-2020
# In the future the script may need to be updated


import json
import urllib.request
from bs4 import BeautifulSoup

act_name_income_tax = "Income Tax Act(1961-2020)"
act_name_finance_act = "Finance Act, 2020"
url_path_income_tax = "https://www.incometaxindia.gov.in/_vti_bin/taxmann.iti.webservices/DataWebService.svc/GetFileContentsByCMSID?cval=102120000000075597&grp=Act&searchFilter=%5B%7B%22CrawledPropertyKey%22%3A1%2C%22Value%22%3A%22Act%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A0%2C%22Value%22%3A%22Income-tax%20Act%2C%201961%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A29%2C%22Value%22%3A%222020%22%2C%22SearchOperand%22%3A2%7D%5D&filterBy=S&opt=&k="
url_path_finance_act = "https://www.incometaxindia.gov.in/_vti_bin/taxmann.iti.webservices/DataWebService.svc/GetFileContentsByCMSID?cval=102520000000111072&grp=Act&searchFilter=%5B%7B%22CrawledPropertyKey%22%3A1%2C%22Value%22%3A%22Act%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A0%2C%22Value%22%3A%22Finance%20Acts%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A29%2C%22Value%22%3A%222020%22%2C%22SearchOperand%22%3A2%7D%5D&filterBy=S&opt=&k="
sections_dict = {}


def start_parse():
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

    if input_int == 1:
        link_to_parse = url_path_income_tax
        act_name = act_name_income_tax
    else:
        link_to_parse = url_path_finance_act
        act_name = act_name_finance_act

    while True:
        json_data = load_json_data(link_to_parse)

        if json_data['NextLink'] is not None:
            sections_dict[str(i)] = parse_data(json_data)
            link_to_parse = process_link(json_data)
            i = i + 1
        else:
            break

    # write to file
    json_dump = {
        "act_details": {
            "act_name": act_name,
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

    # final out to json
    with open(act_name_income_tax if input_int == 1 else act_name_finance_act + '.json', 'w') as write_file:
        json.dump(json_dump, write_file)


# Loads the json file from the url
def load_json_data(parse_url):
    with urllib.request.urlopen(parse_url) as url:
        data = json.loads(url.read().decode())
        return data


# Gets the title from the json and then processes html content
def parse_data(jsn_data):
    section_title = jsn_data['Title']
    if input_int == 1:
        section_title = section_title.replace(', Income-tax Act, 1961-2020', '')
    else:
        section_title = section_title.replace(', Finance Acts-2020', '')
    section_title = section_title.replace(' - ', ' ')

    html_content = jsn_data['HtmlContent']
    # html content process
    processed_html_content = process_html_content(html_content)

    # get subtitle from processed html
    section_subtitle = processed_html_content[0].replace("\n", "")

    # remove the subtitle from processed_html_content
    del processed_html_content[0]

    x = {
        "title": section_title,
        "subtitle": section_subtitle,
        "content": processed_html_content,
        "footnotes": ["\n", "\n", "\n"]
    }
    print(x)
    return x


# Gets the CVAL which is required to fetch next section link
def process_link(jsn_data):
    nextlink = jsn_data['NextLink']
    link = nextlink.replace('javascript: ', '')

    split_link = link.split(',')
    cval = split_link[2].replace(r"'", "")
    cval = cval.strip()

    reconstructed_link_income_tax = "https://www.incometaxindia.gov.in/_vti_bin/taxmann.iti.webservices/DataWebService.svc/GetFileContentsByCMSID?cval=" + cval + \
                                    "&grp=Act&searchFilter=%5B%7B%22CrawledPropertyKey%22%3A1%2C%22Value%22%3A%22Act%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A0%2C%22Value%22%3A%22Income-tax%20Act%2C%201961%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A29%2C%22Value%22%3A%222020%22%2C%22SearchOperand%22%3A2%7D%5D&filterBy=S&opt=&k="

    reconstructed_link_finance_act = "https://www.incometaxindia.gov.in/_vti_bin/taxmann.iti.webservices/DataWebService.svc/GetFileContentsByCMSID?cval=" + cval + \
                                     "&grp=Act&searchFilter=%5B%7B%22CrawledPropertyKey%22%3A1%2C%22Value%22%3A%22Act%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A0%2C%22Value%22%3A%22Finance%20Acts%22%2C%22SearchOperand%22%3A2%7D%2C%7B%22CrawledPropertyKey%22%3A29%2C%22Value%22%3A%222020%22%2C%22SearchOperand%22%3A2%7D%5D&filterBy=S&opt=&k="

    if input_int == 1:
        return reconstructed_link_income_tax
    else:
        return reconstructed_link_finance_act


# Html content sanitised by removing residual html tags and spaces and adding to a list
def process_html_content(html_cont):
    soup = BeautifulSoup(html_cont, features='html.parser')
    tempList = []

    content = soup.get_text()
    split_content = content.splitlines()

    for line in split_content:
        space_removed = line.strip()
        spaces_removed = space_removed.replace('\xa0\xa0', ' ')
        i_tag_removed = spaces_removed.replace(r'<\/i>', '')
        a_tag_removed = i_tag_removed.replace(r'<\/a>', '')
        b_tag_removed = a_tag_removed.replace(r'<\/b>', '')
        p_tag_removed = b_tag_removed.replace(r'<\/p>', '')
        if p_tag_removed != "":
            tempList.append(p_tag_removed + '\n')
        else:
            pass

    return tempList


if __name__ == '__main__':
    print("Which act to scrape: ")
    print("1. Income Tax Act")
    print("2. Finance Act")
    global input_int
    input_int = int(input('Enter Option:'))
    start_parse()
