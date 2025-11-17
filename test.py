import requests
import re
from bs4 import BeautifulSoup
import config.config as config
from utils.TagFilter import flat_filter
from playwright.sync_api import sync_playwright
import time
from models.Realty import Realty


def extract_realty_ids_from_lun_page(html_page:str):
    """
    This function extracts id`s of flat`s from page
    :param html_page:
    :return: list of id`s
    """
    soup = BeautifulSoup(html_page, 'html.parser')
    empty_result_condition = soup.find('div', class_=re.compile(config.REALTY_EMPTY_ROOT)) is not None
    if empty_result_condition:
        return None
    # collect all divs with flat data
    flats_data = soup.find_all(flat_filter)
    ids = [extract_id_from_flat_tag(flat) for flat in flats_data]
    return ids

def extract_id_from_flat_tag(flat):
    unique_id_tag = flat.find('div', class_=re.compile(config.FLAT_ID_PATTERN))
    unique_id_text = re.findall('[0-9]+', unique_id_tag['data-event-options'])[0]
    try:
        unique_id_int = int(unique_id_text)
    except ValueError as e:
        print(e, "text_value={text_value}".format(text_value=unique_id_text))
        raise e
    else:
        return unique_id_int

def parse_realty_by_id(realty_id):
    with sync_playwright() as p:
        print("processing {}".format(realty_id))
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto("https://lun.ua/realty/{}".format(realty_id),timeout=30000) #30000 ms = 30 s
            properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()
            start_time = time.time()
            while True:
                load_condition = [re.match('Знайдено', value) is not None for value in properties]
                if True in load_condition:
                    end_time = time.time()
                    print("time of loading {} page is {}".format(realty_id, end_time - start_time))
                    break
                time.sleep(0.005)  # random value
                properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()

            price = page.locator('[class*="{}"]'.format(config.REALTY_PRICE_PATTERN)).first.text_content()
            location = page.locator('[class^="{}"]'.format(config.REALTY_LOCATION_PATTERN)).all_text_contents()
            description = page.locator('[class^="{}"]'.format(config.REALTY_DESCRIPTION_PATTERN)).first.text_content()
            properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()
            furniture = page.locator('[class^="{}"]'.format(config.REALTY_FURNITURE_PATTERN)).all_text_contents()
            img_link = page.locator('[class^="{}"]'.format(config.REALTY_GALLERY_SLIDER_PATTERN)
                                    ).first.locator('img').first.get_attribute('src')
            browser.close()
            realty_object = Realty(
                realty_id=realty_id,
                price=price,
                location=location,
                description=description,
                furniture=furniture,
                properties=properties,
                img_link=img_link)
            return realty_object

        except Exception as e:
            print(e)
            print("failed to load {} page".format(realty_id))
            return None



def extract_realty_data():
    all_realty = []
    for page_number in range(1,10000000):
        page_url =  config.REALTY_PAGE_URL.format(page_number=page_number)
        try:
            response = requests.get(page_url)
        except requests.exceptions.RequestException as e:
            print("error while parsing page", e)
            return None
        else:
            ids = extract_realty_ids_from_lun_page(response.text)
            if ids is None:
                break
            realty_objects = [parse_realty_by_id(realty_id) for realty_id in ids]
            all_realty.extend(realty_objects)

    return all_realty

if __name__ == '__main__':
    start_time = time.time()
    realty_objects = extract_realty_data()
    print(len(realty_objects))
    end_time = time.time()
    print((end_time - start_time)/60)