'''
IT IS ASSUMED THAT ONLY THE `library_service.py` FILE WILL BE TESTED, ACCORDING TO THE `requirements_specification.md` 
AND `student_instructions.md` FILE!!! 

Run this file with venv terminal `python -m pytest tests/r6_test.py` to pytest. 
'''
import pytest
import os
from database import init_database, add_sample_data, DATABASE
from services.library_service import (
    search_books_in_catalog  # The only function required for R6. 
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()

# -------------------------------------------------------------------------

def test_search_books_in_catalog_invalid():
    """Test searching for a book with valid inputs but does not exist."""
    result = search_books_in_catalog("One Piece", "title")

    assert isinstance(result, list)
    assert len(result) == 0  # No books with title "One Piece" in sample data.


def test_search_books_in_catalog():
    '''Test searching with valid book title and valid term.'''
    result = search_books_in_catalog("1984", "title")  # Default sample book.
    assert len(result) == 1 
    assert result[0]['title'] == "1984"  # Original function returns a list of Dict. 
    assert result[0]['author'] == "George Orwell"
    assert result[0]['isbn'] == "9780451524935"


def test_search_books_in_catalog_partials():
    '''Test searching with valid partial book information and valid term.'''
    partial_result = search_books_in_catalog("19", "title")  # Partial match test for title. 
    assert partial_result[0]['title'] == "1984" 
    assert partial_result[0]['author'] == "George Orwell"
    assert partial_result[0]['isbn'] == "9780451524935"

    partial_result2 = search_books_in_catalog("George", "author")  # Partial match test for author.
    assert partial_result2[0]['title'] == "1984" 
    assert partial_result2[0]['author'] == "George Orwell"
    assert partial_result2[0]['isbn'] == "9780451524935"


def test_search_books_in_catalog_ISBN_exact():
    '''Test searching with valid full ISBN.'''
    result = search_books_in_catalog("9780451524935", "isbn")  # Exact match for ISBN.
    assert result[0]['title'] == "1984" 
    assert result[0]['author'] == "George Orwell"
    assert result[0]['isbn'] == "9780451524935"


def test_search_books_in_catalog_invalid_ISBN():
    '''Test searching with an invalid ISBN.'''
    result = search_books_in_catalog("676767", "isbn")
    assert result == []  # Should return empty list for invalid ISBN or include an error/status message.


def test_search_books_in_catalog_invalid_type():
    '''Test searching with an invalid type not in the dropdown.'''
    result = search_books_in_catalog("Detective Chinatown", "literally peak type")

    assert result == []  # Should return empty list for invalid type or include an error/status message.


def test_search_books_in_catalog_q_empty_term():
    '''Test searching with an empty `q` term (non-existing).'''
    result = search_books_in_catalog("", "title")
    assert len(result) > 0  # Should return all books in the catalog, which will always be more than 0 in this test setup.

    result = search_books_in_catalog("       ", "title")
    assert len(result) > 0


def test_search_books_in_catalog_case_insensitive():
    '''Test searching with different cases in the search term.'''
    result = search_books_in_catalog("tHe gReAt gAtSbY", "title")  # Different casing.
    assert result[0]['title'] == "The Great Gatsby"


def test_search_books_in_catalog_trailing_spaces():
    '''Test searching with leading and trailing spaces in the search term.'''
    result = search_books_in_catalog("   1984   ", "title")  # Leading and trailing spaces.
    assert result[0]['title'] == "1984"
