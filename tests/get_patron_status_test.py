import pytest
from datetime import datetime, timedelta

from database import get_book_by_isbn, get_db_connection
from library_service import (
    get_patron_status_report,
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron
)


def _book_id_for_isbn(isbn: str) -> int:
    return get_book_by_isbn(isbn)['id']


def _set_due_date(patron_id: str, book_id: int, days_overdue: int) -> None:
    conn = get_db_connection()
    try:
        record = conn.execute(
            '''
            SELECT id FROM borrow_records
            WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
            ORDER BY borrow_date DESC
            LIMIT 1
            ''',
            (patron_id, book_id)
        ).fetchone()
        if not record:
            return
        new_due_date = datetime.now() - timedelta(days=days_overdue)
        conn.execute(
            'UPDATE borrow_records SET due_date = ? WHERE id = ?',
            (new_due_date.isoformat(), record['id'])
        )
        conn.commit()
    finally:
        conn.close()


def test_get_patron_status_valid_with_borrowed_books():
    """Test getting patron status with borrowed books."""
    isbn = "4434500000000"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    result = get_patron_status_report("123456")

    assert isinstance(result, dict)
    assert result['status'] == 'success'
    assert result['total_borrowed'] == 1
    assert result['borrowed_books'][0]['title'] == "Test Book"
    assert result['total_late_fees'] == 0.0


def test_get_patron_status_valid_no_borrowed_books():
    """Test getting patron status after returning all books."""
    isbn = "4434500000001"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    return_book_by_patron("123456", book_id)
    result = get_patron_status_report("123456")

    assert isinstance(result, dict)
    assert result['status'] == 'success'
    assert result['total_borrowed'] == 0
    assert len(result['history']) == 1
    assert result['history'][0]['return_date'] is not None


def test_get_patron_status_with_overdue_books():
    """Test getting patron status with overdue books."""
    isbn = "4434500000002"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 5)
    result = get_patron_status_report("123456")

    assert isinstance(result, dict)
    assert result['borrowed_books'][0]['days_overdue'] == 5
    assert result['borrowed_books'][0]['late_fee'] == 2.5
    assert result['total_late_fees'] == 2.5


def test_get_patron_status_patron_id_too_short():
    """Test getting patron status with too short patron ID."""
    result = get_patron_status_report("12345")

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_get_patron_status_patron_id_invalid():
    """Test getting patron status with invalid patron ID."""
    result = get_patron_status_report("test")

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_get_patron_status_patron_id_too_long():
    """Test getting patron status with too long patron ID."""
    result = get_patron_status_report("1234567")

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_get_patron_status_patron_id_empty():
    """Test getting patron status with empty patron ID."""
    result = get_patron_status_report("")

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_get_patron_status_multiple_borrowed_books():
    """Test getting patron status with multiple borrowed books."""
    isbn_first = "4434500000003"
    isbn_second = "4434500000004"
    add_book_to_catalog("Test Book 1", "Test Author", isbn_first, 5)
    add_book_to_catalog("Test Book 2", "Test Author", isbn_second, 5)
    first_id = _book_id_for_isbn(isbn_first)
    second_id = _book_id_for_isbn(isbn_second)
    borrow_book_by_patron("123456", first_id)
    borrow_book_by_patron("123456", second_id)
    _set_due_date("123456", second_id, 4)
    result = get_patron_status_report("123456")

    assert isinstance(result, dict)
    assert result['total_borrowed'] == 2
    titles = {book['title'] for book in result['borrowed_books']}
    assert {"Test Book 1", "Test Book 2"} == titles
    assert result['total_late_fees'] == 2.0


def test_get_patron_status_nonexistent_patron():
    """Test getting patron status for patron who never borrowed."""
    result = get_patron_status_report("999999")

    assert isinstance(result, dict)
    assert result['status'] == 'success'
    assert result['total_borrowed'] == 0
    assert result['history'] == []


def test_get_patron_status_patron_id_whitespace():
    """Test getting patron status with whitespace in patron ID."""
    isbn = "4434500000005"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    result = get_patron_status_report("  123456  ")

    assert isinstance(result, dict)
    assert result['patron_id'] == "123456"
    assert result['total_borrowed'] == 1
