import pytest
from services.library_service import add_book_to_catalog


def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog(
        "Test Book", "Test Author", "1234567890123", 5
    )

    assert success == True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)

    assert success == False
    assert "13 digits" in message


# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.


def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog(
        "Test Book", "Test Author", "1234567890123456789", 5
    )

    assert success == False
    assert "13 digits" in message


def test_add_book_no_title():
    """Test adding a book with no title."""

    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)

    assert success == False
    assert "Title is required." in message


def test_add_book_no_author():
    """Test adding a book with no author."""

    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    assert success == False
    assert "Author is required." in message


def test_add_book_title_too_long():
    """Test adding a book with title too long."""

    success, message = add_book_to_catalog(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi"
        " volutpat risus non suscipit aliquam. Praesent lectus ante, rhoncus "
        "a mauris vitae, fermentum consequat tortor. Quisque fermentum ultrices "
        "lectus sit amet venenatis. Nunc maximus id ex quis vulputate. Nullam "
        "rhoncus interdum sodales. Donec quis diam eu libero pharetra laoreet in "
        "ac orci. Vivamus convallis ligula scelerisque convallis porttitor. "
        "Mauris ac posuere massa. Ut luctus eget eros ut lacinia. Phasellus "
        "vestibulum dui libero, ac feugiat est dapibus vitae.",
        "Test Author",
        "1234567890123",
        5,
    )

    assert success == False
    assert "Title must be less than 200 characters." in message


def test_add_book_author_too_long():
    """Test adding a book with Author too long."""

    success, message = add_book_to_catalog(
        "Test Book",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi"
        " volutpat risus non suscipit aliquam. Praesent lectus ante, rhoncus "
        "a mauris vitae, fermentum consequat tortor. Quisque fermentum ultrices "
        "lectus sit amet venenatis. Nunc maximus id ex quis vulputate. Nullam "
        "rhoncus interdum sodales. Donec quis diam eu libero pharetra laoreet in "
        "ac orci. Vivamus convallis ligula scelerisque convallis porttitor. "
        "Mauris ac posuere massa. Ut luctus eget eros ut lacinia. Phasellus "
        "vestibulum dui libero, ac feugiat est dapibus vitae.",
        "1234567890123",
        5,
    )

    assert success == False
    assert "Author must be less than 100 characters." in message


def test_add_book_total_copies_invalid():
    """Test adding a book with total copies invalid."""

    success, message = add_book_to_catalog(
        "Test Book", "Test Author", "1234567890123", -5
    )

    assert success == False
    assert "Total copies must be a positive integer." in message


def test_add_book_duplicate():
    """Test adding a book with duplicate book."""

    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    success, message = add_book_to_catalog(
        "Test Book", "Test Author", "1234567890123", 5
    )

    assert success == False
    assert "A book with this ISBN already exists." in message

