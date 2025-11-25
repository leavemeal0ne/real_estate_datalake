from FlatParser.FlatParser import FlatsParser
import datetime

def main():
    parse_date = datetime.date.today() - datetime.timedelta(days=5)
    print(parse_date)
    FlatsParser().create_Kyiv_realty_data_by_date(parse_date)

if __name__ == '__main__':
    main()