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

#### 3. return_book_test.py
**Function Tested**: `return_book_by_patron`
**Total Test Cases**: 8
**Test Cases**:
- `test_return_book_valid_input()` - Positive test with valid book return
- `test_return_book_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_return_book_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_return_book_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_return_book_not_found()` - Invalid book ID handling
- `test_return_book_not_borrowed_by_patron()` - Book not borrowed by patron validation
- `test_return_book_already_returned()` - Already returned book handling
- `test_return_book_patron_id_empty()` - Empty patron ID validation

#### 4. calculate_late_fee_test.py
**Function Tested**: `calculate_late_fee_for_book`
**Total Test Cases**: 10
**Test Cases**:
- `test_calculate_late_fee_no_overdue()` - No late fee for on-time returns
- `test_calculate_late_fee_first_week_overdue()` - Fee calculation for first week overdue ($0.50/day)
- `test_calculate_late_fee_after_first_week()` - Mixed rate calculation (7 days at $0.50 + additional at $1.00)
- `test_calculate_late_fee_maximum_cap()` - Maximum fee cap validation ($15.00)
- `test_calculate_late_fee_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_calculate_late_fee_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_calculate_late_fee_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_calculate_late_fee_book_not_found()` - Invalid book ID handling
- `test_calculate_late_fee_book_not_borrowed()` - Book not borrowed by patron validation
- `test_calculate_late_fee_patron_id_empty()` - Empty patron ID validation

#### 5. search_books_test.py
**Function Tested**: `search_books_in_catalog`
**Total Test Cases**: 10
**Test Cases**:
- `test_search_books_by_title_valid()` - Valid title search functionality
- `test_search_books_by_author_valid()` - Valid author search functionality
- `test_search_books_by_isbn_valid()` - Valid ISBN search functionality
- `test_search_books_empty_search_term()` - Empty search term handling
- `test_search_books_no_results()` - No matching results handling
- `test_search_books_case_insensitive()` - Case insensitive search validation
- `test_search_books_partial_match()` - Partial text matching functionality
- `test_search_books_invalid_search_type()` - Invalid search type handling
- `test_search_books_whitespace_search_term()` - Whitespace-only search term handling
- `test_search_books_special_characters()` - Special characters in search terms

#### 6. get_patron_status_test.py
**Function Tested**: `get_patron_status_report`
**Total Test Cases**: 10
**Test Cases**:
- `test_get_patron_status_valid_with_borrowed_books()` - Patron status with active borrowed books
- `test_get_patron_status_valid_no_borrowed_books()` - Patron status with no borrowed books
- `test_get_patron_status_with_overdue_books()` - Patron status including overdue book information
- `test_get_patron_status_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_get_patron_status_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_get_patron_status_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_get_patron_status_patron_id_empty()` - Empty patron ID handling
- `test_get_patron_status_multiple_borrowed_books()` - Multiple borrowed books status
- `test_get_patron_status_nonexistent_patron()` - Patron with no borrowing history
- `test_get_patron_status_patron_id_whitespace()` - Whitespace in patron ID handling
