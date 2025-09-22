"""
Tests for CreditNote functionality.
"""
import pytest
from datetime import datetime

from en16931 import CreditNote, CreditNoteLine, Entity, PostalAddress


class TestCreditNote:

    def test_initialization(self):
        """Test CreditNote initialization."""
        cn = CreditNote()
        assert cn.credit_note_id == '1'
        assert cn.currency == 'EUR'
        assert cn.credit_note_type_code == 381
        assert cn.ubl_version_id == "2.1"

    def test_initialization_with_params(self):
        """Test CreditNote initialization with parameters."""
        cn = CreditNote(credit_note_id="CN-001", currency="USD")
        assert cn.credit_note_id == "CN-001"
        assert cn.currency == "USD"

    def test_invalid_currency(self):
        """Test invalid currency raises KeyError."""
        with pytest.raises(KeyError):
            CreditNote(currency="INVALID")

    def test_issue_date_property(self):
        """Test issue date property."""
        cn = CreditNote()
        cn.issue_date = "2023-12-01"
        assert cn.issue_date == datetime(2023, 12, 1)

    def test_issue_date_datetime(self):
        """Test issue date with datetime object."""
        cn = CreditNote()
        date = datetime(2023, 12, 1)
        cn.issue_date = date
        assert cn.issue_date == date

    def test_due_date_property(self):
        """Test due date property."""
        cn = CreditNote()
        cn.due_date = "2023-12-31"
        assert cn.due_date == datetime(2023, 12, 31)

    def test_billing_reference(self):
        """Test billing reference property."""
        cn = CreditNote()
        cn.billing_reference = "INV-001"
        assert cn.billing_reference == "INV-001"

    def test_seller_buyer_party(self):
        """Test seller and buyer party properties."""
        cn = CreditNote()
        
        # Create valid entities
        seller = Entity(name="Test Seller", tax_scheme="VAT",
                       tax_scheme_id="DE123456789", country="DE",
                       party_legal_entity_id="DE123456789",
                       registration_name="Test Seller Ltd",
                       endpoint="DE123456789", endpoint_scheme="DE:VAT",
                       address="Test Street", city="Test City", 
                       postalzone="12345", province="Test Province")
        
        buyer = Entity(name="Test Buyer", tax_scheme="VAT", 
                      tax_scheme_id="DE987654321", country="DE",
                      party_legal_entity_id="DE987654321",
                      registration_name="Test Buyer Ltd",
                      endpoint="DE987654321", endpoint_scheme="DE:VAT",
                      address="Buyer Street", city="Buyer City",
                      postalzone="54321", province="Buyer Province")
        
        cn.seller_party = seller
        cn.buyer_party = buyer
        
        assert cn.seller_party == seller
        assert cn.buyer_party == buyer

    def test_add_lines(self):
        """Test adding credit note lines."""
        cn = CreditNote()
        
        line1 = CreditNoteLine(
            quantity=10, 
            price=5.00, 
            item_name="Test Item", 
            tax_percent=0.19, 
            tax_category="S"
        )
        
        line2 = CreditNoteLine(
            quantity=2, 
            price=25.00, 
            item_name="Another Item", 
            tax_percent=0.19, 
            tax_category="S"
        )
        
        cn.add_line(line1)
        cn.add_line(line2)
        
        assert len(cn.lines) == 2
        assert cn.lines[0] == line1
        assert cn.lines[1] == line2

    def test_add_lines_from_list(self):
        """Test adding multiple lines from a list."""
        cn = CreditNote()
        
        lines = [
            CreditNoteLine(quantity=1, price=10.00, item_name="Item 1", tax_percent=0.19, tax_category="S"),
            CreditNoteLine(quantity=2, price=15.00, item_name="Item 2", tax_percent=0.19, tax_category="S"),
        ]
        
        cn.add_lines_from(lines)
        
        assert len(cn.lines) == 2

    def test_calculations(self):
        """Test credit note calculations."""
        cn = CreditNote()
        
        # Add lines with different tax rates
        line1 = CreditNoteLine(quantity=10, price=5.00, item_name="Item 1", tax_percent=0.19, tax_category="S")
        line2 = CreditNoteLine(quantity=2, price=25.00, item_name="Item 2", tax_percent=0.07, tax_category="S")
        
        cn.add_line(line1)
        cn.add_line(line2)
        
        # Test subtotal (without tax)
        expected_subtotal = (10 * 5.00) + (2 * 25.00)  # 50 + 50 = 100
        assert float(cn.subtotal().amount) == expected_subtotal
        
        # Test tax amount calculation
        expected_tax = (50 * 0.19) + (50 * 0.07)  # 9.5 + 3.5 = 13
        assert float(cn.tax_amount().amount) == expected_tax
        
        # Test total (with tax)
        expected_total = expected_subtotal + expected_tax  # 100 + 13 = 113
        assert float(cn.total().amount) == expected_total

    def test_unique_taxes(self):
        """Test unique taxes calculation."""
        cn = CreditNote()
        
        # Add lines with same and different tax rates
        line1 = CreditNoteLine(quantity=1, price=10.00, item_name="Item 1", tax_percent=0.19, tax_category="S")
        line2 = CreditNoteLine(quantity=1, price=10.00, item_name="Item 2", tax_percent=0.19, tax_category="S") 
        line3 = CreditNoteLine(quantity=1, price=10.00, item_name="Item 3", tax_percent=0.07, tax_category="S")
        
        cn.add_lines_from([line1, line2, line3])
        
        unique_taxes = cn.unique_taxes
        assert len(unique_taxes) == 2  # Should have 2 unique tax rates (19% and 7%)

    def test_to_xml_basic(self):
        """Test basic XML generation."""
        cn = CreditNote(credit_note_id="CN-001")
        cn.issue_date = "2023-12-01"
        
        # Create minimal parties
        seller = Entity(name="Test Seller", tax_scheme="VAT",
                       tax_scheme_id="DE123456789", country="DE",
                       party_legal_entity_id="DE123456789",
                       registration_name="Test Seller Ltd",
                       endpoint="DE123456789", endpoint_scheme="DE:VAT",
                       address="Test Street", city="Test City",
                       postalzone="12345", province="Test Province")
        
        buyer = Entity(name="Test Buyer", tax_scheme="VAT",
                      tax_scheme_id="DE987654321", country="DE", 
                      party_legal_entity_id="DE987654321",
                      registration_name="Test Buyer Ltd",
                      endpoint="DE987654321", endpoint_scheme="DE:VAT",
                      address="Buyer Street", city="Buyer City",
                      postalzone="54321", province="Buyer Province")
        
        cn.seller_party = seller
        cn.buyer_party = buyer
        
        # Add a simple line
        line = CreditNoteLine(
            quantity=1,
            price=100.00, 
            item_name="Test Item",
            tax_percent=0.19,
            tax_category="S"
        )
        cn.add_line(line)
        
        xml = cn.to_xml()
        
        # Basic validation
        assert '<?xml version="1.0"' in xml
        assert '<CreditNote' in xml
        assert 'CN-001' in xml
        assert '2023-12-01' in xml
        assert 'Test Seller' in xml
        assert 'Test Buyer' in xml
        assert 'Test Item' in xml


class TestCreditNoteLine:

    def test_initialization(self):
        """Test CreditNoteLine initialization."""
        line = CreditNoteLine()
        assert line.quantity is None
        assert line.price is None
        assert line.currency == "EUR"
        assert line.unit_code == "C62"

    def test_initialization_with_params(self):
        """Test CreditNoteLine initialization with parameters."""
        line = CreditNoteLine(
            quantity=10,
            price=5.50,
            item_name="Test Item",
            currency="USD",
            tax_percent=0.21,
            tax_category="S"
        )
        
        assert line.quantity == 10
        assert float(line.price.amount) == 5.50
        assert line.item_name == "Test Item"
        assert line.currency == "USD"
        assert line.tax_percent == 0.21
        assert line.tax_category == "S"

    def test_invalid_currency(self):
        """Test invalid currency raises KeyError."""
        with pytest.raises(KeyError):
            CreditNoteLine(currency="INVALID")

    def test_line_extension_amount_calculation(self):
        """Test line extension amount calculation."""
        line = CreditNoteLine(quantity=10, price=5.50, currency="EUR")
        
        expected_amount = 10 * 5.50
        assert float(line.line_extension_amount.amount) == expected_amount

    def test_tax_property(self):
        """Test tax property."""
        line = CreditNoteLine(tax_percent=0.19, tax_category="S", tax_name="VAT")
        
        tax = line.tax
        assert tax is not None
        assert tax.percent == 0.19
        assert tax.category == "S"
        assert tax.name == "VAT"

    def test_no_tax(self):
        """Test line without tax."""
        line = CreditNoteLine(quantity=1, price=10.00)
        assert line.tax is None

    def test_is_valid(self):
        """Test line validation."""
        # Invalid line (missing required fields)
        line = CreditNoteLine()
        assert not line.is_valid()
        
        # Valid line
        line = CreditNoteLine(
            quantity=1,
            price=10.00,
            tax_percent=0.19,
            tax_category="S"
        )
        assert line.is_valid()

    def test_has_tax(self):
        """Test has_tax method."""
        from en16931 import Tax
        
        line = CreditNoteLine(tax_percent=0.19, tax_category="S")
        tax = Tax(0.19, "S", "VAT")
        
        assert line.has_tax(tax)
        assert line.has_tax(None)  # Should return True for None
        
        different_tax = Tax(0.21, "S", "VAT")
        assert not line.has_tax(different_tax)

    def test_repr(self):
        """Test string representation."""
        line = CreditNoteLine()
        assert "empty" in repr(line)
        
        line = CreditNoteLine(
            quantity=5,
            price=10.00,
            item_name="Test Item",
            tax_percent=0.19,
            tax_category="S"
        )
        
        repr_str = repr(line)
        assert "5" in repr_str
        assert "Test Item" in repr_str
        assert "10.00" in repr_str
        assert "EUR" in repr_str