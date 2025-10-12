<br>

# Emily Cheng, 20398504, Group Number 1
**Note to TA**: The professor was not clear at all his expectations of this assignment... When we asked he would either tell us to ask ChatGPT or to send an email which he never responded to anyways. In the rare moments he did try to help, the answers were very vague so I tried my very best to be detailed D:
- Each function that works with a requirement is listed under its own file, so scroll down to find more. 
- "Not Implemented" means it only includes the declaration of a function with barebones constant return statement placeholder or none at all. "Partial" means there are some missing features OR <u>BUGS even if the rest of the function is complete</u>. 
- Some functions do not state a specific R# but because one of its requirement points mentioned such a function, then I included it as a part of the requirement in the chart. For example, R4 which states to want to "Calculates and displays any late fees owed." but that is also a function in R5! 
- Some functions can be fully complete but it will call other functions that are not complete yet, which is a matter of only the incomplete function and not the one calling it.<br><br>

# Implementation Status
### library_service.py
| Req# | Function Name | Implementation Status (Complete/Partial/Not Implemented) | Missing/Bugs |
|-----|----------------------------------|------------------------------------|-----------------------------|
| R1  | `add_book_to_catalog` | Partial | Missing a check for invalid isbn input such as `isbn=None` which will throw a `TypeError`. Also does not confirm that isbn is exactly 13 digits of a string because an input of 13 spaces still counts as `len(isbn)=13` but is clearly invalid digits. Negative ISBN that are still length of 13 also works even though it should not. |
| R3  | `borrow_book_by_patron`  | Partial | Everything else in the function is complete, but testing that `current_borrowed > 5` is incorrect and thus does not fully satisfy R3 as it must check the patron borrowing limit which is max 5 books. For the function to be complete, simply add an equal sign so `current_borrowed >= 5`. |
| R4  | `return_book_by_patron`  | Not Implemented | Accepts parameter of `patron_id` and `book_id` but has not been implemented yet otherwise and always returns False with a message stating that. Does not verify that the book was borrowed by the patron. Does not update available copies and records return date. Missing calculation/display of late fees owed. |
| R4  | `calculate_late_fee_for_book` | Not Implemented | Does not calculate or display any late fees owed, still an empty function besides the TODO list and does not actually return anything. |
| R5  | `calculate_late_fee_for_book` | Not Implemented | Does not calculate late fees for overdue books at all (nothing for books due 14 days after borrowing, $0.50/day for first 7 days overdue, $1.00/day for each additional day after 7 days, Maximum $15.00 per book) still an empty function besides the TODO list and does not actually return anything. |
| R6  | `search_books_in_catalog` | Not Implemented | Function is completely empty except for TODO comments and a return of empty list `[]`. |
| R7  | `get_patron_status` | Not Implemented | Function is completely empty except for TODO comments and a return of `{}`. |

### search_routes.py
| Req# | Function Name | Implementation Status (Complete/Partial/Not Implemented) | Missing/Bugs |
|-----|----------------------------------|------------------------------------|-----------------------------|
| R6  | `search_books` | Partial | Main API interface that correctly has `q` search term but `type` only has the back-end option to search for title, then library service file is not implemented. Front-end has option for title/author partial matching and ISBN exact matching but it does not exist back-end and displays a message of not being implemented yet when searching. Logically returns the same format as a catalog display but missing functionality and features. |

### catalog_routes.py
| Req# | Function Name | Implementation Status (Complete/Partial/Not Implemented) | Missing/Bugs |
|-----|----------------------------------|------------------------------------|-----------------------------|
| R1  | `add_book` | Complete | N/A |
| R2  | `catalog` | Complete | N/A |

### borrowing_routes.py
| Req# | Function Name | Implementation Status (Complete/Partial/Not Implemented) | Missing/Bugs |
|-----|----------------------------------|------------------------------------|-----------------------------|
| R3  | `borrow_book` | Complete | N/A |
| R4  | `return_book`  | Complete | Calls `return_book_by_patron` in `library_service.py` to request `patron_id` and `book_id`, as well as attempt to verify the book was borrowed by patron but that function is not yet implemented. |

### api_routes.py
| Req# | Function Name | Implementation Status (Complete/Partial/Not Implemented) | Missing/Bugs |
|-----|----------------------------------|------------------------------------|-----------------------------|
| R4  | `get_late_fee`  | Complete | Calls for `calculate_late_fee_for_book` in `library_service` but that was not implemented yet. |
| R5  | `get_late_fee` | Complete | Correctly provides an API endpoint before the function. However, it calls for `calculate_late_fee_for_book` in `library_service` which was not implemented yet. Returns `jsonify(result)` if successful as long as `result=calculate_late_fee_for_book(patron_id, book_id)` worked as expected when the function is completed, otherwise it will return integers 501 or 200. |
| R6  | `search_books_api` | Partial | Alternative API interface that correctly has `q` search term but `type` only has the back-end option to search for title, then library service file is not implemented. Front-end has option for title/author partial matching and ISBN exact matching but it does not exist back-end and displays a message of not being implemented yet when searching. |

+`get_all_books` function inside of `database.py` for R2 returns a list of dictionaries and is fully implemented with no bugs. 

<br>

# Summary of Test Scripts
Each test file clears the database before running then calls `init_database()` and `add_sample_data()` to ensure a clean, deterministic state. Each file must be run in the (venv) terminal with `python -m pytest tests/r#_test.py` for each number `#` to pytest. 
### R1:
- `test_add_book_valid_input` tests by adding a book with valid inputs of book title, author, ISBN, number of copies, then asserting for correct output and a success message. 
- `test_add_book_valid_input2` tests the same as above but straining the checks by setting a title length == 200 characters and author length == 100 characters, then a larger copies count. 
- `test_add_book_no_title` tests by adding a book with no title, which receives the message that a title is required. A book is not successfully added. 
- `test_add_book_long_title` tests by adding a book with a title > 200 characters which receives the message enforcing that requirement and a book is also not successfully added. 
- `test_add_book_no_author` tests by adding an empty author, to which the message states that an author is required, and a book is not added. 
- `test_add_book_long_author` tests by adding a book with an author of over 100 characters so a book is not added. 
- `test_add_book_invalid_isbn_too_short` tests by adding an ISBN too short so a book is not added. 
-  `test_add_book_negative_copies` tests by adding negative copies of a book so it is not added. 
- `test_add_book_existing_ISBN` attempts to add an existing ISBN so it is not added. 
- `test_add_book_negative_ISBN` attempts to add a negative ISBN so it is not added. 
- `test_add_book_invalid_isbn_13_spaces` attempts to add an ISBN that is length 13 but all spaces like "             ", which should normally return success == false and a message that it is invalid. However, this is a bug I discovered where it actually successfully adds the book to the library even when it is invalid. Similar goes for any 13 characters that are not an integer, it shouldn't be added but still is. 

### R2
No such requirement function exists in `library_service.py` so below are tests for `database.py` function `get_all_books`. 
- `test_get_all_books` tests that calling the function returns a list of books, not None or empty, and checks that the return type is a list.
- `test_get_all_books_content` tests that each returned book dictionary contains the required fields (id, title, author, isbn, total_copies, available_copies) and that each field is the correct data type.
- `test_get_all_books_copy_consistency` tests that available_copies is never greater than total_copies, and neither value is negative.
- `test_get_all_books_empty` resets the database to empty, then tests that the function correctly returns an empty list [] when no books exist.
- `test_get_all_books_unique_isbn` tests that every book in the catalog has a unique ISBN (no duplicates allowed).
- `test_get_all_books_table_integrity` tests that each book dictionary has exactly 6 fields, confirming table integrity.

### R3
- `test_borrow_book_by_patron_parameters` tests borrowing a book with a valid 6-digit patron ID and a valid book ID that has available copies, which succeeds and returns a success message.
- `test_borrow_book_by_patron_invalid_patron_id` tests invalid patron IDs: blank spaces, fewer than 6 digits, and a negative number. All return failure with the message "Invalid patron ID. Must be exactly 6 digits."
- `test_borrow_book_by_patron_book_not_found` tests invalid or unavailable book IDs: a non-existent ID, a negative ID, and a book with no available copies. These all fail with appropriate error messages of ("Book not found." or "This book is currently not available."). 
- `test_borrow_book_by_patron_book_available` tests borrowing a valid, available book again and succeeds with the success message.
- `test_borrow_book_by_patron_max_limit` tests the borrowing limit rule by borrowing 5 books successfully, then attempts a 6th borrow. Due to a bug (current_borrowed > 5 instead of >= 5), the 6th borrow is incorrectly allowed. This test allowed me to discover that bug. 

### R4
Tests based on `library_services.py` function `return_book_by_patron`, but most functions except for the first will fail the test because it has not been implemented yet. 
- `test_return_book_by_patron_todo_message` tests the placeholder TODO response. Since the function is not implemented yet, it by default returns (False, "Book return functionality is not yet implemented."). This is the only test that currently passes.
- `test_return_book_by_patron_form_parameters` tests invalid inputs for patron and book IDs (nonexistent ID, negative ID, too short patron ID, negative patron ID). These are expected to fail because the function is unimplemented and does not yet handle validation.
- `test_return_book_by_patron_valid` tests returning a book after first borrowing it but will fail until the function is implemented. After `return_book_by_patron` is fully implemented and complete, then a pass is expected. 
- `test_return_book_by_patron_not_borrowed` tests attempting to return a book that the patron never borrowed, expecting success == False and the book not being returned. Again, this will fail until the function is implemented.
- `test_calculate_fine_for_late_return` simulates a late return scenario (book due 7 days ago) and tests that a positive fee is calculated. This will also fail until the late fee calculation is integrated with returns.

### R5
Tests based on `library_services.py` function `calculate_late_fee_for_book`, but most functions except for the first will fail the test because it has not been implemented yet. 
- `test_books_due_14_days` borrows a book and checks that the due date is exactly 14 days after the borrow date.
- `test_invalid_patrons` tests invalid patron IDs ("000", empty string, long non-digit string). Expects a status like "Invalid patron ID." (but will fail until validation is implemented).
- `test_calculate_late_fee_for_book_no_overdue` inserts a record that is not yet due and expects a $0.00 fee and days_overdue == 0 (will fail until implemented).
- `test_calculate_late_fee_for_book_1_day` simulates being 1 day overdue and expects a $0.50 fee and days_overdue == 1 (will fail until implemented).
- `test_calculate_late_fee_for_book_7_days` simulates 7 days overdue and expects $3.50 (7 × $0.50) and days_overdue == 7 (will fail until implemented).
- `test_calculate_late_fee_for_book_10_days` simulates 10 days overdue and expects $6.50 ((7 × $0.50) + (3 × $1.00)) and days_overdue == 10 (will fail until implemented).
- `test_calculate_late_fee_for_book_maximum` simulates an overdue long enough to exceed the cap and expects the maximum $15.00 fee with correct days_overdue (will fail until implemented).
- `test_calculate_late_fee_for_book_JSON_response` asserts that the function returns a dictionary suitable for JSON serialization (will fail until implemented).

### R6
Tests based on `library_services.py` function `search_books_in_catalog`, many functions will pass for a different reason than the expected one because the incomplete function always returns `[]` by default, giving the illusion it passed for my test code reasons. Some functions will also fail the test because `search_books_in_catalog` has not been implemented yet. 
- `test_search_books_in_catalog_invalid` searches for a non-existent title ("One Piece") and expects an empty list. This passes now only because the function stub always returns [].
- `test_search_books_in_catalog` searches for a known sample book by exact title ("1984") and expects one match with the correct title/author/isbn. Will fail until search is implemented.
- `test_search_books_in_catalog_partials` tests partial matches: "19" for title and "George" for author, each expecting the "1984" record. Will fail until partial matching is implemented.
- `test_search_books_in_catalog_ISBN_exact` searches by exact ISBN ("9780451524935") and expects the "1984" record. Will fail until ISBN matching is implemented.
- `test_search_books_in_catalog_invalid_ISBN` searches with an invalid ISBN ("676767") and expects []. This passes now but only because the incomplete function returns [] unconditionally.
- `test_search_books_in_catalog_q_invalid_term` uses an empty query q string with a valid type and expects []. This passes now but only because the incomplete function returns [] unconditionally. In a complete implementation, you might return [] or an error/status.
- `test_search_books_in_catalog_invalid_type` uses an invalid type string and expects []. This passes now but only because the incomplete function returns [] unconditionally. A complete implementation should validate the type then return [] or an error/status.

### R7
Tests based on `library_services.py` function `get_patron_status_report`, but most functions except for the first will fail the test because it has not been implemented yet. 
- `test_get_patron_status_report_invalid` calls the function with several invalid patron IDs ("", "literally cooked", "-67", "7") and expects an empty dict or an error message depending on chosen implementation. This should pass because of the current unimplemented function that always returns {} anyways.
- `test_get_patron_status_report_var_types` checks that a valid report (for "666666") returns a dictionary with the expected keys and value types (current_borrowed list, borrow_history list, total_late_fees float, current_borrowed_count int).
- `test_get_patron_status_report_valid` uses a new/clean patron ("676767") and expects a dict with: current_borrowed == [], total_late_fees == 0.0, current_borrowed_count == 0, and borrow_history == []. Will fail until the function is implemented to build this structure.
- `test_get_patron_status_report_old_valid` uses an existing patron with history ("696969") and expects populated fields (two current borrows, total late fees 15.0, count 2, and specific history entries). Will fail until implementation computes/returns these values.
