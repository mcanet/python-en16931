"""
Tests for attachment functionality.
"""
import pytest
import tempfile
import os

from en16931.attachment import Attachment, DocumentReference


class TestAttachment:

    def test_initialization(self):
        """Test Attachment initialization."""
        attachment = Attachment()
        assert attachment.filename is None
        assert attachment.mime_type is None
        assert attachment.data is None
        assert attachment.description is None
        assert attachment.encoding == "Base64"

    def test_initialization_with_params(self):
        """Test Attachment initialization with parameters."""
        data = b"Test file content"
        attachment = Attachment(
            filename="test.txt",
            mime_type="text/plain",
            data=data,
            description="Test file"
        )
        
        assert attachment.filename == "test.txt"
        assert attachment.mime_type == "text/plain"
        assert attachment.data == data
        assert attachment.description == "Test file"

    def test_load_from_file(self):
        """Test loading attachment from file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name

        try:
            attachment = Attachment()
            attachment.load_from_file(temp_path)
            
            assert attachment.filename == os.path.basename(temp_path)
            assert attachment.mime_type == "text/plain"
            assert attachment.data == b"Test content"
        finally:
            os.unlink(temp_path)

    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        attachment = Attachment()
        with pytest.raises(FileNotFoundError):
            attachment.load_from_file("/nonexistent/file.txt")

    def test_encoded_data(self):
        """Test base64 encoded data property."""
        data = b"Hello World"
        attachment = Attachment(data=data)
        
        encoded = attachment.encoded_data
        assert encoded is not None
        
        # Verify it's valid base64
        import base64
        decoded = base64.b64decode(encoded)
        assert decoded == data

    def test_encoded_data_no_data(self):
        """Test encoded data when no data is present."""
        attachment = Attachment()
        assert attachment.encoded_data is None

    def test_size(self):
        """Test attachment size property."""
        attachment = Attachment()
        assert attachment.size == 0
        
        data = b"Hello"
        attachment.data = data
        assert attachment.size == len(data)

    def test_is_valid(self):
        """Test attachment validation."""
        attachment = Attachment()
        assert not attachment.is_valid()
        
        attachment.data = b"content"
        assert not attachment.is_valid()  # Missing filename and mime_type
        
        attachment.filename = "test.txt"
        assert not attachment.is_valid()  # Missing mime_type
        
        attachment.mime_type = "text/plain"
        assert attachment.is_valid()

    def test_supported_mime_types(self):
        """Test supported MIME types class method."""
        mime_types = Attachment.supported_mime_types()
        assert isinstance(mime_types, list)
        assert 'application/pdf' in mime_types
        assert 'image/jpeg' in mime_types
        assert 'text/plain' in mime_types

    def test_repr(self):
        """Test string representation."""
        attachment = Attachment()
        assert "empty" in repr(attachment)
        
        attachment = Attachment(
            filename="test.pdf",
            mime_type="application/pdf",
            data=b"pdf content"
        )
        
        repr_str = repr(attachment)
        assert "test.pdf" in repr_str
        assert "application/pdf" in repr_str
        assert "11 bytes" in repr_str


class TestDocumentReference:

    def test_initialization(self):
        """Test DocumentReference initialization."""
        doc_ref = DocumentReference()
        assert doc_ref.document_id is None
        assert doc_ref.document_type is None
        assert doc_ref.attachment is None

    def test_initialization_with_params(self):
        """Test DocumentReference initialization with parameters."""
        attachment = Attachment(
            filename="contract.pdf",
            mime_type="application/pdf",
            data=b"contract content"
        )
        
        doc_ref = DocumentReference(
            document_id="DOC-001",
            document_type="Contract",
            attachment=attachment
        )
        
        assert doc_ref.document_id == "DOC-001"
        assert doc_ref.document_type == "Contract"
        assert doc_ref.attachment == attachment

    def test_is_valid(self):
        """Test document reference validation."""
        doc_ref = DocumentReference()
        assert not doc_ref.is_valid()
        
        # Valid with document ID
        doc_ref.document_id = "DOC-001"
        assert doc_ref.is_valid()
        
        # Valid with attachment
        doc_ref = DocumentReference()
        attachment = Attachment(
            filename="test.pdf",
            mime_type="application/pdf", 
            data=b"content"
        )
        doc_ref.attachment = attachment
        assert doc_ref.is_valid()

    def test_repr(self):
        """Test string representation."""
        doc_ref = DocumentReference(document_id="DOC-001", document_type="Contract")
        repr_str = repr(doc_ref)
        assert "Contract" in repr_str
        assert "DOC-001" in repr_str
        
        attachment = Attachment(filename="test.pdf", mime_type="application/pdf", data=b"content")
        doc_ref = DocumentReference(document_type="Invoice", attachment=attachment)
        repr_str = repr(doc_ref)
        assert "Invoice" in repr_str
        assert "test.pdf" in repr_str