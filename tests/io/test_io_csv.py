from typing import List

from trailblazer.io.csv import read_csv_stream


def test_get_content_from_stream(csv_stream: str):
    """
    Tests read CSV stream.
    """
    # GIVEN a string in csv format

    # WHEN reading the csv content in string
    raw_csv_content: List[List[str]] = read_csv_stream(stream=csv_stream)

    # THEN assert a list is returned
    assert isinstance(raw_csv_content, List)

    # THEN the content should match the expected content
    expected_content = [
        ["Lorem", "ipsum", "sit", "amet"],
        ["value_1", "value_2", "value_3", "value_4"],
    ]
    assert raw_csv_content == expected_content


def test_get_content_from_stream_to_dict(csv_stream: str):
    """
    Tests read CSV stream into a dict.
    """
    # GIVEN a string in csv format

    # WHEN reading the csv content in string
    raw_csv_content: List[List[str]] = read_csv_stream(read_to_dict=True, stream=csv_stream)

    print(raw_csv_content)
    # Then assert a list is returned and that the first element is a dict
    assert isinstance(raw_csv_content, list)
    assert isinstance(raw_csv_content[0], dict)
