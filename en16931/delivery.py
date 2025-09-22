"""
Class for representing delivery information in EN16931 documents.
"""
from datetime import datetime
from en16931.postal_address import PostalAddress
from en16931.utils import parse_date


class DeliveryInformation:
    """EN16931 Delivery Information class.

    This class represents delivery information including delivery date,
    location, and address details according to EN16931 standard.

    Example usage:

    >>> delivery = DeliveryInformation()
    >>> delivery.actual_delivery_date = "2023-12-01"
    >>> delivery.location_id = "WAREHOUSE_A"
    >>> delivery.location_scheme_id = "GLN"
    
    Or with delivery address:

    >>> address = PostalAddress(
    ...     address="123 Delivery Street",
    ...     city_name="Delivery City",
    ...     postal_zone="12345",
    ...     country="DE"
    ... )
    >>> delivery = DeliveryInformation(
    ...     actual_delivery_date="2023-12-01",
    ...     delivery_address=address
    ... )
    """

    def __init__(self, actual_delivery_date=None, location_id=None,
                 location_scheme_id=None, delivery_address=None):
        """Initialize DeliveryInformation.

        Parameters
        ----------
        actual_delivery_date: string or datetime (optional)
            The actual delivery date.

        location_id: string (optional)
            Identifier for the delivery location.

        location_scheme_id: string (optional)
            Scheme identifier for the location (e.g., 'GLN').

        delivery_address: PostalAddress (optional)
            Address where goods were/will be delivered.
        """
        self._actual_delivery_date = None
        self.location_id = location_id
        self.location_scheme_id = location_scheme_id
        self._delivery_address = None

        # Set the date using the property setter for validation
        if actual_delivery_date is not None:
            self.actual_delivery_date = actual_delivery_date

        # Set the address using the property setter for validation
        if delivery_address is not None:
            self.delivery_address = delivery_address

    @property
    def actual_delivery_date(self):
        """Property: Actual delivery date.

        Returns
        -------
        datetime or None
            The actual delivery date.
        """
        return self._actual_delivery_date

    @actual_delivery_date.setter
    def actual_delivery_date(self, date):
        """Set the actual delivery date.

        Parameters
        ----------
        date: string, datetime, or None
            The delivery date.

        Raises
        ------
        ValueError: If the date format is invalid.
        """
        if isinstance(date, str):
            self._actual_delivery_date = parse_date(date)
        elif isinstance(date, datetime):
            self._actual_delivery_date = date
        elif date is None:
            self._actual_delivery_date = None
        else:
            msg = "Expected a string or datetime object, received: {}"
            raise ValueError(msg.format(type(date)))

    @property
    def delivery_address(self):
        """Property: Delivery address.

        Returns
        -------
        PostalAddress or None
            The delivery address.
        """
        return self._delivery_address

    @delivery_address.setter
    def delivery_address(self, address):
        """Set the delivery address.

        Parameters
        ----------
        address: PostalAddress or None
            The delivery address.

        Raises
        ------
        TypeError: If address is not a PostalAddress instance.
        """
        if address is None:
            self._delivery_address = None
        elif isinstance(address, PostalAddress):
            self._delivery_address = address
        else:
            msg = "Expected a PostalAddress object but got a {}"
            raise TypeError(msg.format(type(address)))

    def is_valid(self):
        """Check if the delivery information is valid.

        Returns
        -------
        bool
            True if has at least delivery date or location information.
        """
        return (self._actual_delivery_date is not None or
                self.location_id is not None or
                self._delivery_address is not None)

    def __repr__(self):
        parts = []
        if self._actual_delivery_date:
            parts.append(f"Date: {self._actual_delivery_date.strftime('%Y-%m-%d')}")
        if self.location_id:
            parts.append(f"Location: {self.location_id}")
        if self._delivery_address:
            parts.append(f"Address: {self._delivery_address.city_name}")
        
        if parts:
            return f"{self.__class__.__name__}: {', '.join(parts)}"
        return f"{self.__class__.__name__}: empty"


class DeliveryTerms:
    """EN16931 Delivery Terms class.

    This class represents delivery terms and conditions according to
    Incoterms or other delivery term classifications.

    Example usage:

    >>> terms = DeliveryTerms()
    >>> terms.delivery_terms_code = "DAP"
    >>> terms.delivery_location = "Customer Warehouse"
    """

    def __init__(self, delivery_terms_code=None, delivery_location=None):
        """Initialize DeliveryTerms.

        Parameters
        ----------
        delivery_terms_code: string (optional)
            Delivery terms code (e.g., Incoterms like 'FOB', 'CIF', 'DAP').

        delivery_location: string (optional)
            Description of the delivery location or terms.
        """
        self.delivery_terms_code = delivery_terms_code
        self.delivery_location = delivery_location

    @classmethod
    def incoterms_2020(cls):
        """Get list of valid Incoterms 2020 codes.

        Returns
        -------
        list
            List of Incoterms 2020 codes.
        """
        return [
            'EXW',  # Ex Works
            'FCA',  # Free Carrier
            'CPT',  # Carriage Paid To
            'CIP',  # Carriage and Insurance Paid To
            'DAP',  # Delivered at Place
            'DPU',  # Delivered at Place Unloaded
            'DDP',  # Delivered Duty Paid
            'FAS',  # Free Alongside Ship
            'FOB',  # Free on Board
            'CFR',  # Cost and Freight
            'CIF',  # Cost, Insurance and Freight
        ]

    def is_valid(self):
        """Check if the delivery terms are valid.

        Returns
        -------
        bool
            True if has either terms code or location.
        """
        return (self.delivery_terms_code is not None or
                self.delivery_location is not None)

    def __repr__(self):
        if self.delivery_terms_code and self.delivery_location:
            return f"{self.__class__.__name__}: {self.delivery_terms_code} - {self.delivery_location}"
        elif self.delivery_terms_code:
            return f"{self.__class__.__name__}: {self.delivery_terms_code}"
        elif self.delivery_location:
            return f"{self.__class__.__name__}: {self.delivery_location}"
        return f"{self.__class__.__name__}: empty"