import re
from playwright.sync_api import sync_playwright
import time
import config.config as config
from models.Realty import Realty

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,timeout=3000)
        page = browser.new_page()
        page.goto("https://lun.ua/realty/3912350111")

        properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()

        while True:
            load_condition = [re.match('Знайдено', value) is not None for value in properties]
            if True in load_condition:
                break
            print("fault")
            time.sleep(0.5) # random value
            properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()

        price = page.locator('[class*="{}"]'.format(config.REALTY_PRICE_PATTERN)).first.text_content()

        location = page.locator('[class^="{}"]'.format(config.REALTY_LOCATION_PATTERN)).all_text_contents()

        description = page.locator('[class^="{}"]'.format(config.REALTY_DESCRIPTION_PATTERN)).first.text_content()

        properties = page.locator('[class^="{}"]'.format(config.REALTY_PROPERTIES_PATTERN)).all_text_contents()

        furniture = page.locator('[class^="{}"]'.format(config.REALTY_FURNITURE_PATTERN)).all_text_contents()

        browser.close()

        return (
            price,
            location,
            description,
            properties,
            furniture
        )



data = test()
object1 = Realty(
    realty_id=3912350111,
    price=data[0],
    location=data[1],
    description=data[2],
    properties=data[3].copy(),
    furniture=data[4],
    img_link='3232'
                 )