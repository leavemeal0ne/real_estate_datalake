# url adresses
PARSE_URL = 'https://lun.ua/rent/uz/flats?sort=price-asc&page={page_number}'
FLAT_BASE_URL = 'https://lun.ua/realty/'

# last page flag
FLAT_EMPTY_ROOT='^RealtiesEmpty_root*?'

# value of class attribute of flat div
FLAT_BASE_PATTERN='^RealtiesLayout_resultsItem__xapRs$'

# div which contains unique id of flat
FLAT_ID_PATTERN='^MenuItem-module_root*?'

# divs with common data
FLAT_PRICE_PATTERN='^RealtyCard_price_*?' # class_
FLAT_LOCATION_PATTERN='^RealtyCard_title_*?' # class_ IT'S IN A H3 TAG
FLAT_DESCRIPTION_PATTERN='^RealtyCard_description_*?' # class_

# additional data grid
FLAT_GRID_DATA_PATTERN='^RealtyCard_propertyGrid_*?' # class_
# data grid element
FLAT_DATA_INSIDE_GRID_PATTERN='^RealtyPropertiesItem_text*?' # class_

#REALTY DATA FOR INDIVIDUAL UNIT
REALTY_PRICE_DATA = '^RealtyDetails_priceMain_*?$'
REALTY_LOCATION_DATA = "^RealtyLocation_item_*?$" #class_ in a tag, may contain 2 or more values
#realty details data inside the grid container
REALTY_DETAILS_DATA = '^RealtyPropertiesItem_text_*?$'
RALTY_DESCRIPTION_DATA = 'ExpandableText_text'

