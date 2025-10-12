import pytest
from datetime import datetime, timedelta

from database import get_book_by_isbn, get_book_by_id, get_db_connection
from library_service import (
    return_book_by_patron,
    add_book_to_catalog,
    borrow_book_by_patron
)


def _book_id_for_isbn(isbn: str) -> int:
    return get_book_by_isbn(isbn)['id']


def _set_due_date(patron_id: str, book_id: int, days_overdue: int) -> None:
    conn = get_db_connection()
    new_due_date = datetime.now() - timedelta(days=days_overdue)
    conn.execute(
        '''
        UPDATE borrow_records
        SET due_date = ?
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
        ''',
        (new_due_date.isoformat(), patron_id, book_id)
    )
    conn.commit()
    conn.close()


def test_return_book_valid_input():
    """Test returning a book with valid input and no late fees."""
    isbn = "1234500000000"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    success, message = return_book_by_patron("123456", book_id)

    assert success is True
    assert "successfully returned" in message.lower()
    assert "no late fees" in message.lower()
    book = get_book_by_id(book_id)
    assert book['available_copies'] == book['total_copies']


def test_return_book_patron_id_too_short():
    """Test returning a book with too short patron ID."""
    success, message = return_book_by_patron("12345", 1)

    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_book_patron_id_invalid():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("test", 1)

    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_book_patron_id_too_long():
    """Test returning a book with too long patron ID."""
    success, message = return_book_by_patron("1234567", 1)

    assert success is False
    assert "invalid patron id" in message.lower()


def test_return_book_not_found():
    """Test returning a book with invalid book ID."""
    success, message = return_book_by_patron("123456", 999)

    assert success is False
    assert "book not found" in message.lower()


def test_return_book_not_borrowed_by_patron():
    """Test returning a book not borrowed by the patron."""
    isbn = "1234500000001"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    success, message = return_book_by_patron("123456", book_id)

    assert success is False
    assert "not borrowed" in message.lower()


def test_return_book_with_isbn_input():
    """Test returning a book using the ISBN instead of the numeric ID."""
    isbn = "1234500000003"
    add_book_to_catalog("Return With ISBN", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    success, message = return_book_by_patron("123456", isbn)

    assert success is True
    assert "successfully returned" in message.lower()


def test_return_book_already_returned():
    """Test returning a book that was already returned."""
    isbn = "1234500000002"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 3)
    first_success, first_message = return_book_by_patron("123456", book_id)
    second_success, second_message = return_book_by_patron("123456", book_id)

    assert first_success is True
    assert "late fee due: $1.50" in first_message.lower()
    assert second_success is False
    assert "already" in second_message.lower()


def test_return_book_patron_id_empty():
    """Test returning a book with empty patron ID."""
    success, message = return_book_by_patron("", 1)

    assert success is False
    assert "invalid patron id" in message.lower()
