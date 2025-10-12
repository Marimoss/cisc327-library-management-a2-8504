'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!!

Run this file with venv terminal `python -m pytest tests/r3_test.py` to pytest. 
'''
import pytest
import os
from database import init_database, add_sample_data, DATABASE
from library_service import (
    borrow_book_by_patron,  # The only function required for R3. 
    add_book_to_catalog # More books needed for testing. 
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
if os.path.exists(DATABASE):
    os.remove(DATABASE)

init_database()
add_sample_data()

# -------------------------------------------------------------------------

def test_borrow_book_by_patron_parameters():
    """Test if the function accepts correct patron ID and book ID parameters, and that the book is available."""
    success, message = borrow_book_by_patron("666666", 1)
    assert success == True
    assert "Successfully borrowed" in message


def test_borrow_book_by_patron_invalid_patron_id():
    """Test borrowing with an invalid patron ID."""
    success, message = borrow_book_by_patron("      ", 1)  # Invalid, empty and not digits.
    assert success == False
    assert message == "Invalid patron ID. Must be exactly 6 digits."

    success, message = borrow_book_by_patron("12345", 1)  # Invalid, not 6 digits.
    assert success == False
    assert message == "Invalid patron ID. Must be exactly 6 digits."

    success, message = borrow_book_by_patron("-12345", 1)  # Invalid, negative number.
    assert success == False
    assert message == "Invalid patron ID. Must be exactly 6 digits."  


def test_borrow_book_by_patron_book_not_found():
    """Test borrowing a book that does not exist or is not available."""
    success, message = borrow_book_by_patron("666666", 3456)  # Invalid book ID.
    assert success == False
    assert message == "Book not found."

    success, message = borrow_book_by_patron("666666", -1)  # Negative book ID.
    assert success == False
    assert message == "Book not found."

    success, message = borrow_book_by_patron("666666", 3)  # All copies of Book ID 3 are taken.
    assert success == False
    assert message == "This book is currently not available."


def test_borrow_book_by_patron_book_available():
    """Test borrowing a book that is available."""
    success, message = borrow_book_by_patron("666666", 1)  # Book ID 1 has available copies.
    assert success == True
    assert "Successfully borrowed" in message


def test_borrow_book_by_patron_max_limit():
    """Test borrowing when the patron reaches maximum borrowing limit. There is an error in the code that previously allowed
    borrowing more than 5 books because of the check `current_borrowed > 5` instead of `current_borrowed >= 5`."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)  # Reset database to ensure a clean state.
    init_database()
    
    add_book_to_catalog("Detective Chinatown", "Peak Director", "8888888888888", 6)  # Add new books to borrow.
    patron_id = "666666"
    for book_id in [1, 1, 1, 1, 1]:  # Borrowing 5 copies until borrow limit is reached.
        success, message = borrow_book_by_patron(patron_id, book_id)
        assert success == True
        assert "Successfully borrowed" in message

    # Now try to borrow a 6th book.
    success, message = borrow_book_by_patron(patron_id, 1)  # A2: Fixed a BUG discovered in the code. 
    assert success == False
    assert message == "You have reached the maximum borrowing limit of 5 books."
