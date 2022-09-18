from parser import parser
from params import SOURCE_URL
import asyncio
from datetime import datetime


def main():
    asyncio.run(parser.get_all_items(SOURCE_URL))


if __name__ == '__main__':
    main()
