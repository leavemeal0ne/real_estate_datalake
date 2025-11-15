from urllib.request import urlopen


class FlatsParser:
    __url = 'https://lun.ua/rent/uz/flats?sort=price-asc&page=1'

    def parse(self, url=None):
        if url is None:
            url = self.__url
        try:
           data = urlopen(url).read().decode('utf8')
        except UnicodeDecodeError as e:
            print(e)
            raise e
        except Exception as e:
            print(e)
            raise e
        else:
            return data