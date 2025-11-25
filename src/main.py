from FlatParser import FlatsParser
import time
import csv
def main():
    start_time = time.time()
    parser = FlatsParser()
    realty_objects = parser.extract_realty_data()
    print(len(realty_objects))
    end_time = time.time()
    print("{:.2f}m".format((end_time - start_time) / 60))
    return realty_objects

if __name__ == '__main__':
    data = main()
    with open("test_data.csv", "w", encoding='utf-8',newline="") as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)