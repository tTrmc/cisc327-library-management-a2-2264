import pytest
from services.library_service import (
    borrow_book_by_patron,
    add_book_to_catalog
)

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    success, message = borrow_book_by_patron("123456", 1)

    assert success == True
    assert "Successfully borrowed" in message

def test_borrow_book_patron_id_too_short():
    """Test borrowing a book with too short patron ID."""

    success, message = borrow_book_by_patron("12345", 1)

    assert success == False
    assert "Invalid patron ID." in message

def test_borrow_book_patron_id_invalid():
    """Test borrowing a book with invalid patron ID."""
    success, message = borrow_book_by_patron("test", 1)

    assert success == False
    assert "Invalid patron ID." in message

def test_borrow_book_patron_id_too_long():
    """Test borrowing a book with too long patron ID."""
    success, message = borrow_book_by_patron("1234567", 1)

    assert success == False
    assert "Invalid patron ID." in message

def test_borrow_book_not_found():
    """Test borrowing a book with invalid book ID"""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    success, message = borrow_book_by_patron("123456", 123)

    assert success == False
    assert "Book not found." in message

def test_borrow_book_not_available():
    """Test borrowing a book not available."""

    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 1)
    borrow_book_by_patron("123456", 1)
    success, message = borrow_book_by_patron("123456", 1)

    assert success == False
    assert "not available." in message

def test_borrow_book_patron_borrow_count():
    """Test borrowing a book with max patron book borrow count."""

    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 10)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    borrow_book_by_patron("123456", 1)
    success, message = borrow_book_by_patron("123456", 1)


    assert "maximum borrowing" in message
    assert success == False