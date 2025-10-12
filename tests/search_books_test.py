import pytest
from library_service import (
    search_books_in_catalog,
    add_book_to_catalog
)


def test_search_books_by_title_valid():
    """Test searching books by title with valid input."""
    add_book_to_catalog("The Great Gatsby", "F. Scott Fitzgerald", "3334500000000", 5)
    add_book_to_catalog("To Kill a Mockingbird", "Harper Lee", "3334500000001", 3)
    result = search_books_in_catalog("Great Gatsby", "title")

    assert isinstance(result, list)
    titles = [book['title'] for book in result]
    assert "The Great Gatsby" in titles


def test_search_books_by_author_valid():
    """Test searching books by author with valid input."""
    add_book_to_catalog("Test Book", "Test Author", "3334500000002", 5)
    add_book_to_catalog("Another Book", "Different Author", "3334500000003", 2)
    result = search_books_in_catalog("Test Author", "author")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['author'] == "Test Author"


def test_search_books_by_isbn_valid():
    """Test searching books by ISBN with valid input."""
    add_book_to_catalog("Test Book", "Test Author", "3334500000004", 5)
    result = search_books_in_catalog("3334500000004", "isbn")

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['isbn'] == "3334500000004"


def test_search_books_empty_search_term():
    """Test searching books with empty search term."""
    result = search_books_in_catalog("", "title")

    assert isinstance(result, list)
    assert result == []


def test_search_books_no_results():
    """Test searching books with no matching results."""
    add_book_to_catalog("Test Book", "Test Author", "3334500000005", 5)
    result = search_books_in_catalog("Nonexistent Book", "title")

    assert isinstance(result, list)
    assert len(result) == 0


def test_search_books_case_insensitive():
    """Test searching books with case insensitive search."""
    add_book_to_catalog("The Great Gatsby", "F. Scott Fitzgerald", "3334500000006", 5)
    result = search_books_in_catalog("great gatsby", "title")

    assert isinstance(result, list)
    assert any(book['title'] == "The Great Gatsby" for book in result)


def test_search_books_partial_match():
    """Test searching books with partial match."""
    add_book_to_catalog("The Great Gatsby", "F. Scott Fitzgerald", "3334500000007", 5)
    result = search_books_in_catalog("Great", "title")

    assert isinstance(result, list)
    assert any("Great" in book['title'] for book in result)


def test_search_books_invalid_search_type():
    """Test searching books with invalid search type."""
    add_book_to_catalog("Test Book", "Test Author", "3334500000008", 5)
    result = search_books_in_catalog("Test", "invalid_type")

    assert isinstance(result, list)
    assert result == []


def test_search_books_whitespace_search_term():
    """Test searching books with whitespace only search term."""
    result = search_books_in_catalog("   ", "title")

    assert isinstance(result, list)
    assert result == []


def test_search_books_special_characters():
    """Test searching books with special characters in search term."""
    add_book_to_catalog("Test Book: A Story", "Test Author", "3334500000009", 5)
    result = search_books_in_catalog("Test Book:", "title")

    assert isinstance(result, list)
    assert any(book['title'] == "Test Book: A Story" for book in result)
