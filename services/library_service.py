"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from services.payment_service import PaymentGateway  # ASSIGNMENT 3. 

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books,
    get_patron_borrowing_history
)


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management.
    
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
    
    if not isbn or not isbn.isdigit():
        return False, "ISBN must be exactly 13 number-only digits."  # A2: New check for invalid input. 

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
    Implements R3 as per requirements. 
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:  # A2: Modified to check for exactly 5 books limit. 
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implement R4 as per requirements.

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return

    Returns:
        tuple: (success: bool, message: str)
    """
    patron_borrowed = get_patron_borrowed_books(patron_id)  # Returns a list of dictionaries. 
    # Check if no books were borrowed at all, list would be empty. 
    if not patron_borrowed:
        return False, "Error, no active borrow record found for this patron."
    
    # Verify if the specific book was currently borrowed by patron.
    for book in patron_borrowed: 
        if book['book_id'] == book_id:
            late_fees = calculate_late_fee_for_book(patron_id, book_id)  # Returns a dictionary. 
            return_success = update_borrow_record_return_date(patron_id, book_id, datetime.now())  # Book was borrowed, record its return date. 
            if not return_success:
                return False, "Database error occurred while updating book return date."
            
            # Update availabile book copies. 
            update_success = update_book_availability(book_id, 1)
            if not update_success:
                return False, "Database error occurred while updating book availability."
            
            # Calculate late fees owed. Assume user pays late fees of a book after returning it. 
            if late_fees['fee_amount'] > 0:
                return True, f'Book with id={book_id} successfully returned. Late fee ${late_fees["fee_amount"]:.2f} for being {late_fees["days_overdue"]} days overdue.'
            else:
                return True, f"Book with id={book_id} returned successfully. No late fees."

    return False, f"No active borrow record found for this patron and book with id={book_id}."


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book. PATRON CANNOT BORROW MORE THAN 1 COPY OF THE SAME BOOK AT A TIME. 
    Implement R5 as per requirements.
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to check for late fees

    Returns:
        dict: {'fee_amount': float, 'days_overdue': int, 'status': str}
    """
    patron_borrowed = get_patron_borrowed_books(patron_id)
    due_date = None
    fee = 0.00

    for book in patron_borrowed: 
        if book['book_id'] == book_id: 
            if not book['is_overdue']:  # Book is not overdue, no fees. 
                return {
                    'fee_amount': 0.00,
                    'days_overdue': 0,
                    'status': 'Not overdue.'
                }
            due_date = book['due_date']  # Stores due date as datetime object to use outside this loop. 
            break

    # Book was not found in patron's borrow list, therefore not overdue.
    if not due_date:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrow record found for this patron and book.'
        }
    
    days_overdue = (datetime.now() - due_date).days  # Current date - due date. 
    if 0 < days_overdue <= 7:
        fee = days_overdue * 0.50  # First 7 days, $0.50 per day.
    elif days_overdue > 7:
        fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)  # After 7 days, $1.00 per day. 
        
        if fee >= 15.00:
            fee = 15.00  # Maximum fee of $15.00 per book. 

    return {
        'fee_amount': round(fee, 2),
        'days_overdue': days_overdue,
        'status': f'Overdue. Late fee of ${fee:.2f} is currently applied.'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implement R6 as per requirements.

    Args:
        search_term: Term that was searched for, as q
        search_type: "title", "author", or "isbn"

    Returns:
        list: List of matching books results (as dictionaries)
    """
    q = search_term.strip()  # Remove leading and trailing spaces.
    if search_type == "isbn":
        book = get_book_by_isbn(q)  # Exact matching for ISBN. 
        return [book] if book else []  # Return empty if no match. 
     
    all_books = get_all_books()
    if not search_term or not search_term.strip():
        return all_books  # If search term is empty or whitespaces. 
    
    elif search_type == "title":
        books = [book for book in all_books if q.lower() in book['title'].lower()]  # Partial matching, case-insensitive. 
        return books # [] if no matches. 
    
    elif search_type == "author":
        all_books = get_all_books()
        books = [book for book in all_books if q.lower() in book['author'].lower()]  # Partial matching, case-insensitive.  
        return books  
        
    return []  # Search type was invalid.


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implement R7 as per requirements.

    Args:
        patron_id: 6-digit library card ID

    Returns:
        dict: Patron status report with currently borrowed books (list of dict), total late fees owed, number borrowed, and borrowing history (list of dict).
    """ 
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {}  # Invalid patron ID.

    current_borrowed = get_patron_borrowed_books(patron_id)  # Currently borrowed books, including due dates of each. 
    num_borrowed = get_patron_borrow_count(patron_id)  # Number of books currently borrowed.
    borrowing_history = get_patron_borrowing_history(patron_id)  # List of all past (returned) borrow records. 
    
    # Total late fees owed currently. 
    total_fees = 0.00
    for book in current_borrowed:
        if book['is_overdue']:
            late_fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
            total_fees += late_fee_info['fee_amount']

    return {
        'current_borrowed': current_borrowed,
        'total_late_fees': round(total_fees, 2),
        'current_borrowed_count': num_borrowed,
        'borrow_history': borrowing_history
    }


# NEW FUNCTIONs PASTED FOR ASSIGNMENT 3.
def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[bool, str, Optional[str]]:  # type: ignore
    """
    Process payment for late fees using external payment gateway.
    
    NEW FEATURE FOR ASSIGNMENT 3: Demonstrates need for mocking/stubbing
    This function depends on an external payment service that should be mocked in tests.
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book with late fees
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str, transaction_id: Optional[str])
        
    Example for you to mock:
        # In tests, mock the payment gateway:
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", None
    
    # Calculate late fee first
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    # Check if there's a fee to pay
    if not fee_info or 'fee_amount' not in fee_info:
        return False, "Unable to calculate late fees.", None
    
    fee_amount = fee_info.get('fee_amount', 0.0)
    
    if fee_amount <= 0:
        return False, "No late fees to pay for this book.", None
    
    # Get book details for payment description
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", None
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process payment through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN THEIR TESTS!
    try:
        success, transaction_id, message = payment_gateway.process_payment(
            patron_id=patron_id,
            amount=fee_amount,
            description=f"Late fees for '{book['title']}'"
        )
        
        if success:
            return True, f"Payment successful! {message}", transaction_id
        else:
            return False, f"Payment failed: {message}", None
            
    except Exception as e:
        # Handle payment gateway errors
        return False, f"Payment processing error: {str(e)}", None


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[bool, str]: # type: ignore
    """
    Refund a late fee payment (e.g., if book was returned on time but fees were charged in error).
    
    NEW FEATURE FOR ASSIGNMENT 3: Another function requiring mocking
    
    Args:
        transaction_id: Original transaction ID to refund
        amount: Amount to refund
        payment_gateway: Payment gateway instance (injectable for testing)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."
    
    if amount <= 0:
        return False, "Refund amount must be greater than 0."
    
    if amount > 15.00:  # Maximum late fee per book
        return False, "Refund amount exceeds maximum late fee."
    
    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()
    
    # Process refund through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN YOUR TESTS!
    try:
        success, message = payment_gateway.refund_payment(transaction_id, amount)
        
        if success:
            return True, message
        else:
            return False, f"Refund failed: {message}"
            
    except Exception as e:
        return False, f"Refund processing error: {str(e)}"
    