# Moustafa Salem 20442264 Group 4

| Function Name               | Implementation Status | What is Missing |
|-----------------------------|-----------------------|-----------------|
| add_book_to_catalog         | complete              | None            |
| borrow_book_by_patron       | complete              | None            |
| return_book_by_patron       | complete              | None            |
| calculate_late_fee_for_book | complete              | None            |
| search_books_in_catalog     | complete              | None            |
| get_patron_status_report    | complete              | None            |

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
**Total Test Cases**: 9
**Test Cases**:
- `test_return_book_valid_input()` - Confirms availability resets and no-fee messaging for timely returns
- `test_return_book_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_return_book_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_return_book_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_return_book_not_found()` - Invalid book ID handling
- `test_return_book_not_borrowed_by_patron()` - Book not borrowed by patron validation
- `test_return_book_with_isbn_input()` - Verifies ISBN-based returns locate the borrowed copy
- `test_return_book_already_returned()` - Late fee messaging and already-returned handling
- `test_return_book_patron_id_empty()` - Empty patron ID validation

#### 4. calculate_late_fee_test.py
**Function Tested**: `calculate_late_fee_for_book`
**Total Test Cases**: 11
**Test Cases**:
- `test_calculate_late_fee_no_overdue()` - No late fee for on-time returns
- `test_calculate_late_fee_first_week_overdue()` - Fee calculation for first week overdue ($0.50/day)
- `test_calculate_late_fee_after_first_week()` - Mixed rate calculation (7 days at $0.50 + additional at $1.00)
- `test_calculate_late_fee_maximum_cap()` - Maximum fee cap validation ($15.00)
- `test_calculate_late_fee_returned_book()` - Late fee summary after return date is recorded
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
- `test_get_patron_status_valid_no_borrowed_books()` - Patron status after all loans are returned with history recorded
- `test_get_patron_status_with_overdue_books()` - Patron status including overdue book information and accrued fees
- `test_get_patron_status_patron_id_too_short()` - Patron ID validation (less than 6 digits)
- `test_get_patron_status_patron_id_invalid()` - Patron ID format validation (non-numeric)
- `test_get_patron_status_patron_id_too_long()` - Patron ID validation (more than 6 digits)
- `test_get_patron_status_patron_id_empty()` - Empty patron ID handling
- `test_get_patron_status_multiple_borrowed_books()` - Multiple borrowed books status and total fee aggregation
- `test_get_patron_status_nonexistent_patron()` - Patron with no borrowing history
- `test_get_patron_status_patron_id_whitespace()` - Whitespace in patron ID handling

## Implementation Experience
Completing the remaining service layer work is now fully complete. Implementing shared helpers for patron validation and overdue math made it easier to align return processing, late-fee calculation, search, and reporting behaviour while keeping the database interactions consistent. Updating the tests alongside the code surfaced edge cases (like handling returned items in fee summaries) and confirmed the new logic behaves as intended across timely, overdue, and whitespace-heavy inputs.
