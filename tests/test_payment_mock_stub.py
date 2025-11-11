"""Unit tests for payment workflows using stubs and mocks."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway, PaymentGatewayError


@pytest.fixture
def payment_gateway_mock() -> Mock:
    return Mock(spec=PaymentGateway)


def stub_book(mocker, title="Test Title"):
    return mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": title, "author": "Anon", "available_copies": 1}
    )


def stub_late_fee(mocker, amount: float):
    return mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": amount, "days_overdue": 2, "status": "Overdue"}
    )


def test_pay_late_fees_success(mocker, payment_gateway_mock):
    stub_book(mocker, title="1984")
    stub_late_fee(mocker, amount=7.5)
    payment_gateway_mock.process_payment.return_value = SimpleNamespace(status="success", transaction_id="txn_1")

    result = pay_late_fees("123456", 1, payment_gateway_mock)

    assert result["success"] is True
    assert result["transaction_id"] == "txn_1"
    payment_gateway_mock.process_payment.assert_called_once_with("123456", 7.5, description="Late fee for 1984")


def test_pay_late_fees_declined(mocker, payment_gateway_mock):
    stub_book(mocker, title="Brave New World")
    stub_late_fee(mocker, amount=4.0)
    payment_gateway_mock.process_payment.return_value = SimpleNamespace(status="declined", transaction_id="txn_2")

    result = pay_late_fees("123456", 1, payment_gateway_mock)

    assert result["success"] is False
    assert "declined" in result["status"].lower()
    payment_gateway_mock.process_payment.assert_called_once_with("123456", 4.0, description="Late fee for Brave New World")


def test_pay_late_fees_invalid_patron_does_not_invoke_gateway(mocker, payment_gateway_mock):
    book_stub = stub_book(mocker)
    fee_stub = stub_late_fee(mocker, amount=6.0)

    result = pay_late_fees("111", 1, payment_gateway_mock)

    assert result["success"] is False
    book_stub.assert_not_called()
    fee_stub.assert_not_called()
    payment_gateway_mock.process_payment.assert_not_called()


def test_pay_late_fees_zero_amount_does_not_charge(mocker, payment_gateway_mock):
    stub_book(mocker)
    stub_late_fee(mocker, amount=0.0)

    result = pay_late_fees("123456", 1, payment_gateway_mock)

    assert result["success"] is False
    assert "no outstanding" in result["status"].lower()
    payment_gateway_mock.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker, payment_gateway_mock):
    stub_book(mocker)
    stub_late_fee(mocker, amount=3.25)
    payment_gateway_mock.process_payment.side_effect = PaymentGatewayError("timeout")

    result = pay_late_fees("123456", 1, payment_gateway_mock)

    assert result["success"] is False
    assert "failed" in result["status"].lower()
    payment_gateway_mock.process_payment.assert_called_once_with("123456", 3.25, description="Late fee for Test Title")


def test_pay_late_fees_invalid_book_id(mocker, payment_gateway_mock):
    stub_book(mocker)
    stub_late_fee(mocker, amount=5.0)

    result = pay_late_fees("123456", "bad", payment_gateway_mock)

    assert result["success"] is False
    payment_gateway_mock.process_payment.assert_not_called()


def test_refund_success(payment_gateway_mock):
    payment_gateway_mock.refund_payment.return_value = SimpleNamespace(status="refunded", transaction_id="refund_1")

    result = refund_late_fee_payment("txn_1", 5.0, payment_gateway_mock)

    assert result["success"] is True
    assert result["transaction_id"] == "refund_1"
    payment_gateway_mock.refund_payment.assert_called_once_with("txn_1", 5.0)


def test_refund_invalid_transaction(payment_gateway_mock):
    result = refund_late_fee_payment("   ", 5.0, payment_gateway_mock)

    assert result["success"] is False
    payment_gateway_mock.refund_payment.assert_not_called()


@pytest.mark.parametrize("bad_amount", [-1, 0, 20])
def test_refund_invalid_amounts(payment_gateway_mock, bad_amount):
    result = refund_late_fee_payment("txn_1", bad_amount, payment_gateway_mock)

    assert result["success"] is False
    payment_gateway_mock.refund_payment.assert_not_called()


def test_refund_gateway_error(payment_gateway_mock):
    payment_gateway_mock.refund_payment.side_effect = PaymentGatewayError("network")

    result = refund_late_fee_payment("txn_1", 5.0, payment_gateway_mock)

    assert result["success"] is False
    assert "failed" in result["status"].lower()
    payment_gateway_mock.refund_payment.assert_called_once_with("txn_1", 5.0)
