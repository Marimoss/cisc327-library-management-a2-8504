'''
Run this file with venv terminal `python -m pytest tests/r2_test.py` to pytest. 
'''
import pytest
import os
from database import init_database, add_sample_data, DATABASE
from database import (
    get_all_books  # The only function of R2. 
)

# MANDATORY: Reset the database before running tests to ensure a clean state with no interference from previous tests!
@pytest.fixture(autouse=True, scope="module")
def reset_database():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_database()
    add_sample_data()

# -------------------------------------------------------------------------

def test_get_all_books():
    """Test Getting all books from the catalog."""
    books = get_all_books() # Call the function to test if it works. 
    
    assert books != None or books != []  # Test if books list returns properly when it is not actually empty.
    assert isinstance(books, list)  # Test if it returns type list of dictionaries.


def test_get_all_books_content():
    """Test the content of the books returned from get_all_books."""
    books = get_all_books()
    
    # Check if each book has the required fields.
    for book in books:
        assert 'id' in book
        assert 'title' in book
        assert 'author' in book
        assert 'isbn' in book
        assert 'total_copies' in book
        assert 'available_copies' in book
        
        # Check types of each field.
        assert isinstance(book['id'], int)
        assert isinstance(book['title'], str)
        assert isinstance(book['author'], str)
        assert isinstance(book['isbn'], str)
        assert isinstance(book['total_copies'], int)
        assert isinstance(book['available_copies'], int)


def test_get_all_books_copy_consistency():
    """Test that available copies never exceed total copies or are negative."""
    books = get_all_books()

    for book in books:
        assert book['available_copies'] <= book['total_copies']
        assert book['total_copies'] >= 0  # Total copies should never be negative.
        assert book['available_copies'] >= 0


def test_get_all_books_empty():
    """Test getting all books when the catalog is empty."""
    # Reset the database to be empty.
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    init_database()
    
    books = get_all_books()
    assert books == []  # Should return an empty list when no books are present.


def test_get_all_books_unique_isbn():
    """Test that no two books share the same ISBN."""
    books = get_all_books()
    isbns = [book['isbn'] for book in books]

    # ISBN must be unique across all books.
    assert len(isbns) == len(set(isbns))


def test_get_all_books_table_integrity():
    """Test that the books table structure is intact."""
    books = get_all_books()
    
    for book in books:
        assert len(book) == 6  # There should be exactly 6 fields in each book dictionary table. 
