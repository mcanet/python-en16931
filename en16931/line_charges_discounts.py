"""
Classes for representing line-level charges and discounts in EN16931.
"""
from decimal import Decimal, InvalidOperation
from money.currency import Currency
from en16931.utils import parse_money


class LineCharge:
    """EN16931 Line-level Charge class.

    Represents a charge applied to a specific invoice line.
    
    Example usage:

    >>> charge = LineCharge(
    ...     amount=5.00,
    ...     reason="Handling fee",
    ...     currency="EUR"
    ... )
    """

    def __init__(self, amount=None, reason=None, currency="EUR"):
        """Initialize a LineCharge.

        Parameters
        ----------
        amount: float, Decimal, string (optional)
            Charge amount in the specified currency.

        reason: string (optional)
            Reason or description for the charge.

        currency: string (optional, default 'EUR')
            ISO 4217 currency code.
        """
        self._amount = None
        self.reason = reason
        self.currency = currency
        
        if amount is not None:
            self.amount = amount

    @property
    def currency(self):
        """Property: String representation of the ISO 4217 currency code."""
        return self._currency.name

    @currency.setter
    def currency(self, currency_str):
        """Sets the currency of the charge."""
        try:
            self._currency = Currency[currency_str]
        except KeyError:
            raise KeyError('Currency {} not supported'.format(currency_str))

    @property
    def amount(self):
        """Property: The charge amount."""
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the charge amount."""
        if amount is None:
            self._amount = None
            return
        try:
            self._amount = parse_money(amount, self._currency)
        except (ValueError, InvalidOperation):
            raise ValueError("Unrecognized charge amount {}".format(amount))

    def is_valid(self):
        """Check if the charge is valid.

        Returns
        -------
        bool
            True if the charge has an amount.
        """
        return self._amount is not None

    def __repr__(self):
        if self.is_valid():
            reason_part = f" ({self.reason})" if self.reason else ""
            return f"{self.__class__.__name__}: {self.amount}{reason_part}"
        return f"{self.__class__.__name__}: empty"


class LineDiscount:
    """EN16931 Line-level Discount class.

    Represents a discount applied to a specific invoice line.
    Can be specified as a fixed amount or percentage.
    
    Example usage:

    >>> discount = LineDiscount(
    ...     amount=2.50,
    ...     reason="Volume discount",
    ...     currency="EUR"
    ... )
    
    Or as a percentage:

    >>> discount = LineDiscount(
    ...     percentage=10.0,
    ...     reason="Early payment discount"
    ... )
    """

    def __init__(self, amount=None, percentage=None, reason=None, currency="EUR"):
        """Initialize a LineDiscount.

        Parameters
        ----------
        amount: float, Decimal, string (optional)
            Fixed discount amount in the specified currency.

        percentage: float, Decimal, string (optional)
            Discount percentage (e.g., 10.0 for 10%).

        reason: string (optional)
            Reason or description for the discount.

        currency: string (optional, default 'EUR')
            ISO 4217 currency code.
        """
        self._amount = None
        self._percentage = None
        self.reason = reason
        self.currency = currency
        
        if amount is not None:
            self.amount = amount
        if percentage is not None:
            self.percentage = percentage

    @property
    def currency(self):
        """Property: String representation of the ISO 4217 currency code."""
        return self._currency.name

    @currency.setter
    def currency(self, currency_str):
        """Sets the currency of the discount."""
        try:
            self._currency = Currency[currency_str]
        except KeyError:
            raise KeyError('Currency {} not supported'.format(currency_str))

    @property
    def amount(self):
        """Property: The fixed discount amount."""
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the fixed discount amount."""
        if amount is None:
            self._amount = None
            return
        try:
            self._amount = parse_money(amount, self._currency)
        except (ValueError, InvalidOperation):
            raise ValueError("Unrecognized discount amount {}".format(amount))

    @property
    def percentage(self):
        """Property: The discount percentage."""
        return self._percentage

    @percentage.setter
    def percentage(self, percentage):
        """Sets the discount percentage."""
        if percentage is None:
            self._percentage = None
            return
        try:
            self._percentage = Decimal(str(percentage))
        except (ValueError, InvalidOperation):
            raise ValueError("Unrecognized discount percentage {}".format(percentage))

    def calculate_discount_amount(self, base_amount):
        """Calculate the discount amount based on a base amount.

        Parameters
        ----------
        base_amount: Money
            The base amount to calculate percentage discount from.

        Returns
        -------
        Money
            The calculated discount amount.
        """
        if self._amount is not None:
            return self._amount
        elif self._percentage is not None:
            return base_amount * (self._percentage / 100)
        else:
            return parse_money("0", self._currency)

    def is_valid(self):
        """Check if the discount is valid.

        Returns
        -------
        bool
            True if the discount has either an amount or percentage.
        """
        return self._amount is not None or self._percentage is not None

    def __repr__(self):
        if self.is_valid():
            reason_part = f" ({self.reason})" if self.reason else ""
            if self._amount is not None:
                return f"{self.__class__.__name__}: {self.amount}{reason_part}"
            else:
                return f"{self.__class__.__name__}: {self.percentage}%{reason_part}"
        return f"{self.__class__.__name__}: empty"