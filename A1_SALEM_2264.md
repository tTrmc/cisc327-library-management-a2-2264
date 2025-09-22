# Moustafa Salem 20442264 Group 4

| Function Name               | Implementation Status | What is Missing                                                                                                                     |
|-----------------------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| add_book_to_catalog         | complete              | None                                                                                                                                |
| borrow_book_by_patron       | complete              | None                                                                                                                                |
| return_book_by_patron       | partial               | Only returns error message, needs patron/book validation, borrow record verification, availability update, and late fee calculation |
| calculate_late_fee_for_book | partial               | Complete fee calculation logic, overdue date checking, tiered fee structure, and proper return format                               |
| search_books_in_catalog     | partial               | Only returns empty list, needs search term validation, database query logic, and filtering by search type (title/author/isbn)       |
| get_patron_status_report    | partial               | Only returns empty dict, needs borrowed books retrieval, due date calculation, late fees summation, and borrowing history           |

## Unit Test Scripts Summary

### Test Config
- Isolated test database (`test_library.db`) created and cleaned up automatically for each test
- `conftest.py` - Contains pytest fixtures for test database setup

### Test Files

#### 1. add_book_test.py
**Function Tested**: `add_book_to_catalog`
**Total Test Cases**: 9
**Test Cases**:
- `test_add_book_valid_input()` - Positive test with valid book data
- `test_add_book_invalid_isbn_too_short()` - ISBN validation (too few digits)
- `test_add_book_invalid_isbn_too_long()` - ISBN validation (too many digits)
- `test_add_book_no_title()` - Title requirement validation
- `test_add_book_no_author()` - Author requirement validation
- `test_add_book_title_too_long()` - Title length validation (>200 characters)
- `test_add_book_author_too_long()` - Author length validation (>100 characters)
- `test_add_book_total_copies_invalid()` - Negative copies validation
- `test_add_book_duplicate()` - Duplicate ISBN prevention

#### 2. borrow_book_test.py
**Function Tested**: `borrow_book_by_patron`
**Total Test Cases**: 7
**Test Cases**:
- `test_borrow_book_valid_input()` - Positive test with valid patron ID and available book
- `test_borrow_book_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_borrow_book_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_borrow_book_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_borrow_book_not_found()` - Invalid book ID handling
- `test_borrow_book_not_available()` - Unavailable book handling
- `test_borrow_book_patron_borrow_count()` - Maximum borrowing limit validation
