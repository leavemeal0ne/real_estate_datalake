from FlatParser import FlatsParser as fp

def main():
    parser = fp()
    print(parser.parse())

if __name__ == '__main__':
    main()