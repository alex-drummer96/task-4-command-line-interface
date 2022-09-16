import argparse
from unittest import mock
from unittest.mock import patch

import pytest

from counter_app import number_of_unique_characters as module

TEST_STRING = 'aabc'
TEST_FILE = 'strings.txt'
TEST_STRING_FROM_FILE = 'aabbc'


def test_cache() -> None:
    cases = [
        '',
        'asdf',
        '@#$;$@',
        '@#$;$@',
        "abbbccdf",
        "abbbccdf",
        'aawwccddd',
        '114jsdksjq wk1'
    ]
    number_of_calls_cache = 2
    for case in cases:
        module.count_unique_characters(string=case)
    assert module.count_unique_characters.cache_info().hits == number_of_calls_cache


@pytest.mark.parametrize('test_input, expected', [
    ('', 0), ('asdf', 4), ('@#$;$@', 2), ("abbbccdf", 3),
    ('aawwccddd', 0), ('114jsdksjq wk1', 5)
])
def test_count_unique_characters(test_input: str, expected: int) -> None:
    assert module.count_unique_characters(test_input) == expected


@pytest.mark.parametrize('test_input', [111, [111, 'dfvjndvj'], {1: 'xcvdfvdf'}])
def test_check_type(test_input: object) -> None:
    with pytest.raises(module.CustomTypeError) as excinfo:
        module.check_type(string=test_input)
    assert f'{type(test_input)} is not allowed. Only string' in str(excinfo.value)


@pytest.mark.parametrize('test_input', ['null', 111])
def test_check_filepath(test_input):
    with pytest.raises(module.MyException) as context:
        module.check_filepath(filepath=test_input)
    assert f'{test_input} is not a file path' in str(context)


@patch('counter_app.number_of_unique_characters.check_filepath', return_value=None)
def test_read_file(mock_check):
    test_file = 'any_file'
    with patch('builtins.open', mock.mock_open(read_data=TEST_STRING)) as open_mock:
        response = module.read_file(test_file)
        assert response == TEST_STRING
        open_mock.assert_called_with(test_file)
        mock_check.assert_called_once_with(test_file)


@patch('argparse.ArgumentParser.parse_args')
def test_cli_parser(mock_args):
    mock_args.return_value = argparse.Namespace(string=TEST_STRING, file_path=TEST_FILE)
    args = module.cli_parser()
    assert args.string == TEST_STRING
    assert args.file_path == TEST_FILE
    mock_args.assert_called_once()


@patch('counter_app.number_of_unique_characters.count_unique_characters', return_value=2)
@patch('counter_app.number_of_unique_characters.read_file')
@patch('counter_app.number_of_unique_characters.cli_parser',
       return_value=argparse.Namespace(string=TEST_STRING, file_path=None))
def test_logic_if_string(mock_parser, mock_read_file, mock_count_characters):
    response = module.app_logic()
    assert response == 2
    mock_read_file.assert_not_called()
    mock_parser.assert_called_once()
    mock_count_characters.assert_called_once()


@patch('counter_app.number_of_unique_characters.count_unique_characters', return_value=1)
@patch('counter_app.number_of_unique_characters.read_file', return_value=TEST_STRING_FROM_FILE)
@patch('counter_app.number_of_unique_characters.cli_parser',
       return_value=argparse.Namespace(string=TEST_STRING, file_path=TEST_FILE))
def test_logic_if_file(mock_parser, mock_read, mock_count_characters):
    response = module.app_logic()
    assert response == 1
    mock_parser.assert_called_once()
    mock_read.assert_called_once_with(TEST_FILE)
    mock_count_characters.assert_called_once()


@patch('counter_app.number_of_unique_characters.count_unique_characters', return_value=None)
@patch('counter_app.number_of_unique_characters.cli_parser')
def test_atypical_logic(mock_parser, mock_count_characters):
    mock_parser.return_value = argparse.Namespace(string=None, file_path=None)
    with pytest.raises(module.MyException) as context:
        module.app_logic()
    assert 'You must enter arguments --string or --file_path' in str(context)
    mock_parser.assert_called_once()
    mock_count_characters.assert_not_called()
