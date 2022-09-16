import argparse
import os
from collections import Counter
from functools import lru_cache


class CustomTypeError(Exception):
    def __init__(self, data_type: type) -> None:
        self.data_type = data_type

    def __str__(self) -> str:
        return f'{self.data_type} is not allowed. Only string'


class MyException(Exception):
    pass


def check_type(string: str) -> None:
    if not isinstance(string, str):
        raise CustomTypeError(type(string))


@lru_cache(maxsize=None)
def count_unique_characters(string: str) -> int:
    check_type(string=string)
    letter_count = Counter(string)
    return len([key for key in letter_count if letter_count[key] == 1])


def check_filepath(filepath: str) -> None:
    if not os.path.isfile(filepath):
        raise MyException(f'{filepath} is not a file path')


def read_file(filepath: str) -> str:
    check_filepath(filepath)
    with open(filepath) as file:
        return file.read()


def cli_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-st', '--string', help='Your string')
    parser.add_argument('-f', '--file_path', help='Path to your file')
    return parser.parse_args()


def app_logic() -> int:
    args = cli_parser()
    if not (args.file_path or args.string):
        raise MyException('You must enter arguments --string or --file_path')
    if args.file_path:
        string = read_file(args.file_path)
        return count_unique_characters(string=string)
    return count_unique_characters(string=args.string)
