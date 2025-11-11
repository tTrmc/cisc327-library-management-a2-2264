import pytest
from datetime import datetime, timedelta

from database import get_book_by_isbn, get_db_connection
from services.library_service import (
    calculate_late_fee_for_book,
    add_book_to_catalog,
    borrow_book_by_patron
)


def _book_id_for_isbn(isbn: str) -> int:
    return get_book_by_isbn(isbn)['id']


def _set_due_date(patron_id: str, book_id: int, days_overdue: int, returned: bool = False) -> None:
    conn = get_db_connection()
    try:
        record = conn.execute(
            '''
            SELECT id FROM borrow_records
            WHERE patron_id = ? AND book_id = ?
            ORDER BY borrow_date DESC
            LIMIT 1
            ''',
            (patron_id, book_id)
        ).fetchone()
        if not record:
            return
        new_due_date = datetime.now() - timedelta(days=days_overdue)
        return_date = datetime.now() if returned else None
        conn.execute(
            'UPDATE borrow_records SET due_date = ?, return_date = ? WHERE id = ?',
            (new_due_date.isoformat(), return_date.isoformat() if return_date else None, record['id'])
        )
        conn.commit()
    finally:
        conn.close()


def test_calculate_late_fee_no_overdue():
    """Test calculating late fee for book returned on time."""
    isbn = "2234500000000"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.0
    assert result['days_overdue'] == 0
    assert "no outstanding late fees" in result['status'].lower()


def test_calculate_late_fee_first_week_overdue():
    """Test calculating late fee for book 3 days overdue (first week rate)."""
    isbn = "2234500000001"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 3)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert result['fee_amount'] == 1.5
    assert result['days_overdue'] == 3
    assert "overdue by 3" in result['status'].lower()


def test_calculate_late_fee_after_first_week():
    """Test calculating late fee for book 10 days overdue (mixed rates)."""
    isbn = "2234500000002"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 10)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert result['fee_amount'] == 6.5
    assert result['days_overdue'] == 10


def test_calculate_late_fee_maximum_cap():
    """Test calculating late fee with maximum cap of $15.00."""
    isbn = "2234500000003"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 40)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert result['fee_amount'] == 15.0
    assert result['days_overdue'] == 40


def test_calculate_late_fee_returned_book():
    """Test calculating late fee after the book has been returned."""
    isbn = "2234500000004"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    borrow_book_by_patron("123456", book_id)
    _set_due_date("123456", book_id, 2, returned=True)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert result['fee_amount'] == 1.0
    assert result['days_overdue'] == 2
    assert "returned" in result['status'].lower()


def test_calculate_late_fee_patron_id_too_short():
    """Test calculating late fee with too short patron ID."""
    result = calculate_late_fee_for_book("12345", 1)

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_calculate_late_fee_patron_id_invalid():
    """Test calculating late fee with invalid patron ID."""
    result = calculate_late_fee_for_book("test", 1)

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_calculate_late_fee_patron_id_too_long():
    """Test calculating late fee with too long patron ID."""
    result = calculate_late_fee_for_book("1234567", 1)

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()


def test_calculate_late_fee_book_not_found():
    """Test calculating late fee for non-existent book."""
    result = calculate_late_fee_for_book("123456", 999)

    assert isinstance(result, dict)
    assert "book not found" in result['status'].lower()


def test_calculate_late_fee_book_not_borrowed():
    """Test calculating late fee for book not borrowed by patron."""
    isbn = "2234500000005"
    add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    book_id = _book_id_for_isbn(isbn)
    result = calculate_late_fee_for_book("123456", book_id)

    assert isinstance(result, dict)
    assert "not borrowed" in result['status'].lower()


def test_calculate_late_fee_patron_id_empty():
    """Test calculating late fee with empty patron ID."""
    result = calculate_late_fee_for_book("", 1)

    assert isinstance(result, dict)
    assert "invalid patron id" in result['status'].lower()
