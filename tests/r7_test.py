'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!!

Run this file with venv terminal `python -m pytest tests/r7_test.py` to pytest. 
'''
import pytest
import os
from datetime import datetime, timedelta
from database import init_database, add_sample_data, DATABASE, insert_borrow_record
from services.library_service import (
    get_patron_status_report, borrow_book_by_patron, add_book_to_catalog, return_book_by_patron
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()
    add_book_to_catalog("Detective Chinatown", "Peak Director", "8888888888888", 5)  # Add new books to borrow.

# -------------------------------------------------------------------------

def test_get_patron_status_report_invalid():
    """Test that the function returns an empty dictionary."""
    report = get_patron_status_report("")
    assert report == {}  # Can also return an error message depending on implementation.

    report = get_patron_status_report("literally cooked")  # Invalid patron ID
    assert report == {}

    report = get_patron_status_report("-67")  # Invalid patron ID
    assert report == {}

    report = get_patron_status_report("7")  # Invalid patron ID
    assert report == {}


def test_get_patron_status_report_var_types():
    '''Test that the function returns a dictionary with correct keys and value types.'''

    report = get_patron_status_report("666666")
    assert set(report.keys()) == {
        "current_borrowed", "total_late_fees", "current_borrowed_count", "borrow_history"
    }
    assert isinstance(report, dict)  # The result is a dictionary.
    assert isinstance(report["current_borrowed"], list)  # All dictionary keys are made-up for testing.
    assert isinstance(report["borrow_history"], list)
    assert isinstance(report["total_late_fees"], float)
    assert isinstance(report["current_borrowed_count"], int)


def test_get_patron_status_report_valid():
    '''Test that the function returns a dictionary for a clean valid patron ID.'''
    report = get_patron_status_report("676767")  # Assuming "676767" is new.

    assert report['current_borrowed'] == []  # No borrowed books. 
    assert report['total_late_fees'] == 0.0  # No late fees.
    assert report['current_borrowed_count'] == 0  # No currently borrowed books.
    assert report['borrow_history'] == []  # No borrow history.


def test_get_patron_status_report_one():
    '''Test that the function returns a dictionary for a valid patron ID with one borrowed book.'''
    borrow_book_by_patron("777777", 4)  # New patron borrows a single book. 
    report = get_patron_status_report("777777")

    assert len(report['current_borrowed']) == 1  # One currently borrowed book. 
    assert report['current_borrowed'][0]['title'] == "Detective Chinatown"
    assert report['current_borrowed'][0]['due_date'] is not None  # Book has a due date. 
    assert report['total_late_fees'] == 0.0
    assert report['current_borrowed_count'] == 1
    assert report['borrow_history'] == []


def test_get_patron_status_report_returned():
    '''Test that the function returns a dictionary for a valid patron ID with one returned book.'''
    borrow_book_by_patron("888888", 4)  # New patron borrows a single book. 
    return_book_by_patron("888888", 4)
    report = get_patron_status_report("888888")

    assert report['current_borrowed'] == []
    assert report['total_late_fees'] == 0.0
    assert report['current_borrowed_count'] == 0
    assert len(report['borrow_history']) == 1  # Only one book in history. 
    assert report['borrow_history'][0]['title'] == "Detective Chinatown"
    assert report['borrow_history'][0]['return_date'] is not None  # Book has a return date.


def test_get_patron_status_report_many():
    '''Test that the function returns a dictionary for a valid patron ID with many borrowed books and late fees.'''
    add_book_to_catalog("Six Sevennn", "Memes", "9999999999999", 1)  # Create many books and borrow/return records. 
    add_book_to_catalog("Ronaldo Glazing", "Cristiano Ronaldo", "1010101010101", 1)
    add_book_to_catalog("How to Not Die in CISC324", "Hossain", "1111111111111", 1)
    borrow_book_by_patron("999999", 5)
    borrow_book_by_patron("999999", 6)
    return_book_by_patron("999999", 5)  # Return two books on time, no previous book in history. 
    return_book_by_patron("999999", 6)

    # Simulate a late return scenario.
    borrowed = datetime.now() - timedelta(days=21)
    due_date = borrowed + timedelta(days=14) 
    insert_borrow_record("999999", 7, borrowed, due_date)  # Already due 7 days ago.

    report = get_patron_status_report("999999")

    assert len(report['current_borrowed']) == 1  # One currently borrowed book. 
    assert report['current_borrowed'][0]['title'] == "How to Not Die in CISC324"
    assert report['total_late_fees'] == 3.50  # $0.50/day.
    assert report['current_borrowed_count'] == 1
    assert len(report['borrow_history']) == 2
    for book in report['borrow_history']:
        assert book['title'] in ["Detective Chinatown", "Six Sevennn", "Ronaldo Glazing"]  # Titles in history.
        assert book['return_date'] is not None 
