from brandshop_bot.parser import parser
from brandshop_bot.params import SOURCE_URL
import asyncio


def main():
    asyncio.run(parser.get_all_items(SOURCE_URL))


if __name__ == '__main__':
    main()
