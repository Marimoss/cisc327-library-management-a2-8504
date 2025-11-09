'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!! ONLY ONE FUNCTION IS EXPECTED TO PASS BECAUSE THE REST ARE INCOMPLETE.

Run this file with venv terminal `python -m pytest tests/r5_test.py` to pytest. 
'''
import pytest
import os
from datetime import datetime, timedelta
from database import init_database, add_sample_data, DATABASE, insert_borrow_record, get_patron_borrowed_books
from services.library_service import (
    calculate_late_fee_for_book,  # The only function required for R5. 
    borrow_book_by_patron
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()

# -------------------------------------------------------------------------

def test_books_due_14_days():
    """Test late fee calculation for a book returned on time (14 days)."""
    borrow_book_by_patron("666666", 2)  # Borrow a book first to return.

    borrow_date = get_patron_borrowed_books("666666")[0]['borrow_date']  # Get the borrow date of the borrowed book.
    due_date = get_patron_borrowed_books("666666")[0]['due_date']
    
    assert (due_date - borrow_date).days == 14  # The due date is 14 days after the borrow date.


def test_invalid_patrons():
    """Test late fee calculation for an invalid patron."""
    fine = calculate_late_fee_for_book("000", 1)  # Invalid patron ID.
    assert fine['status'] == 'No active borrow record found for this patron and book.'

    fine = calculate_late_fee_for_book("", 1)  
    assert fine['status'] == 'No active borrow record found for this patron and book.'

    fine = calculate_late_fee_for_book("ajsdhkajsaksdj", 1)  
    assert fine['status'] == 'No active borrow record found for this patron and book.'


def test_calculate_late_fee_for_book_no_overdue():
    """Test late fee calculation for a book returned on time."""
    # Simulate an on-time return scenario.
    borrowed = datetime.now() - timedelta(days=10)  # Borrowed 10 days ago.
    due_date = borrowed + timedelta(days=14)  # Due 14 days after borrowing.
    insert_borrow_record("666666", 2, borrowed, due_date)  # Borrowed a book that is not yet due.
    
    fine = calculate_late_fee_for_book("666666", 2)

    assert isinstance(fine['fee_amount'], float)  
    assert fine['fee_amount'] == 0  # Fine amount is 0, days overdue is 0.
    assert fine['days_overdue'] == 0  


def test_calculate_late_fee_for_book_1_day():
    """Test late fee calculation."""
    # Simulate a late return scenario.
    borrowed = datetime.now() - timedelta(days=15)  # Borrowed 15 days ago.
    due_date = borrowed + timedelta(days=14)  # Due 14 days after borrowing.
    insert_borrow_record("666666", 1, borrowed, due_date)  # Borrowed a book that was already due today.
    
    fine = calculate_late_fee_for_book("666666", 1)

    assert isinstance(fine['fee_amount'], float)  # Assert that a late fee amount was calculated and displayed. 
    assert fine['fee_amount'] == 0.50  # $0.50/day. 
    assert fine['days_overdue'] == 1 


def test_calculate_late_fee_for_book_7_days():
    """Test late fee calculation for the first 7 days."""
    # Simulate a late return scenario.
    borrowed = datetime.now() - timedelta(days=21) 
    due_date = borrowed + timedelta(days=14) 
    insert_borrow_record("666666", 2, borrowed, due_date)  # Already due 7 days ago.
    
    fine = calculate_late_fee_for_book("666666", 2)

    assert isinstance(fine['fee_amount'], float)
    assert fine['fee_amount'] == 3.50  # 7 x $0.50/day.
    assert fine['days_overdue'] == 7


def test_calculate_late_fee_for_book_10_days():
    """Test late fee calculation for more than 7 days."""
    # Simulate a late return scenario.
    borrowed = datetime.now() - timedelta(days=24) 
    due_date = borrowed + timedelta(days=14) 
    insert_borrow_record("666666", 1, borrowed, due_date)  # Already due 10 days ago.
    
    fine = calculate_late_fee_for_book("666666", 1)

    assert isinstance(fine['fee_amount'], float)
    assert fine['fee_amount'] == 6.50  # (7 x $0.50) + (3 x $1.00).
    assert fine['days_overdue'] == 10


def test_calculate_late_fee_for_book_maximum():
    """Test late fee calculation for maximum cap."""
    # Maximum is $15.00 per book. 
    borrowed = datetime.now() - timedelta(days=33)  # (7 x $0.50) + (11 x $1.00) = $14.50 but capped at $15.00. 
    due_date = borrowed + timedelta(days=14) 
    insert_borrow_record("666666", 2, borrowed, due_date) 
    
    fine = calculate_late_fee_for_book("666666", 2)  # Due 19 days ago, (7 x $0.50) + (12 x $1.00) = $15.50 but capped at $15.00.

    assert isinstance(fine['fee_amount'], float)
    assert fine['fee_amount'] == 15.00  # Maximum cap reached.
    assert fine['days_overdue'] == 19


def test_calculate_late_fee_for_book_JSON_response():
    """Test that the response is a dictionary which can be serialized into JSON."""
    result = calculate_late_fee_for_book("666666", 1)
    assert isinstance(result, dict)


def test_calculate_late_fee_for_book_no_borrow_record():
    """Test late fee calculation when there is no borrow record."""
    fine = calculate_late_fee_for_book("999999", 1)  # Patron has not borrowed this book.
    assert fine['status'] == 'No active borrow record found for this patron and book.'
    assert fine['fee_amount'] == 0
    assert fine['days_overdue'] == 0

