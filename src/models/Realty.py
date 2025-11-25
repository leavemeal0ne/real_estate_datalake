import re
from utils.DateFormatter import DateFormatter

"""
obj values:
realty_id: e.g. lun_12312 dim_ria_123221

location:
price:
description:
img_link:

count_of_rooms
description:

main_room_square
kitchen_square
bathroom_square

property_dict
furniture_dict

realty_floor
realty_max_floors

update_date
discovery_date
"""
class Realty:
    __realty_url = 'https://lun.ua/realty/{}'
    __list_of_rooms = ['main_room',
                     'kitchen',
                     'bathroom']
    __recent_date_pattern = r'^(знайдено|оновлено)\s+(сьогодні|вчора)(|\s+о\s+\d+:\d+)$'
    def __init__(
            self,*,
            realty_id,
            price,
            location,
            description,
            properties,
            furniture,
            img_link):
        self.__price_process(price)
        self.__img_link = img_link
        self.__realty_id = realty_id
        self.__location = " - ".join(location)
        self.__description = re.sub('\n\n','\n', description)
        self.__property_process(properties)
        self.__process_furniture(furniture)

    def __property_process(self, properties):
        self.__process_count_of_rooms_p(properties) # count of rooms
        self.__process_rooms_square_p(properties)
        self.__process_floor_p(properties)
        self.__process_update_date_p(properties)
        self.__process_discovery_date_p(properties)
        self.__property_dict = {}
        for property_value in properties:
            self.__property_dict[property_value] = True
        return

    def __process_furniture(self, furniture):
        self.__furniture_dict = {}
        for furniture_value in furniture:
            self.__furniture_dict[furniture_value] = True
        return

    def __process_date_property(self, properties, keyword, attr_name):
        for i, prop in enumerate(properties):
            if re.search(keyword, prop, flags=re.IGNORECASE):
                recent_date_condition, value = self.__recent_date_info(prop)

                if recent_date_condition:
                    date_value = DateFormatter.date_formatter(value)
                else:
                    date_value = DateFormatter.date_formatter(
                        re.search(r'(.+? )(\d+ .+)', prop, flags=re.IGNORECASE).groups()[1]
                    )

                setattr(self, attr_name, date_value)
                properties.pop(i)
                return

        raise ValueError(f"no {keyword} date")

    def __process_discovery_date_p(self, properties):
        self.__process_date_property(properties, "знайдено", "_{}__discovery_date".format(self.__class__.__name__))

    def __process_update_date_p(self, properties):
        self.__process_date_property(properties, "оновлено", "_{}__update_date".format(self.__class__.__name__))


    def __recent_date_info(self, date_str):
        today_yesterday_match = re.search(pattern=self.__recent_date_pattern,
                                          string=date_str, flags=re.IGNORECASE)
        if today_yesterday_match is not None:
            return True, "".join(today_yesterday_match.groups()[1:])
        else:
            return False, None


    #process count of rooms property
    def __process_count_of_rooms_p(self,properties:list):
        for i, prop in enumerate(properties):
            if re.search(pattern='кімнат',string=prop,flags=re.IGNORECASE) is not None:
                count_of_rooms = re.sub('[^0-9]','',prop)
                try:
                    count_of_rooms = int(count_of_rooms)
                except ValueError as e :
                    print("Value has not digits signs, value {}".format(count_of_rooms))
                    raise e
                else:
                    self.__count_of_rooms = count_of_rooms
                    properties.pop(i)
                    return
        raise ValueError("There is no property with count of rooms data")

    #process square of rooms property
    def __process_rooms_square_p(self,properties:list):
        for i, prop in enumerate(properties):
            pattern = '([0-9]+|-)/([0-9]+|-)/([0-9]+|-)' #some units may contain only main room value e.g '38 m2' or '60.9 / 30.1 / 12.7 м²'
            prop = re.sub(' ','',prop)
            match = re.search(pattern=pattern, string=prop, flags=re.IGNORECASE)
            if match is not None:
                rooms_data  = match.group().split('/')
                try:
                    rooms_data = [int(room) if room != '-' else room for room in rooms_data]
                except ValueError as e:
                    print("Value has not digits signs, value {}".format(rooms_data))
                    raise e
                else:
                    for room_value in zip(self.__list_of_rooms,rooms_data):
                        value = room_value[1] if isinstance(room_value[1], int) else None
                        setattr(self, f"_{self.__class__.__name__}__{room_value[0]}_square", value)
                    properties.pop(i)
                    return
        raise ValueError("There is no property with square of rooms data")


    #process floor of realty
    def __process_floor_p(self,properties:list):
        for i, prop in enumerate(properties):
            search_pattern = 'поверх'
            data_pattern = '([0-9]+)([^0-9]| )+([0-9]+)'
            match = re.search(pattern=search_pattern, string=prop, flags=re.IGNORECASE)
            if match is not None:
                floor_match = re.search(pattern=data_pattern, string=prop, flags=re.IGNORECASE).groups()
                try:
                    floor_match = [floor_match[0],floor_match[2]]
                    floor_match = [int(floor) for floor in floor_match]
                except (IndexError,ValueError) as e:
                    print("Wrong floor parse result: {}".format(floor_match))
                    raise e
                else:
                    self.__realty_floor = floor_match[0]
                    self.__realty_max_floors = floor_match[1]
                    properties.pop(i)
                    return

        raise ValueError("There is no property with floor number")


    def __price_process(self,price):
        price = re.sub('[^0-9]','',price)
        try:
            price = int(price)
        except ValueError as e:
            print("Value has not digits signs, value {}".format(price))
            raise e
        else:
            self.__price = price

    @staticmethod
    def list_representation_fields():
        return ["id",
                "price",
                "location",
                "count_of_rooms",
                "realty_floor",
                "realty_max_floors",
                "main_room_square",
                "kitchen_square",
                "bathroom_square",
                "discovery_date"]

    def  list_representation(self):
            return [
                self.__realty_id,
                self.__price,
                self.__location,
                self.__count_of_rooms,
                self.__realty_floor,
                self.__realty_max_floors,
                self.__main_room_square,
                self.__kitchen_square,
                self.__bathroom_square,
                self.__discovery_date.strftime('%Y-%m-%d'),
                self.__property_dict,
                self.__furniture_dict]

    def __str__(self):
        str_value = "Realty object;\nprice : {}\ncount of rooms : {}\nlocation : {}".format(
     self.__price,
            self.__count_of_rooms,
            self.__location
        )
        return str_value
