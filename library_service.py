"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from database import (
    get_book_by_id,
    get_book_by_isbn,
    get_patron_borrow_count,
    insert_book,
    insert_borrow_record,
    update_book_availability,
    update_borrow_record_return_date,
    get_all_books,
    get_db_connection,
    get_patron_borrowed_books
)

DATE_OUTPUT_FORMAT = "%Y-%m-%d"


def _normalize_patron_id(patron_id: Optional[str]) -> str:
    if patron_id is None:
        return ""
    return patron_id.strip()


def _validate_patron_id(patron_id: Optional[str]) -> Tuple[bool, str, str]:
    normalized = _normalize_patron_id(patron_id)
    if not normalized or not normalized.isdigit() or len(normalized) != 6:
        return False, normalized, "Invalid patron ID. Must be exactly 6 digits."
    return True, normalized, ""


def _safe_datetime_from_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _format_date(value: Optional[datetime]) -> Optional[str]:
    if not value:
        return None
    return value.strftime(DATE_OUTPUT_FORMAT)


def _calculate_overdue_metrics(due_date: datetime, reference: Optional[datetime] = None) -> Tuple[int, float]:
    reference_point = reference or datetime.now()
    if reference_point <= due_date:
        return 0, 0.0
    days_overdue = (reference_point.date() - due_date.date()).days
    first_seven = min(days_overdue, 7)
    additional = max(days_overdue - 7, 0)
    fee = min(first_seven * 0.50 + additional * 1.00, 15.00)
    return days_overdue, round(fee, 2)


def _get_active_borrow_record(patron_id: str, book_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT br.*, b.title, b.author
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.patron_id = ? AND br.book_id = ? AND br.return_date IS NULL
            ORDER BY br.borrow_date DESC
            LIMIT 1
            """,
            (patron_id, book_id)
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def _get_latest_borrow_record(patron_id: str, book_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT br.*, b.title, b.author
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.patron_id = ? AND br.book_id = ?
            ORDER BY br.borrow_date DESC
            LIMIT 1
            """,
            (patron_id, book_id)
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def _get_patron_borrow_history(patron_id: str) -> List[Dict]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT br.*, b.title, b.author
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.patron_id = ?
            ORDER BY br.borrow_date DESC
            """,
            (patron_id,)
        ).fetchall()
    finally:
        conn.close()

    history: List[Dict] = []
    for row in rows:
        borrow_date = datetime.fromisoformat(row["borrow_date"])
        due_date = datetime.fromisoformat(row["due_date"])
        return_date = _safe_datetime_from_iso(row["return_date"])
        history.append({
            "book_id": row["book_id"],
            "title": row["title"],
            "author": row["author"],
            "borrow_date": _format_date(borrow_date),
            "due_date": _format_date(due_date),
            "return_date": _format_date(return_date)
        })
    return history


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."


def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    normalized_patron_id = _normalize_patron_id(patron_id)
    # Validate patron ID
    if not normalized_patron_id or not normalized_patron_id.isdigit() or len(normalized_patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(normalized_patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(normalized_patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    Implements R4: Book Return Processing
    """
    is_valid, normalized_patron_id, error_message = _validate_patron_id(patron_id)
    if not is_valid:
        return False, error_message

    try:
        book_id_int = int(book_id)
    except (TypeError, ValueError):
        return False, "Invalid book ID."

    if book_id_int <= 0:
        return False, "Invalid book ID."

    book = get_book_by_id(book_id_int)
    if not book:
        return False, "Book not found."

    active_record = _get_active_borrow_record(normalized_patron_id, book_id_int)
    if not active_record:
        latest_record = _get_latest_borrow_record(normalized_patron_id, book_id_int)
        if latest_record and latest_record.get("return_date"):
            return False, "This book has already been returned."
        return False, "This book is not borrowed by this patron."

    if book['available_copies'] >= book['total_copies']:
        return False, "Book inventory data is inconsistent; all copies are already available."

    due_date = datetime.fromisoformat(active_record['due_date'])
    now = datetime.now()
    _, fee_amount = _calculate_overdue_metrics(due_date, now)

    if not update_borrow_record_return_date(normalized_patron_id, book_id_int, now):
        return False, "Database error occurred while updating borrow record."

    if not update_book_availability(book_id_int, 1):
        return False, "Database error occurred while updating book availability."

    if fee_amount > 0:
        message = f'Book "{book["title"]}" successfully returned. Late fee due: ${fee_amount:.2f}.'
    else:
        message = f'Book "{book["title"]}" successfully returned. No late fees.'

    return True, message


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    Implements R5: Late Fee Calculation API
    """
    is_valid, normalized_patron_id, error_message = _validate_patron_id(patron_id)
    if not is_valid:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': error_message}

    try:
        book_id_int = int(book_id)
    except (TypeError, ValueError):
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': "Invalid book ID."}

    if book_id_int <= 0:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': "Invalid book ID."}

    book = get_book_by_id(book_id_int)
    if not book:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': "Book not found."}

    active_record = _get_active_borrow_record(normalized_patron_id, book_id_int)
    record = active_record or _get_latest_borrow_record(normalized_patron_id, book_id_int)

    if not record:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': "Book is not borrowed by this patron."}

    due_date = datetime.fromisoformat(record['due_date'])
    return_date = _safe_datetime_from_iso(record.get('return_date'))

    reference_point = return_date if return_date and not active_record else None
    days_overdue, fee_amount = _calculate_overdue_metrics(due_date, reference_point)

    if active_record:
        status = "No outstanding late fees." if days_overdue == 0 else f"Book overdue by {days_overdue} day(s)."
    else:
        if return_date:
            if days_overdue == 0:
                status = f"Book returned on {_format_date(return_date)}. No outstanding late fees."
            else:
                status = f"Book was returned on {_format_date(return_date)} with {days_overdue} day(s) overdue."
        else:
            status = "Book is not borrowed by this patron."

    return {
        'fee_amount': fee_amount,
        'days_overdue': days_overdue,
        'status': status,
        'due_date': _format_date(due_date),
        'return_date': _format_date(return_date)
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    Implements R6: Book Search Functionality
    """
    if not isinstance(search_type, str):
        return []

    search_type_normalized = search_type.strip().lower()
    if search_type_normalized not in {"title", "author", "isbn"}:
        return []

    if not isinstance(search_term, str):
        return []

    term = search_term.strip()
    if not term:
        return []

    conn = get_db_connection()
    try:
        if search_type_normalized == "title":
            rows = conn.execute(
                "SELECT * FROM books WHERE LOWER(title) LIKE ? ORDER BY title",
                (f"%{term.lower()}%",)
            ).fetchall()
        elif search_type_normalized == "author":
            rows = conn.execute(
                "SELECT * FROM books WHERE LOWER(author) LIKE ? ORDER BY title",
                (f"%{term.lower()}%",)
            ).fetchall()
        else:
            normalized_isbn = term.replace("-", "")
            rows = conn.execute(
                "SELECT * FROM books WHERE isbn = ?",
                (normalized_isbn,)
            ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    Implements R7: Patron Status Report
    """
    is_valid, normalized_patron_id, error_message = _validate_patron_id(patron_id)
    if not is_valid:
        return {
            'patron_id': normalized_patron_id,
            'status': error_message,
            'borrowed_books': [],
            'total_borrowed': 0,
            'total_late_fees': 0.0,
            'history': []
        }

    borrowed_books = get_patron_borrowed_books(normalized_patron_id)
    now = datetime.now()
    borrowed_summaries: List[Dict] = []
    total_late_fees = 0.0

    for book in borrowed_books:
        due_date = book['due_date'] if isinstance(book['due_date'], datetime) else datetime.fromisoformat(book['due_date'])
        borrow_date = book['borrow_date'] if isinstance(book['borrow_date'], datetime) else datetime.fromisoformat(book['borrow_date'])
        days_overdue, fee_amount = _calculate_overdue_metrics(due_date, now)
        borrowed_summaries.append({
            'book_id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'borrow_date': _format_date(borrow_date),
            'due_date': _format_date(due_date),
            'days_overdue': days_overdue,
            'late_fee': fee_amount
        })
        total_late_fees += fee_amount

    history = _get_patron_borrow_history(normalized_patron_id)

    return {
        'patron_id': normalized_patron_id,
        'status': 'success',
        'borrowed_books': borrowed_summaries,
        'total_borrowed': len(borrowed_summaries),
        'total_late_fees': round(total_late_fees, 2),
        'history': history
    }
