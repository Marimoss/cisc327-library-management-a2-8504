import pytest
from services.library_service import pay_late_fees, refund_late_fee_payment 
from unittest.mock import Mock
from services.payment_service import PaymentGateway

# ASSIGNMENT 3. 
# Only required test scenarios are implemented for Task 2.1 so far. -------------------------------------------------------------------------
def test_pay_late_fees_successful_payment(mocker):
    '''Test successful payment of late fees scenario.'''
    # STUB database functions with fake data. Only the most necessary return values are provided. 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "Mock Book"})

    # MOCK payment gateway. Simulate success with patron_id="888888".  
    mock_gateway = Mock(spec=PaymentGateway)
    # process_payment() returns tuple (success: bool, transaction_id: str, message: str).
    mock_gateway.process_payment.return_value = (True, "txn_888888_1731110000", "Payment of $1.00 processed successfully")
    
    # Call the tested function, passing patron_id, book_id, and mocked gateway. 
    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)

    assert success is True
    assert msg  == "Payment successful! Payment of $1.00 processed successfully"
    assert txn == "txn_888888_1731110000" 
    mock_gateway.process_payment.assert_called_once()  # Verify it was called only once. 
    mock_gateway.process_payment.assert_called_with(
        patron_id="888888", 
        amount=1.00, 
        description="Late fees for 'Mock Book'"
    )  # Verify correct process_payment() parameters. 


def test_pay_late_fees_payment_declined(mocker):
    '''Test payment declined by gateway scenario, due to amount exceeding limit.'''
    # STUB database functions. 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1001.00})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "Mock Book"})

    # MOCK payment gateway. Force a declined response. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "txn_888888_1731110000", "Payment declined: amount exceeds limit")

    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)

    assert success is False
    assert msg == "Payment failed: Payment declined: amount exceeds limit"  # From process_payment() msg.
    assert txn is None  # Not set on failure. 
    mock_gateway.process_payment.assert_called_once()
    mock_gateway.process_payment.assert_called_with(
        patron_id="888888", 
        amount=1001.00, 
        description="Late fees for 'Mock Book'"
    )


def test_pay_late_fees_invalid_patron_id(mocker): 
    '''Test payment using an invalid patron ID scenario. pay_late_fees() validates patron ID first, so process_payment() mock 
    should NEVER get called in the first place.'''
    # MOCK payment gateway setup, but process_payment() is never called. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_invalid", "Not actually called...")  
    
    success, msg, txn = pay_late_fees("invalid_id", 9, mock_gateway)  # Call tested function with invalid patron ID.

    assert success is False  # Function failed as expected. 
    assert msg == "Invalid patron ID. Must be exactly 6 digits."
    assert txn is None
    mock_gateway.process_payment.assert_not_called()  # Verify mock process_payment() was NOT called.


def test_pay_late_fees_zero_late_fees(mocker): 
    '''Test scenario where there are zero late fees. Like before, pay_late_fees() should NOT call process_payment() mock.'''
    # STUB database function, to return zero late fees.
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.00})

    # MOCK payment gateway setup, but process_payment() is never called.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_zero", "Not actually called...")

    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)

    assert success is False  # Function failed as expected.
    assert msg == "No late fees to pay for this book."
    assert txn is None
    mock_gateway.process_payment.assert_not_called()  # Verify mock process_payment() was NOT called.


def test_pay_late_fees_network_error(mocker):
    '''Test scenario where there is a payment gateway network error exception handling.'''
    # STUB database functions.
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mocker.patch("services.library_service.get_book_by_id", return_value={"title": "Mock Book"})

    # MOCK payment gateway setup, to raise an exception simulating network error.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network error, unable to reach payment gateway.")

    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)

    assert success is False  # Payment error. 
    assert msg == "Payment processing error: Network error, unable to reach payment gateway."
    assert txn is None
    mock_gateway.process_payment.assert_called_once()  # It was called once before raising exception. 
    mock_gateway.process_payment.assert_called_with(
        patron_id="888888",
        amount=1.00,
        description="Late fees for 'Mock Book'"
    )


# refund_late_fee_payment() never calls database functions so no stubbing is needed. 
def test_refund_late_fee_payment_successful_refund(): 
    '''Test successful refund scenario.'''
    # MOCK payment gateway, refund_payment() returns tuple (success: bool, message: str). 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $1.00 processed successfully. Refund ID: txn_888888_1731110000")  # Arbitrary refund ID used.

    success, msg = refund_late_fee_payment("txn_888888_1731110000", 1.00, mock_gateway)

    assert success is True
    assert msg == "Refund of $1.00 processed successfully. Refund ID: txn_888888_1731110000"
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with("txn_888888_1731110000", 1.00)


def test_refund_late_fee_payment_invalid_transaction_id():
    '''Test refund rejection due to invalid transaction ID. refund_payment() mock is never actually called in this case.'''
    # MOCK payment gateway, to simulate invalid transaction ID rejection.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Not actually called...")

    success, msg = refund_late_fee_payment("invalid_txn_id", 1.00, mock_gateway)
    assert success is False
    assert msg == "Invalid transaction ID."
    mock_gateway.refund_payment.assert_not_called()  # refund_payment() should NOT be called due to invalid ID check first.


# refund_late_fee_payment() required test scenarios: Invalid refund amounts (negative, zero, exceeds $15 maximum). 
def test_refund_late_fee_payment_invalid_refund_amounts():
    '''Test refund rejection due to invalid refund amounts (negative, zero, exceeds $15 maximum). 
    refund_payment() mock is never actually called in this case.'''
    # MOCK payment gateway, to simulate invalid refund amount rejection.
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Not actually called...")

    # Negative refund.
    success, msg = refund_late_fee_payment("txn_888888_1731110000", -5.00, mock_gateway)
    assert success is False
    assert msg == "Refund amount must be greater than 0."

    # Zero refund.
    success, msg = refund_late_fee_payment("txn_888888_1731110000", 0.00, mock_gateway)
    assert success is False
    assert msg == "Refund amount must be greater than 0."

    # Refund exceeds $15 maximum.
    success, msg = refund_late_fee_payment("txn_888888_1731110000", 20.00, mock_gateway)
    assert success is False
    assert msg == "Refund amount exceeds maximum late fee."

    mock_gateway.refund_payment.assert_not_called()  # refund_payment() should NEVER be called because the function returns early.


# Task 2.2: Code Coverage Testing. ----------------------------------------------------------------------------------------------------------
# Each R1-R7 additional tests are added in their respective test files! This file is only for payment mock/stub tests.
def test_pay_late_fees_no_fee_info(mocker):
    '''Test payment for late fees, calculate_late_fee_for_book() is called but its return fee_info is None, so the rest is never called.'''
    # STUB database-related function, simulate it having an issue with calculating late fees. 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value=None) 

    # MOCK payment gateway setup, but process_payment() is never called. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_zero", "Not actually called...")  # Kept for consistency with above tests. 

    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)  # Call the tested function. 

    assert success is False 
    assert msg == "Unable to calculate late fees."
    assert txn is None
    mock_gateway.process_payment.assert_not_called()  # Verify mock process_payment() was NOT called.


def test_pay_late_fees_no_book(mocker): 
    '''Test payment for late fees, get_book_by_id() returns None, so the rest is never called.'''
    # STUB database-related function, simulate it having an issue with getting a book by its ID. 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mocker.patch("services.library_service.get_book_by_id", return_value=None)

    # MOCK payment gateway setup, but process_payment() is never called. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_zero", "Not actually called...")

    success, msg, txn = pay_late_fees("888888", 9, mock_gateway)

    assert success is False 
    assert msg == "Book not found."
    assert txn is None
    mock_gateway.process_payment.assert_not_called()  # Verify mock process_payment() was NOT called.


def test_refund_late_fee_payment_failed(): 
    '''Test failed refund scenario.'''
    # MOCK payment gateway, to return with success=False. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (False, "Invalid transaction ID") 

    success, msg = refund_late_fee_payment("txn_888888_1731110000", 1.00, mock_gateway)

    assert success is False  # refund_payment() was not a success. 
    assert msg == "Refund failed: Invalid transaction ID"
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with("txn_888888_1731110000", 1.00)


def test_refund_late_fee_payment_exception():
    '''Test refund processing error because of an exception when calling mock refund_payment().'''
    # MOCK payment gateway. 
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.side_effect = Exception("Network timeout.")

    success, msg = refund_late_fee_payment("txn_888888_1731110000", 1.00, mock_gateway)

    assert success is False  # Refund processing error. 
    assert msg == "Refund processing error: Network timeout."
    mock_gateway.refund_payment.assert_called_once()  # It was called once before raising exception. 
    mock_gateway.refund_payment.assert_called_with("txn_888888_1731110000", 1.00)
