"""
Class for representing a CreditNote.
"""
from datetime import datetime
import lxml.etree

from jinja2 import Environment, PackageLoader, select_autoescape
from money.currency import Currency

from en16931.entity import Entity
from en16931.money import MyMoney
from en16931.utils import parse_date
from en16931.utils import parse_money
from en16931.xpaths import get_from_xpath
from en16931.xpaths import get_entity
from en16931.xpaths import get_invoice_lines
from en16931.xpaths import get_discount
from en16931.xpaths import get_charge


templates = Environment(
    loader=PackageLoader("en16931"),
    autoescape=select_autoescape()
)


class CreditNote:
    """EN16931 CreditNote class.

    This class represents a Credit Note which follows the same structure
    as an Invoice but with different semantics and document type codes.

    Credit Notes are used to reduce the amount of tax and amount owed by 
    the customer when goods are returned or services are not fully provided.
    """

    def __init__(self, credit_note_id=None, customization_id=None, currency="EUR", from_xml=False):
        """Initialize a CreditNote.

        Parameters
        ----------
        credit_note_id: string (optional, default '1')
            Arbitrary string to identify the credit note.

        customization_id: string (optional, default 'urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0')

        currency: string (optional, default 'EUR')
            An ISO 4217 currency code.

        from_xml: bool (optional, default False)
            A flag to mark if the object is the result of importing
            an XML credit note.

        Raises
        ------
        KeyError: If the currency code is not a valid ISO 4217 code.
        """
        self.credit_note_id = credit_note_id or '1'
        self.currency = currency
        self.ubl_version_id = "2.1"
        self.customization_id = customization_id or "urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0"
        self.profile_id = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
        self.credit_note_type_code = 381  # Standard credit note type code
        self._issue_date = None
        self._due_date = None
        self._seller_party = None
        self._buyer_party = None
        self._templates = templates.get_template('credit_note.xml')
        self._imported_from_xml = from_xml
        self._line_extension_amount = None
        self._tax_exclusive_amount = None
        self._tax_inclusive_amount = None
        self._payable_amount = None
        self._charge_amount = None
        self._charge_percent = None
        self._discount_amount = None
        self._discount_percent = None
        self._original_xml = None
        self._payment_means_code = None
        self._billing_reference = None  # Reference to original invoice
        self.lines = []

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
        """Sets the currency of the CreditNote.
        """
        try:
            self._currency = Currency[currency_str]
        except KeyError:
            raise KeyError('Currency {} not supported'.format(currency_str))

    @property
    def issue_date(self):
        """Property: Issue date of the credit note.
        """
        return self._issue_date

    @issue_date.setter
    def issue_date(self, date):
        """Sets the issue date of the credit note.
        """
        if isinstance(date, str):
            self._issue_date = parse_date(date)
        elif isinstance(date, datetime):
            self._issue_date = date
        elif date is None:
            self._issue_date = None
        else:
            msg = "Expected a string or datetime object, received: {}"
            raise ValueError(msg.format(type(date)))

    @property
    def due_date(self):
        """Property: Due date of the credit note.
        """
        return self._due_date

    @due_date.setter
    def due_date(self, date):
        """Sets the due date of the credit note.
        """
        if isinstance(date, str):
            self._due_date = parse_date(date)
        elif isinstance(date, datetime):
            self._due_date = date
        elif date is None:
            self._due_date = None
        else:
            msg = "Expected a string or datetime object, received: {}"
            raise ValueError(msg.format(type(date)))

    @property
    def seller_party(self):
        """Property: Entity with the role of AccountingSupplierParty.
        """
        return self._seller_party

    @seller_party.setter
    def seller_party(self, party):
        """Set the Entity with the role of AccountingSupplierParty.
        """
        if isinstance(party, Entity):
            if party.is_valid():
                self._seller_party = party
            else:
                raise ValueError("Invalid Entity")
        else:
            msg = "Expected an Entity object but got a {}"
            raise TypeError(msg.format(type(party)))

    @property
    def buyer_party(self):
        """Property: Entity with the role of AccountingCustomerParty.
        """
        return self._buyer_party

    @buyer_party.setter
    def buyer_party(self, party):
        """Set the Entity with the role of AccountingCustomerParty.
        """
        if isinstance(party, Entity):
            if party.is_valid():
                self._buyer_party = party
            else:
                raise ValueError("Invalid Entity")
        else:
            msg = "Expected an Entity object but got a {}"
            raise TypeError(msg.format(type(party)))

    @property
    def billing_reference(self):
        """Property: Reference to the original invoice being credited.
        """
        return self._billing_reference

    @billing_reference.setter
    def billing_reference(self, reference):
        """Set the billing reference to the original invoice.
        """
        self._billing_reference = reference

    def add_line(self, credit_note_line):
        """Add a CreditNoteLine to the credit note.

        Parameters
        ----------
        credit_note_line: CreditNoteLine
            An instance of CreditNoteLine.
        """
        self.lines.append(credit_note_line)

    def add_lines_from(self, lines):
        """Add CreditNoteLines from a list.

        Parameters
        ----------
        lines: list
            A list of CreditNoteLine instances.
        """
        for line in lines:
            self.add_line(line)

    def subtotal(self):
        """Total amount without taxes, charges and discounts.
        """
        total = MyMoney('0', self._currency)
        for line in self.lines:
            if line.line_extension_amount:
                total += line.line_extension_amount
        return total

    def total(self):
        """Total amount including taxes.
        """
        return self.subtotal() + self.tax_amount()

    def tax_amount(self):
        """Total tax amount.
        """
        total = MyMoney('0', self._currency)
        for tax in self.unique_taxes:
            total += self.taxable_base(tax) * tax.percent
        return total

    def taxable_base(self, tax=None):
        """Taxable base for a given tax.
        """
        total = MyMoney('0', self._currency)
        for line in self.lines_with_taxes(tax):
            total += line.line_extension_amount
        return total

    def lines_with_taxes(self, tax=None):
        """Lines that match a given tax.
        """
        return [line for line in self.lines if line.has_tax(tax)]

    @property
    def unique_taxes(self):
        """Unique taxes applied in the credit note.
        """
        return {line.tax for line in self.lines if line.tax is not None}

    def to_xml(self):
        """Serialize the credit note to XML string.
        """
        return self._templates.render(credit_note=self)

    def save(self, filename):
        """Save the credit note to an XML file.
        """
        with open(filename, 'w') as f:
            f.write(self.to_xml())

    @classmethod
    def from_xml(cls, xml_string_or_file):
        """Create a CreditNote from XML.

        Parameters
        ----------
        xml_string_or_file: string
            Path to XML file or XML string.

        Returns
        -------
        CreditNote
            A CreditNote instance.
        """
        # This method would need to be implemented similar to Invoice.from_xml
        # For now, we'll keep it as a placeholder
        raise NotImplementedError("CreditNote.from_xml not yet implemented")