from FlatParser.FlatParser import FlatsParser
import datetime
import time

def main():
    FlatsParser().create_Kyiv_realty_data_by_date(datetime.date.today())

if __name__ == '__main__':
    main()