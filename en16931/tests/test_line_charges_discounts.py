"""
Tests for line-level charges and discounts functionality.
"""
import pytest

from en16931.line_charges_discounts import LineCharge, LineDiscount
from en16931.utils import parse_money
from money.currency import Currency


class TestLineCharge:

    def test_initialization(self):
        """Test LineCharge initialization."""
        charge = LineCharge()
        assert charge.amount is None
        assert charge.reason is None
        assert charge.currency == "EUR"

    def test_initialization_with_params(self):
        """Test LineCharge initialization with parameters."""
        charge = LineCharge(
            amount=5.00,
            reason="Handling fee",
            currency="USD"
        )
        
        assert float(charge.amount.amount) == 5.00
        assert charge.reason == "Handling fee"
        assert charge.currency == "USD"

    def test_invalid_currency(self):
        """Test invalid currency raises KeyError."""
        with pytest.raises(KeyError):
            LineCharge(currency="INVALID")

    def test_amount_property(self):
        """Test amount property."""
        charge = LineCharge(currency="EUR")
        charge.amount = 10.50
        
        assert float(charge.amount.amount) == 10.50

    def test_invalid_amount(self):
        """Test invalid amount raises ValueError."""
        charge = LineCharge()
        with pytest.raises(ValueError):
            charge.amount = "invalid"

    def test_is_valid(self):
        """Test charge validation."""
        charge = LineCharge()
        assert not charge.is_valid()
        
        charge.amount = 5.00
        assert charge.is_valid()

    def test_repr(self):
        """Test string representation."""
        charge = LineCharge()
        assert "empty" in repr(charge)
        
        charge = LineCharge(amount=5.00, reason="Handling fee")
        repr_str = repr(charge)
        assert "5.00" in repr_str
        assert "Handling fee" in repr_str


class TestLineDiscount:

    def test_initialization(self):
        """Test LineDiscount initialization."""
        discount = LineDiscount()
        assert discount.amount is None
        assert discount.percentage is None
        assert discount.reason is None
        assert discount.currency == "EUR"

    def test_initialization_with_amount(self):
        """Test LineDiscount initialization with fixed amount."""
        discount = LineDiscount(
            amount=2.50,
            reason="Volume discount",
            currency="USD"
        )
        
        assert float(discount.amount.amount) == 2.50
        assert discount.percentage is None
        assert discount.reason == "Volume discount"
        assert discount.currency == "USD"

    def test_initialization_with_percentage(self):
        """Test LineDiscount initialization with percentage."""
        discount = LineDiscount(
            percentage=10.0,
            reason="Early payment discount"
        )
        
        assert discount.amount is None
        assert float(discount.percentage) == 10.0
        assert discount.reason == "Early payment discount"

    def test_invalid_currency(self):
        """Test invalid currency raises KeyError."""
        with pytest.raises(KeyError):
            LineDiscount(currency="INVALID")

    def test_amount_property(self):
        """Test amount property."""
        discount = LineDiscount(currency="EUR")
        discount.amount = 15.25
        
        assert float(discount.amount.amount) == 15.25

    def test_percentage_property(self):
        """Test percentage property."""
        discount = LineDiscount()
        discount.percentage = 12.5
        
        assert float(discount.percentage) == 12.5

    def test_invalid_amount(self):
        """Test invalid amount raises ValueError."""
        discount = LineDiscount()
        with pytest.raises(ValueError):
            discount.amount = "invalid"

    def test_invalid_percentage(self):
        """Test invalid percentage raises ValueError."""
        discount = LineDiscount()
        with pytest.raises(ValueError):
            discount.percentage = "invalid"

    def test_calculate_discount_amount_fixed(self):
        """Test discount calculation with fixed amount."""
        discount = LineDiscount(amount=10.00, currency="EUR")
        base_amount = parse_money("100.00", Currency["EUR"])
        
        calculated = discount.calculate_discount_amount(base_amount)
        assert float(calculated.amount) == 10.00

    def test_calculate_discount_amount_percentage(self):
        """Test discount calculation with percentage."""
        discount = LineDiscount(percentage=15.0, currency="EUR")
        base_amount = parse_money("100.00", Currency["EUR"])
        
        calculated = discount.calculate_discount_amount(base_amount)
        assert float(calculated.amount) == 15.00

    def test_calculate_discount_amount_no_discount(self):
        """Test discount calculation with no discount set."""
        discount = LineDiscount(currency="EUR")
        base_amount = parse_money("100.00", Currency["EUR"])
        
        calculated = discount.calculate_discount_amount(base_amount)
        assert float(calculated.amount) == 0.00

    def test_is_valid(self):
        """Test discount validation."""
        discount = LineDiscount()
        assert not discount.is_valid()
        
        # Valid with amount
        discount.amount = 5.00
        assert discount.is_valid()
        
        # Valid with percentage
        discount = LineDiscount()
        discount.percentage = 10.0
        assert discount.is_valid()

    def test_repr(self):
        """Test string representation."""
        discount = LineDiscount()
        assert "empty" in repr(discount)
        
        # With amount
        discount = LineDiscount(amount=5.00, reason="Volume discount")
        repr_str = repr(discount)
        assert "5.00" in repr_str
        assert "Volume discount" in repr_str
        
        # With percentage
        discount = LineDiscount(percentage=10.0, reason="Early payment")
        repr_str = repr(discount)
        assert "10.0%" in repr_str
        assert "Early payment" in repr_str