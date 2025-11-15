import os

import requests
import re
from bs4 import BeautifulSoup
from config.config import *
from utils.TagFilter import flat_filter



def extract_data_from_page(html_page:str):
    """
    This function extracts id`s of flat`s from page
    :param html_page:
    :return:
    """
    soup = BeautifulSoup(html_page, 'html.parser')
    # collect all div's with flat data
    unclear_flats_data = soup.find_all(flat_filter)
    # some div's collect no data
    flats_data = [flat for flat in unclear_flats_data if len(flat.text) != 0]
    ids = []
    for flat in flats_data:
        flat_id = extract_id_from_flat_tag(flat)
        #if id == -1:
        ids.append(flat_id)
    return ids

def extract_id_from_flat_tag(flat):
    # add logic of presence of data
    unique_id_tag = flat.find('div', class_=re.compile(FLAT_ID_PATTERN))
    unique_id_text = re.findall('[0-9]+', unique_id_tag['data-event-options'])[0]
    try:
        unique_id_int = int(unique_id_text)
    except ValueError as e:
        print(e, "text_value={text_value}".format(text_value=unique_id_text))
        return -1
    else:
        return unique_id_int

"""
    def extract_data_from_flat_tag(flat:bs4.element.Tag):
        price_tag = flat.find('div', class_=re.compile(FLAT_PRICE_PATTERN))
        location_tag = flat.find('h3', class_=re.compile(FLAT_LOCATION_PATTERN))
        description_tag = flat.find('div', class_=re.compile(FLAT_DESCRIPTION_PATTERN))
        unique_id_tag = flat.find('div',class_=re.compile(FLAT_ID_PATTERN))
        unique_id_text = re.findall('[0-9]+', unique_id_tag['data-event-options'])[0]
        print(price_tag.text, location_tag.text, len(description_tag.text), unique_id_text)
"""

def parse_flat_by_id(flat_id):


def flats_parser():
    for page in range(1,11):
        url = PARSE_URL.format(page_number=page)


def test():
    url = PARSE_URL.format(page_number=1)
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("error while parsing page", e)
        return
    else:
        html_page = response.text
        ids = extract_data_from_page(html_page)
        print(ids)

if __name__ == '__main__':
    test()
