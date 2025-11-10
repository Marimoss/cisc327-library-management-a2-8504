'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!! THIS FILE IS EXPECTED TO ONLY PASS ONE TEST AS THE FUNCTION IS NOT IMPLEMENTED YET.

Run this file with venv terminal `python -m pytest tests/r4_test.py` to pytest. 
'''
import pytest
import os
from database import init_database, add_sample_data, DATABASE, insert_borrow_record
from services.library_service import (
    return_book_by_patron,  # The only function required for R4.
    borrow_book_by_patron,  # To test returning, we need to borrow first. 
    add_book_to_catalog, 
    calculate_late_fee_for_book  # To test fine calculation for late return.
)
from datetime import datetime, timedelta  # To simulate late return.

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()
    success, message = borrow_book_by_patron("666666", 1)  # Borrow a book first to return.

# -------------------------------------------------------------------------

def test_return_book_by_patron_invalid_book():
    """Test if function accepts correct patron and book ID form parameters."""
    success, message = return_book_by_patron("666666", 999)  # Invalid book ID. 
    assert success == False
    assert "No active borrow record found for this patron and book with id=" in message


def test_return_book_by_patron_negative_book():
    success, message = return_book_by_patron("666666", -1)  # Negative book ID.
    assert success == False
    assert "No active borrow record found for this patron and book with id=" in message


def test_return_book_by_patron_invalid_patron():
    success, message = return_book_by_patron("12345", 1)  # Invalid patron ID.
    assert success == False
    assert message == "Error, no active borrow record found for this patron."


def test_return_book_by_patron_negative_patron():
    success, message = return_book_by_patron("-12345", 1)  # Negative patron ID.
    assert success == False
    assert message == "Error, no active borrow record found for this patron."


def test_return_book_by_patron_not_borrowed():
    """Test returning a valid book that was not borrowed."""
    success, message = return_book_by_patron("666666", 2)  # Book ID 2 was never borrowed by patron 666666 in this test.
    assert success == False
    assert "No active borrow record found for this patron and book with id=2" in message


def test_return_book_by_patron_valid():
    """Test returning a book with valid input."""
    add_book_to_catalog("Detective Chinatown", "Peak Director", "8888888888888", 100)  # Add new books to borrow.
    borrow_book_by_patron("666666", 4)  # Borrow a book first to return.

    success, message = return_book_by_patron("666666", 4)  # Function accepts patron ID and book ID as form parameters.
    
    # Should pass and be able to return the book as it was borrowed just now.
    assert success == True
    assert message == "Book with id=4 returned successfully. No late fees."


def test_calculate_fine_for_late_return():
    """ Test fine calculation for late return."""
    # Simulate a late return scenario.
    days_ago = datetime.now() - timedelta(days=7)
    insert_borrow_record("666666", 1, days_ago, days_ago)  # Borrowed a book that was due 7 days ago.
    
    fine = calculate_late_fee_for_book("666666", 1)
    
    assert isinstance(fine['fee_amount'], float)  # Assert that a late fee amount was calculated and displayed. 
    assert fine['fee_amount'] > 0  # Assert that the fine amount is greater than 0.


def test_return_book_by_patron_late():
    """Test returning a book that is late and results in a fine."""
    # Simulate a late return scenario.
    days_ago = datetime.now() - timedelta(days=10)
    insert_borrow_record("777777", 1, days_ago, days_ago)  # Borrowed a book that was due 10 days ago.
    success, message = return_book_by_patron("777777", 1)  # Return the book.
    
    assert success == True
    assert message == 'Book with id=1 successfully returned. Late fee $6.50 for being 10 days overdue.'


# ASSIGNMENT 3 TESTS. -------------------------------------------------------
def test_return_book_by_patron_return_DB_error(mocker): 
    '''Test returning a book with a database error that occurred while updating the book return date. Uses stubs for database functions.'''
    # STUB database functions, patron had a borrowed book. 
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id": 1, "title": "Mock Book"}]) 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0, "days_overdue": 0})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=False)  # Force DB update return date failure.

    success, msg = return_book_by_patron("888888", 1)

    assert success is False  # Function failed as expected. 
    assert msg == "Database error occurred while updating book return date."


def test_return_book_by_patron_availablility_DB_error(mocker):
    '''Test returning a book with a database error that occurred while updating the book availability. Uses stubs for database functions.'''
    # STUB database functions, patron had a borrowed book and return date was updated. 
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[{"book_id": 1, "title": "Mock Book"}]) 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0, "days_overdue": 0})
    mocker.patch("services.library_service.update_borrow_record_return_date", return_value=True)

    mocker.patch("services.library_service.update_book_availability", return_value=False)  # Force DB update book availability failure.

    success, msg = return_book_by_patron("888888", 1)

    assert success is False  # Function failed as expected. 
    assert msg == "Database error occurred while updating book availability."
