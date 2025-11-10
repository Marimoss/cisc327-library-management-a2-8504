'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!!

Run this file with venv terminal `python -m pytest tests/r1_test.py` to pytest. 
'''
import pytest
import os
from database import init_database, add_sample_data, DATABASE
from services.library_service import (
    add_book_to_catalog  # The only function required for R1. 
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()

# -------------------------------------------------------------------------

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234123412341", 4)
    
    assert success == True
    assert "successfully added" in message.lower()  # Display success/error message depending on output. 


def test_add_book_valid_input2():
    """Test adding a book with valid input but straining the checks. Title length 200 characters, Author length 100 characters."""
    success, message = add_book_to_catalog("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "eeeeeeeeeeeee" \
    "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "9876543210987", 9999)
    
    assert success == True
    assert "successfully added" in message.lower()


def test_add_book_no_title():
    """Test adding a book with no title."""
    success, message = add_book_to_catalog(" ", "Emily Cheng", "7777777777777", 5)
    
    assert success == False  
    assert message == "Title is required."


def test_add_book_long_title():
    """Test adding a book with a title over 200 characters."""
    success, message = add_book_to_catalog("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Emily Cheng", "8888888888888", 5)
    
    assert success == False  
    assert message == "Title must be less than 200 characters."


def test_add_book_no_author():
    """Test adding a book with no author."""
    success, message = add_book_to_catalog("One Piece", "", "9999999999999", 5)
    
    assert success == False  
    assert message == "Author is required."


def test_add_book_long_author():
    """Test adding a book with an author over 100 characters."""
    success, message = add_book_to_catalog("garbage", "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" \
    "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "0000000000000", 5)
    
    assert success == False  
    assert message == "Author must be less than 100 characters."


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "999999", 5)
    
    assert success == False
    assert message == "ISBN must be exactly 13 digits."


def test_add_book_negative_copies():
    """Test adding a book with copies that are NEGATIVE numbers."""
    success, message = add_book_to_catalog("Hello", "Carol Cheng", "1111111111111", -5)
    
    assert success == False
    assert message == "Total copies must be a positive integer."


def test_add_book_existing_ISBN():
    """Test adding a book with an existing ISBN from the first test."""
    success, message = add_book_to_catalog("New Hello", "Carol Cheng", "1234123412341", 5)
    
    assert success == False
    assert message == "A book with this ISBN already exists."


def test_add_book_negative_ISBN():
    """Test adding a book with a negative ISBN that is still 13 digits."""
    success, message = add_book_to_catalog("Bro...", "Person", "-123423412341", 5)
    
    assert success == False  # A2: Fixed a BUG discovered in the code. 
    assert 'ISBN must be exactly 13 number-only digits.' in message


def test_add_book_invalid_isbn_13_spaces():
    """Test adding a book with ISBN of length 13 but it is all spaces."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "             ", 5)
    
    assert success == False  # A2: Fixed a BUG discovered in the code. 
    assert 'ISBN must be exactly 13 number-only digits.' in message


# ASSIGNMENT 3 TEST. -------------------------------------------------------
def test_add_book_to_catalog_DB_error(mocker):
    '''Test adding a book when database error occurs, simulated by stubbing the database connection to raise an exception.'''
    # STUB database functions. 
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)  # No existing book with the same ISBN. 
    mocker.patch("services.library_service.insert_book", return_value=False)  # Force DB insertion failure.

    success, msg = add_book_to_catalog("DB Error Book", "Jackie Chan", "0000000000000", 1)  # Call tested function. 

    assert success is False  # Function failed as expected.
    assert msg == "Database error occurred while adding the book."

