import os

import requests
import re
from bs4 import BeautifulSoup
import config.config as config
from utils.TagFilter import flat_filter
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
from models.Realty import Realty
from datetime import date
import csv
import math

class FlatsParser:
                            #flats?insert_date_min=2025-11-22&insert_date_max=2025-11-25&sort=insert_time&page=12
    __lun_realty_kyiv_url = 'https://lun.ua/rent/kyiv/flats?insert_date_min={d_min}&insert_date_max={d_max}&sort=insert_time&page={page_n}&geoDistance=10009580%3A0'
    __lun_realty_url = 'https://lun.ua/realty/{}'
    __page_load_timeout_ms = 10000 #10s
    __locator_timeout_ms = 10000 #10s
    __max_number_of_pages = 2 #10000000000
    __count_of_unites_per_page = 24
    __file_format = 'realty_data_{date}.csv'
    __realty_count_pattern = r'.?RealtiesTitle_resultsCount.?'

    def extract_units_count_from_lun_page(self,html_page):
        soup = BeautifulSoup(html_page, 'html.parser')
        result_tag = soup.find('span', class_=re.compile(self.__realty_count_pattern))
        text = result_tag.text.replace(" ","").replace("\u00A0", "")
        units_count_pattern = r'по(\d+)о.*?'
        try:
            units_count = int(re.search(units_count_pattern, text,flags=re.IGNORECASE).groups()[0])
        except ValueError as e:
            print("Unable to parse count of units")
            raise e
        else:
            return units_count

    def get_number_of_pages(self,number_of_units):
        return math.ceil(number_of_units/self.__count_of_unites_per_page)

    def extract_realty_ids_from_lun_page(self,html_page):
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
        ids = [self.extract_id_from_flat_tag(flat) for flat in flats_data]
        return ids

    def extract_id_from_flat_tag(self,flat):
        unique_id_tag = flat.find('div', class_=re.compile(config.FLAT_ID_PATTERN))
        unique_id_text = re.findall('[0-9]+', unique_id_tag['data-event-options'])[0]
        try:
            unique_id_int = int(unique_id_text)
        except ValueError as e:
            print(e, "text_value={text_value}".format(text_value=unique_id_text))
            raise e
        else:
            return unique_id_int

    def parse_realty_by_id(self,realty_id):
        with Stealth().use_sync(sync_playwright()) as p:
            print("processing {}".format(realty_id))
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            context.set_default_timeout(self.__page_load_timeout_ms)
            context.set_default_navigation_timeout(self.__locator_timeout_ms)
            page = context.new_page()
            try:
                start_time = time.time()
                response = page.goto(self.__lun_realty_url.format(realty_id))
                if response.status != 200:
                    raise Exception("response status is not 200")
                properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()
                while True:
                    load_condition = [re.match('Знайдено', value) is not None for value in properties]
                    if True in load_condition:
                        end_time = time.time()
                        print("time of loading {} page is {:.2f}s".format(realty_id, end_time - start_time))
                        break
                    time.sleep(0.005)  # random value
                    properties = page.locator(
                        '[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()

                main = page.locator('[class^="Realty_main"]')
                properties = main.locator(f'[class^="{config.REALTY_PROPERTIES_PATTERN}"]').all_text_contents()
                price = main.locator(f'[class*="{config.REALTY_PRICE_PATTERN}"]').first.text_content()
                location = main.locator(f'[class^="{config.REALTY_LOCATION_PATTERN}"]').all_text_contents()
                description = main.locator(f'[class^="{config.REALTY_DESCRIPTION_PATTERN}"]').first.text_content()
                furniture = main.locator(f'[class^="{config.REALTY_FURNITURE_PATTERN}"]').all_text_contents()
                img_link = main.locator(f'[class^="{config.REALTY_GALLERY_SLIDER_PATTERN}"] img').first.get_attribute(
                    'src')

                browser.close()
                realty_object = Realty(
                    realty_id=realty_id,
                    price=price,
                    location=location,
                    description=description,
                    furniture=furniture,
                    properties=list(properties),
                    img_link=img_link)
                return realty_object

            except Exception as e:
                print(e)
                print("failed to load {} page".format(realty_id))
                return None


    def extract_kyiv_realty_by_date(self,search_date:date):
        if not isinstance(search_date,date):
            raise ValueError("date object must be of type datetime, instead get:{} ".format(type(date)))
        all_realty = []
        str_date = search_date.strftime("%Y-%m-%d")
        page_url = self.__lun_realty_kyiv_url.format(d_min=str_date,d_max=str_date,page_n=1)
        try:
            response = requests.get(page_url)
        except requests.exceptions.RequestException as e:
            print("error while parsing page for units count", e)
            raise e
        else:
            count_of_units = self.extract_units_count_from_lun_page(response.text)
            start_page = self.get_number_of_pages(count_of_units)
            for page_number in range(start_page, 0,-1):
                page_url = self.__lun_realty_kyiv_url.format(d_min=str_date,d_max=str_date,page_n=page_number)
                print(page_url)
                try:
                    response = requests.get(page_url)
                except requests.exceptions.RequestException as e:
                    print("error while parsing page", e)
                    continue
                else:
                    # extract_realty_ids_from_lun_page will return None if there is no more realty data
                    ids = self.extract_realty_ids_from_lun_page(response.text)
                    if ids is None:
                        break
                    # get realty object by id
                    realty_objects = [self.parse_realty_by_id(realty_id) for realty_id in ids]
                    all_realty.extend(realty_objects)
                    # check for realty objects with different search date
                    stop_condition = True in [realty.get_discovery_date() != search_date if realty is not None else False for realty in realty_objects]
                    # stop search if there are no more relevant realty object
                    if stop_condition:
                        break
            # clear realty list from None values and irrelevant objects
            all_realty = [realty for realty in all_realty if realty is not None and realty.get_discovery_date() == search_date]
            return all_realty

    def write_realty_to_a_csv(self,realty_data,date,file_format=None,file_location='/opt/airflow/data'):
        if len(realty_data) == 0:
            raise ValueError("data cannot be empty")
        file_format = self.__file_format if file_format is None else file_format
        file_name = file_format.format(date=date)
        if not file_location is None:
            file_name = os.path.join(file_location, file_name)
        with open(file_name, 'w', encoding='utf-8',newline="") as f:
            writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(Realty.list_representation_fields())
            writer.writerows(realty_data)
        return file_name

    def create_Kyiv_realty_data_by_date(self,search_date:date):
        start_time = time.time()
        raw_data = self.extract_kyiv_realty_by_date(search_date)
        prepared_data = [realty.list_representation() for realty in raw_data]
        file_name = self.write_realty_to_a_csv(realty_data=prepared_data,date=search_date)
        end_time = time.time()
        print('processing time of {} is: {:.2f}m'.format(file_name,(end_time - start_time) / 60))
        return file_name


    # def extract_realty_data(self):
    #     all_realty = []
    #     for page_number in range(1, self.__max_number_of_pages):
    #         page_url = config.REALTY_PAGE_URL.format(page_number=page_number)
    #         try:
    #             response = requests.get(page_url)
    #         except requests.exceptions.RequestException as e:
    #             print("error while parsing page", e)
    #             return None
    #         else:
    #             ids = self.extract_realty_ids_from_lun_page(response.text)
    #             if ids is None:
    #                 break
    #             realty_objects = [self.parse_realty_by_id(realty_id) for realty_id in ids]
    #             all_realty.extend(realty_objects)
    #     all_realty = [realty.list_representation() for realty in all_realty if realty is not None]
    #     all_realty.insert(0, Realty.list_representation_fields())
    #     return all_realty