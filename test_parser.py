import re
from playwright.sync_api import sync_playwright
import time

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://lun.ua/realty/3912350111")

        elements = page.locator('[class^="RealtyPropertiesItem_text"]')
        texts = elements.all_text_contents()

        while True:
            load_condition = [re.match('Знайдено', value) is not None for value in texts]
            if True in load_condition:
                break
            print("fault")
            time.sleep(0.5) # random value
            elements = page.locator('[class^="RealtyPropertiesItem_text"]')
            texts = elements.all_text_contents()

        browser.close()
        print(texts)
        return texts

test()