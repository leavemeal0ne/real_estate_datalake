import re
class Realty:
    __realty_url = 'https://lun.ua/realty/'
    __list_of_rooms = ['main_room',
                     'kitchen',
                     'bathroom']
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
        self.__id = realty_id
        self.__location = " - ".join(location)
        self.__description = re.sub('\n\n','\n', description)
        self.__property_process(properties)
        self.__process_furniture(furniture)

    def __property_process(self, properties):
        self.__process_count_of_rooms_p(properties) # count of rooms
        self.__process_rooms_square_p(properties)
        self.__process_floor_p(properties)

    def __process_furniture(self, furniture):
        self.__furniture_dict = {}
        for furniture_value in furniture:
            self.__furniture_dict[furniture_value] = True
        return


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
            pattern = '([0-9]+|-)/([0-9]+|-)/([0-9]+|-)'
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
                        setattr(self, f"__{room_value[0]}_square", value) # change to modify dict
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
                except IndexError as e:
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