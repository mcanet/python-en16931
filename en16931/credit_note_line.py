"""
Class for representing a CreditNoteLine.
"""
from decimal import Decimal, InvalidOperation
from money.currency import Currency

from en16931.tax import Tax
from en16931.utils import parse_money


UNIT_CODES = [
    "C62",  # one
    "EA",   # each
    "XUN",  # unidad
    "DAY",  # day
    "HUR",  # hour
    "MTR",  # metre
    "KTM",  # kilometre
    "LTR",  # litre
    "KGM",  # kilogram
    "TNE",  # tonne
    "MTK",  # square metre
    "MTQ",  # cubic metre
    "MON",  # month
    "WEE",  # week
    "MIN",  # minute
    "SEC",  # second
]


class CreditNoteLine:
    """EN16931 CreditNoteLine class.

    Each :class:`CreditNote` has to have at least one credit note
    line in which the quantity and the price of the items is
    reflected.

    You can initialize a CreditNoteLine instance with all its
    attributes:

    >>> cl = CreditNoteLine(quantity=11, unit_code="EA", price=2,
    ...                     item_name='test', currency="EUR",
    ...                     tax_percent=0.21, tax_category="S")

    Or you can do it step by step:

    >>> cl = CreditNoteLine()
    >>> cl.quantity = 11
    >>> cl.price = 2
    >>> cl.item_name = 'test'
    >>> cl.tax_percent = 0.21
    >>> cl.tax_category = "S"

    A CreditNoteLine is only valid if it has quantity, price and
    tax defined:

    >>> cl.is_valid()
    True
    >>> new_line = CreditNoteLine()
    >>> new_line.is_valid()
    False

    """

    def __init__(self, quantity=None, unit_code="C62", price=None,
                 item_name=None, currency="EUR", tax_percent=None,
                 tax_category=None, tax_name=None):
        """Initialize a CreditNoteLine.

        Parameters
        ----------
        quantity: int, float, Decimal
            Quantity of items in the line.

        unit_code: string
            Unit code following UN/ECE rec. 20.

        price: int, float, Decimal, string
            Price of one item (without taxes).

        item_name: string
            Name of the item.

        currency: string
            ISO 4217 currency code for the price.

        tax_percent: int, float, Decimal
            Tax percentage applied to this line. For example,
            0.21 for 21% VAT.

        tax_category: string
            Tax category. Usually one of the standard VAT category
            codes: "S" (standard), "Z" (zero rated), "E" (exempt),
            etc.

        tax_name: string
            Tax name or description.
        """
        self._quantity = None
        self._price = None
        self._line_extension_amount = None
        self.unit_code = unit_code
        self.item_name = item_name
        self.tax_percent = tax_percent
        self.tax_category = tax_category
        self.tax_name = tax_name
        self.currency = currency
        
        # Set these after currency is set
        if quantity is not None:
            self.quantity = quantity
        if price is not None:
            self.price = price

    @property
    def quantity(self):
        """Property: The quantity of the line."""
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        """Sets the quantity of the line."""
        if quantity is None:
            return
        try:
            self._quantity = Decimal(str(quantity))
            if self._price is not None:
                self._line_extension_amount = self._price * self._quantity
        except (ValueError, InvalidOperation):
            raise ValueError("Unrecognized quantity {}".format(quantity))

    @property
    def currency(self):
        """Property: String representation of the ISO 4217 currency code.

        Parameters
        ----------
        currency_str: string
            String representation of the ISO 4217 currency code.

        Raises
        ------
        KeyError: If the currency code is not a valid ISO 4217 code.

        """
        return self._currency.name

    @currency.setter
    def currency(self, currency_str):
        """Sets the currency of the CreditNoteLine.
        """
        try:
            self._currency = Currency[currency_str]
        except KeyError:
            raise KeyError('Currency {} not supported'.format(currency_str))

    @property
    def tax(self):
        """Returns a Tax object representing the taxes applied to the line.
        """
        if self.tax_percent and self.tax_category:
            return Tax(self.tax_percent, self.tax_category, self.tax_name or "")
        else:
            return None

    @property
    def price(self):
        """Property: The price of one item.

        Parameters
        ---------
        price: string, integer, float
            The input must be a valid input for the Decimal class
            the Python Standard Library.

        """
        return self._price

    @price.setter
    def price(self, price):
        """Sets the price of one item.
        """
        if price is None:
            return
        try:
            self._price = parse_money(price, self._currency)
            if self._quantity is not None:
                self._line_extension_amount = self._price * self._quantity
        except ValueError:
            raise ValueError("Unrecognized price {}".format(price))

    @property
    def line_extension_amount(self):
        """Property: The line extension amount (quantity * price).
        """
        if self._line_extension_amount is not None:
            return self._line_extension_amount
        if self._price is not None and self._quantity is not None:
            self._line_extension_amount = self._price * self._quantity
            return self._line_extension_amount
        return None

    @line_extension_amount.setter
    def line_extension_amount(self, amount):
        """Sets the line extension amount directly.
        """
        if amount is None:
            self._line_extension_amount = None
            return
        try:
            self._line_extension_amount = parse_money(amount, self._currency)
        except ValueError:
            raise ValueError("Unrecognized line extension amount {}".format(amount))

    def is_valid(self):
        """Check if the credit note line is valid.

        Returns
        -------
        bool
            True if the line has at least quantity, price, and tax defined.
        """
        return (self._quantity is not None and 
                self._price is not None and 
                self.tax is not None)

    def has_tax(self, tax):
        """Returns True if the line has this tax.

        Parameters
        ----------
        tax: Tax Object.
            
        """
        if tax is None:
            return True
        return self.tax == tax

    def __repr__(self):
        if not self.is_valid():
            return "{}: empty".format(self.__class__)
        return "{}: {} {} x {} {}".format(self.__class__, self.quantity,
                                          self.item_name, self.price,
                                          self.currency)