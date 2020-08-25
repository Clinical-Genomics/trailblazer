"""Test all aspects of the get command"""


def test_get(invoke_cli):
    """Test get with a argument that should yield no results"""
    # GIVEN the cli
    # WHEN running get with a comment
    result = invoke_cli(["get", "-c", "dummy-comment"])
    # THEN all analyses containing that comment should be listed
    assert not result.output
