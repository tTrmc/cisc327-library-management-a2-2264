import pytest
from library_service import (
    return_book_by_patron,
    add_book_to_catalog,
    borrow_book_by_patron
)

def test_return_book_valid_input():
    """Test returning a book with valid input."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    success, message = return_book_by_patron("123456", 1)
    
    assert success == True
    assert "successfully returned" in message.lower()

def test_return_book_patron_id_too_short():
    """Test returning a book with too short patron ID."""
    success, message = return_book_by_patron("12345", 1)
    
    assert success == False
    assert "Invalid patron ID" in message

def test_return_book_patron_id_invalid():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("test", 1)
    
    assert success == False
    assert "Invalid patron ID" in message

def test_return_book_patron_id_too_long():
    """Test returning a book with too long patron ID."""
    success, message = return_book_by_patron("1234567", 1)
    
    assert success == False
    assert "Invalid patron ID" in message

def test_return_book_not_found():
    """Test returning a book with invalid book ID."""
    success, message = return_book_by_patron("123456", 999)
    
    assert success == False
    assert "Book not found" in message

def test_return_book_not_borrowed_by_patron():
    """Test returning a book not borrowed by the patron."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    success, message = return_book_by_patron("123456", 1)
    
    assert success == False
    assert "not borrowed" in message.lower()

def test_return_book_already_returned():
    """Test returning a book that was already returned."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    return_book_by_patron("123456", 1)
    success, message = return_book_by_patron("123456", 1)
    
    assert success == False
    assert "already returned" in message.lower()

def test_return_book_patron_id_empty():
    """Test returning a book with empty patron ID."""
    success, message = return_book_by_patron("", 1)
    
    assert success == False
    assert "Invalid patron ID" in message