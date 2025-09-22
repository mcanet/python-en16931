"""
Tests for delivery functionality.
"""
import pytest
from datetime import datetime

from en16931.delivery import DeliveryInformation, DeliveryTerms
from en16931.postal_address import PostalAddress


class TestDeliveryInformation:

    def test_initialization(self):
        """Test DeliveryInformation initialization."""
        delivery = DeliveryInformation()
        assert delivery.actual_delivery_date is None
        assert delivery.location_id is None
        assert delivery.location_scheme_id is None
        assert delivery.delivery_address is None

    def test_initialization_with_params(self):
        """Test DeliveryInformation initialization with parameters."""
        address = PostalAddress(
            address="123 Delivery St",
            city_name="Delivery City",
            postal_zone="12345",
            country="DE"
        )
        
        delivery = DeliveryInformation(
            actual_delivery_date="2023-12-01",
            location_id="WAREHOUSE_A",
            location_scheme_id="GLN",
            delivery_address=address
        )
        
        assert delivery.actual_delivery_date == datetime(2023, 12, 1)
        assert delivery.location_id == "WAREHOUSE_A"
        assert delivery.location_scheme_id == "GLN"
        assert delivery.delivery_address == address

    def test_actual_delivery_date_string(self):
        """Test setting delivery date from string."""
        delivery = DeliveryInformation()
        delivery.actual_delivery_date = "2023-12-15"
        assert delivery.actual_delivery_date == datetime(2023, 12, 15)

    def test_actual_delivery_date_datetime(self):
        """Test setting delivery date from datetime."""
        delivery = DeliveryInformation()
        date = datetime(2023, 12, 15, 10, 30)
        delivery.actual_delivery_date = date
        assert delivery.actual_delivery_date == date

    def test_actual_delivery_date_none(self):
        """Test setting delivery date to None."""
        delivery = DeliveryInformation()
        delivery.actual_delivery_date = None
        assert delivery.actual_delivery_date is None

    def test_invalid_delivery_date(self):
        """Test invalid delivery date raises ValueError."""
        delivery = DeliveryInformation()
        with pytest.raises(ValueError):
            delivery.actual_delivery_date = 123

    def test_delivery_address_property(self):
        """Test delivery address property."""
        delivery = DeliveryInformation()
        
        address = PostalAddress(
            address="Test Street",
            city_name="Test City", 
            postal_zone="12345",
            country="DE"
        )
        
        delivery.delivery_address = address
        assert delivery.delivery_address == address

    def test_delivery_address_none(self):
        """Test setting delivery address to None."""
        delivery = DeliveryInformation()
        delivery.delivery_address = None
        assert delivery.delivery_address is None

    def test_invalid_delivery_address(self):
        """Test invalid delivery address raises TypeError."""
        delivery = DeliveryInformation()
        with pytest.raises(TypeError):
            delivery.delivery_address = "Invalid address string"

    def test_is_valid(self):
        """Test delivery information validation."""
        delivery = DeliveryInformation()
        assert not delivery.is_valid()
        
        # Valid with delivery date
        delivery.actual_delivery_date = "2023-12-01"
        assert delivery.is_valid()
        
        # Valid with location ID
        delivery = DeliveryInformation()
        delivery.location_id = "WAREHOUSE_A"
        assert delivery.is_valid()
        
        # Valid with delivery address
        delivery = DeliveryInformation()
        address = PostalAddress(
            address="Test Street",
            city_name="Test City",
            postal_zone="12345", 
            country="DE"
        )
        delivery.delivery_address = address
        assert delivery.is_valid()

    def test_repr(self):
        """Test string representation."""
        delivery = DeliveryInformation()
        assert "empty" in repr(delivery)
        
        delivery.actual_delivery_date = "2023-12-01"
        delivery.location_id = "WAREHOUSE_A"
        
        address = PostalAddress(
            address="Test Street",
            city_name="Test City",
            postal_zone="12345",
            country="DE"
        )
        delivery.delivery_address = address
        
        repr_str = repr(delivery)
        assert "Date: 2023-12-01" in repr_str
        assert "Location: WAREHOUSE_A" in repr_str
        assert "Address: Test City" in repr_str


class TestDeliveryTerms:

    def test_initialization(self):
        """Test DeliveryTerms initialization."""
        terms = DeliveryTerms()
        assert terms.delivery_terms_code is None
        assert terms.delivery_location is None

    def test_initialization_with_params(self):
        """Test DeliveryTerms initialization with parameters."""
        terms = DeliveryTerms(
            delivery_terms_code="DAP",
            delivery_location="Customer Warehouse"
        )
        
        assert terms.delivery_terms_code == "DAP"
        assert terms.delivery_location == "Customer Warehouse"

    def test_incoterms_2020(self):
        """Test Incoterms 2020 class method."""
        incoterms = DeliveryTerms.incoterms_2020()
        assert isinstance(incoterms, list)
        assert 'EXW' in incoterms
        assert 'FOB' in incoterms
        assert 'DAP' in incoterms
        assert 'DDP' in incoterms
        assert len(incoterms) == 11  # Should have 11 Incoterms 2020 codes

    def test_is_valid(self):
        """Test delivery terms validation."""
        terms = DeliveryTerms()
        assert not terms.is_valid()
        
        # Valid with terms code
        terms.delivery_terms_code = "FOB"
        assert terms.is_valid()
        
        # Valid with location
        terms = DeliveryTerms()
        terms.delivery_location = "Port of Hamburg"
        assert terms.is_valid()
        
        # Valid with both
        terms = DeliveryTerms(
            delivery_terms_code="CIF",
            delivery_location="Destination Port"
        )
        assert terms.is_valid()

    def test_repr(self):
        """Test string representation."""
        terms = DeliveryTerms()
        assert "empty" in repr(terms)
        
        # With code only
        terms = DeliveryTerms(delivery_terms_code="FOB")
        repr_str = repr(terms)
        assert "FOB" in repr_str
        
        # With location only
        terms = DeliveryTerms(delivery_location="Customer Warehouse")
        repr_str = repr(terms)
        assert "Customer Warehouse" in repr_str
        
        # With both
        terms = DeliveryTerms(
            delivery_terms_code="DAP",
            delivery_location="Customer Warehouse"
        )
        repr_str = repr(terms)
        assert "DAP" in repr_str
        assert "Customer Warehouse" in repr_str