import pytest
from library_service import (
    calculate_late_fee_for_book,
    add_book_to_catalog,
    borrow_book_by_patron
)

def test_calculate_late_fee_no_overdue():
    """Test calculating late fee for book returned on time."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0

def test_calculate_late_fee_first_week_overdue():
    """Test calculating late fee for book 3 days overdue (first week rate)."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    # Should be $0.50 per day for first 7 days

def test_calculate_late_fee_after_first_week():
    """Test calculating late fee for book 10 days overdue (mixed rates)."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert 'fee_amount' in result
    assert 'days_overdue' in result
    # Should be $0.50 * 7 + $1.00 * 3 = $6.50

def test_calculate_late_fee_maximum_cap():
    """Test calculating late fee with maximum cap of $15.00."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    borrow_book_by_patron("123456", 1)
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert result['fee_amount'] <= 15.00
    assert 'days_overdue' in result

def test_calculate_late_fee_patron_id_too_short():
    """Test calculating late fee with too short patron ID."""
    result = calculate_late_fee_for_book("12345", 1)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "Invalid patron ID" in result['status']

def test_calculate_late_fee_patron_id_invalid():
    """Test calculating late fee with invalid patron ID."""
    result = calculate_late_fee_for_book("test", 1)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "Invalid patron ID" in result['status']

def test_calculate_late_fee_patron_id_too_long():
    """Test calculating late fee with too long patron ID."""
    result = calculate_late_fee_for_book("1234567", 1)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "Invalid patron ID" in result['status']

def test_calculate_late_fee_book_not_found():
    """Test calculating late fee for non-existent book."""
    result = calculate_late_fee_for_book("123456", 999)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "Book not found" in result['status']

def test_calculate_late_fee_book_not_borrowed():
    """Test calculating late fee for book not borrowed by patron."""
    add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    result = calculate_late_fee_for_book("123456", 1)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "not borrowed" in result['status'].lower()

def test_calculate_late_fee_patron_id_empty():
    """Test calculating late fee with empty patron ID."""
    result = calculate_late_fee_for_book("", 1)
    
    assert isinstance(result, dict)
    assert 'status' in result
    assert "Invalid patron ID" in result['status']