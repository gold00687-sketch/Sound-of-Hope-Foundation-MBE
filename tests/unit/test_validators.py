from app.utils.validators import is_valid_phone, is_valid_slug, normalise_email, normalise_phone


def test_valid_phone_numbers() -> None:
    assert is_valid_phone("+256701234567")
    assert is_valid_phone("+1234567890")


def test_invalid_phone_numbers() -> None:
    assert not is_valid_phone("123")
    assert not is_valid_phone("abcdefg")
    assert not is_valid_phone("")


def test_normalise_phone() -> None:
    assert normalise_phone("+256 70 123 4567") == "+256701234567"


def test_normalise_email() -> None:
    assert normalise_email("  Alice@Example.COM  ") == "alice@example.com"


def test_valid_slugs() -> None:
    assert is_valid_slug("my-programme")
    assert is_valid_slug("course-2024")


def test_invalid_slugs() -> None:
    assert not is_valid_slug("My Programme")
    assert not is_valid_slug("-leading-dash")
