from trailblazer.store.models import User


def test_user_first_name():
    """Test setting user first name."""
    # GIVEN a user with a name
    user: User = User(name="Paul T. Anderson")

    # WHEN accessing the first name
    first_name = user.first_name

    # THEN it should return the spoken name
    assert first_name == "Paul"
