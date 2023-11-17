from trailblazer.io.csv import read_csv_stream


def test_get_content_from_stream(csv_stream: str):
    """Tests read CSV stream."""
    # GIVEN a string in CSV format

    # WHEN reading the CSV content in string
    raw_csv_content: list[list[str]] = read_csv_stream(stream=csv_stream)

    # THEN assert a list is returned
    assert isinstance(raw_csv_content, list)

    # THEN the content should match the expected content
    expected_content = [
        ["Lorem", "ipsum", "sit", "amet"],
        ["value_1", "value_2", "value_3", "value_4"],
    ]
    assert raw_csv_content == expected_content


def test_get_content_from_stream_to_dict(csv_stream: str):
    """Tests read CSV stream into a dict."""
    # GIVEN a string in CSV format

    # WHEN reading the CSV content in string
    raw_csv_content: list[list[str]] = read_csv_stream(read_to_dict=True, stream=csv_stream)

    # Then assert a list is returned and that the first element is a dict
    assert isinstance(raw_csv_content, list)
    assert isinstance(raw_csv_content[0], dict)
