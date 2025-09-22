#!/usr/bin/env python3
"""
Demonstration script showing the extended EN16931 functionality.

This script demonstrates all the new features added to make the library
more complete according to the EN16931 EU standard:

1. Credit Notes
2. File Attachments
3. Delivery Information  
4. Line-level Charges and Discounts
5. Additional Invoice attributes (periods, references)
"""
import tempfile
from datetime import datetime

from en16931 import (
    Invoice, InvoiceLine, CreditNote, CreditNoteLine,
    Entity, PostalAddress, Attachment, DocumentReference,
    DeliveryInformation, DeliveryTerms, LineCharge, LineDiscount
)


def create_sample_entity(name, tax_id, country="ES"):
    """Create a sample entity for testing."""
    return Entity(
        name=name,
        tax_scheme="VAT",
        tax_scheme_id=tax_id,
        country=country,
        party_legal_entity_id=tax_id,
        registration_name=name + " Ltd",
        endpoint=tax_id,
        endpoint_scheme=f"{country}:VAT",
        address="Sample Street 123",
        city="Sample City",
        postalzone="12345",
        province="Sample Province"
    )


def demonstrate_credit_note():
    """Demonstrate CreditNote functionality."""
    print("=== CREDIT NOTE DEMONSTRATION ===")
    
    # Create a credit note
    credit_note = CreditNote(credit_note_id="CN-2023-001", currency="EUR")
    credit_note.issue_date = "2023-12-01"
    credit_note.billing_reference = "INV-2023-001"  # Reference to original invoice
    
    # Set parties
    seller = create_sample_entity("Acme Corp", "ES12345678")
    buyer = create_sample_entity("Customer Inc", "ES87654321")
    credit_note.seller_party = seller
    credit_note.buyer_party = buyer
    
    # Add credit note lines
    line1 = CreditNoteLine(
        quantity=2,
        price=50.00,
        item_name="Returned Product A",
        tax_percent=0.21,
        tax_category="S"
    )
    
    line2 = CreditNoteLine(
        quantity=1,
        price=25.00,
        item_name="Defective Product B",
        tax_percent=0.21,
        tax_category="S"
    )
    
    credit_note.add_lines_from([line1, line2])
    
    print(f"Credit Note ID: {credit_note.credit_note_id}")
    print(f"Billing Reference: {credit_note.billing_reference}")
    print(f"Total Lines: {len(credit_note.lines)}")
    print(f"Subtotal: {credit_note.subtotal()}")
    print(f"Tax Amount: {credit_note.tax_amount()}")
    print(f"Total: {credit_note.total()}")
    
    # Generate XML
    xml = credit_note.to_xml()
    print(f"XML Generated: {len(xml)} characters")
    print("✓ Credit Note functionality working")
    print()


def demonstrate_attachments():
    """Demonstrate file attachment functionality."""
    print("=== ATTACHMENT DEMONSTRATION ===")
    
    # Create a temporary file to attach
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a sample document attachment for the invoice.")
        temp_file = f.name
    
    # Create an attachment from file
    attachment = Attachment()
    attachment.load_from_file(temp_file)
    attachment.description = "Supporting documentation"
    attachment.document_type = "Contract"
    
    print(f"Attachment: {attachment.filename}")
    print(f"MIME Type: {attachment.mime_type}")
    print(f"Size: {attachment.size} bytes")
    print(f"Valid: {attachment.is_valid()}")
    print(f"Encoded data length: {len(attachment.encoded_data)} characters")
    
    # Create document reference
    doc_ref = DocumentReference(
        document_id="DOC-2023-001",
        document_type="Contract",
        attachment=attachment
    )
    
    print(f"Document Reference: {doc_ref}")
    print("✓ Attachment functionality working")
    print()
    
    # Cleanup
    import os
    os.unlink(temp_file)


def demonstrate_delivery():
    """Demonstrate delivery information functionality."""
    print("=== DELIVERY INFORMATION DEMONSTRATION ===")
    
    # Create delivery address
    delivery_address = PostalAddress(
        address="Warehouse Street 456",
        city_name="Delivery City",
        postal_zone="54321",
        country="ES",
        province="Delivery Province"
    )
    
    # Create delivery information
    delivery_info = DeliveryInformation(
        actual_delivery_date="2023-12-15",
        location_id="WAREHOUSE_A",
        location_scheme_id="GLN",
        delivery_address=delivery_address
    )
    
    print(f"Delivery Info: {delivery_info}")
    print(f"Delivery Date: {delivery_info.actual_delivery_date}")
    print(f"Location: {delivery_info.location_id}")
    print(f"Valid: {delivery_info.is_valid()}")
    
    # Create delivery terms
    delivery_terms = DeliveryTerms(
        delivery_terms_code="DAP",
        delivery_location="Customer Warehouse"
    )
    
    print(f"Delivery Terms: {delivery_terms}")
    print(f"Incoterms 2020: {len(DeliveryTerms.incoterms_2020())} available")
    print("✓ Delivery functionality working")
    print()


def demonstrate_line_charges_discounts():
    """Demonstrate line-level charges and discounts."""
    print("=== LINE CHARGES & DISCOUNTS DEMONSTRATION ===")
    
    # Create invoice line
    line = InvoiceLine(
        quantity=10,
        price=100.00,
        item_name="Product with charges/discounts",
        tax_percent=0.21,
        tax_category="S"
    )
    
    # Add line charge
    handling_charge = LineCharge(
        amount=10.00,
        reason="Handling fee"
    )
    line.add_line_charge(handling_charge)
    
    # Add line discount
    volume_discount = LineDiscount(
        percentage=5.0,
        reason="Volume discount"
    )
    line.add_line_discount(volume_discount)
    
    print(f"Base line extension: {line.line_extension_amount}")
    print(f"Total charges: {line.total_charges_amount()}")
    print(f"Total discounts: {line.total_discounts_amount()}")
    print(f"Net amount: {line.net_line_extension_amount()}")
    print(f"Line charges: {len(line.line_charges)}")
    print(f"Line discounts: {len(line.line_discounts)}")
    print("✓ Line charges & discounts functionality working")
    print()


def demonstrate_enhanced_invoice():
    """Demonstrate enhanced invoice with all new features."""
    print("=== ENHANCED INVOICE DEMONSTRATION ===")
    
    # Create invoice with new attributes
    invoice = Invoice(invoice_id="INV-2023-ENHANCED", currency="EUR")
    invoice.issue_date = "2023-12-01"
    invoice.due_date = "2023-12-31"
    
    # Set new attributes
    invoice.buyer_reference = "PO-12345"
    invoice.order_reference = "ORDER-2023-001"
    invoice.contract_document_reference = "CONTRACT-2023-A"
    invoice.invoice_period_start = "2023-11-01"
    invoice.invoice_period_end = "2023-11-30"
    invoice.note = "This invoice demonstrates enhanced EN16931 features"
    
    # Set parties
    seller = create_sample_entity("Enhanced Corp", "ES11111111")
    buyer = create_sample_entity("Advanced Client", "ES22222222")
    invoice.seller_party = seller
    invoice.buyer_party = buyer
    
    # Add delivery information
    delivery_address = PostalAddress(
        address="Client Street 789",
        city_name="Client City",
        postal_zone="99999",
        country="ES"
    )
    
    delivery_info = DeliveryInformation(
        actual_delivery_date="2023-12-05",
        delivery_address=delivery_address
    )
    invoice.delivery_information = delivery_info
    
    # Add delivery terms
    delivery_terms = DeliveryTerms(
        delivery_terms_code="FOB",
        delivery_location="Port of Barcelona"
    )
    invoice.delivery_terms = delivery_terms
    
    # Add document reference with attachment
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Contract terms and conditions...")
        temp_file = f.name
    
    attachment = Attachment()
    attachment.load_from_file(temp_file)
    attachment.description = "Contract document"
    
    doc_ref = DocumentReference(
        document_id="CONTRACT-2023-A",
        document_type="Contract",
        attachment=attachment
    )
    invoice.add_document_reference(doc_ref)
    
    # Add enhanced invoice line
    line = InvoiceLine(
        quantity=5,
        price=200.00,
        item_name="Enhanced Product",
        tax_percent=0.21,
        tax_category="S"
    )
    
    # Add line-level charge and discount
    line.add_line_charge(LineCharge(amount=25.00, reason="Special handling"))
    line.add_line_discount(LineDiscount(percentage=10.0, reason="Loyalty discount"))
    
    invoice.add_line(line)
    
    print(f"Invoice ID: {invoice.invoice_id}")
    print(f"Buyer Reference: {invoice.buyer_reference}")
    print(f"Order Reference: {invoice.order_reference}")
    print(f"Contract Reference: {invoice.contract_document_reference}")
    print(f"Invoice Period: {invoice.invoice_period_start} to {invoice.invoice_period_end}")
    print(f"Note: {invoice.note}")
    print(f"Delivery Terms: {invoice.delivery_terms}")
    print(f"Attachments: {len(invoice.attachments)}")
    print(f"Document References: {len(invoice.additional_document_references)}")
    print(f"Total: {invoice.total()}")
    
    # Generate XML
    xml = invoice.to_xml()
    print(f"Enhanced XML Generated: {len(xml)} characters")
    print("✓ Enhanced Invoice functionality working")
    print()
    
    # Cleanup
    import os
    os.unlink(temp_file)


def main():
    """Main demonstration function."""
    print("EN16931 Extended Library Demonstration")
    print("=" * 50)
    print()
    
    try:
        demonstrate_credit_note()
        demonstrate_attachments()
        demonstrate_delivery()
        demonstrate_line_charges_discounts()
        demonstrate_enhanced_invoice()
        
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print()
        print("The EN16931 library now supports:")
        print("✅ Credit Notes with billing references")
        print("✅ File attachments with base64 encoding")
        print("✅ Delivery information and terms")
        print("✅ Line-level charges and discounts")
        print("✅ Enhanced invoice attributes (periods, references)")
        print("✅ Document references and attachments")
        print("✅ Complete XML generation for all features")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()